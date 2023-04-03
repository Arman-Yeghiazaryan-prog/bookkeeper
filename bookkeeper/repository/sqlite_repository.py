"""Модуль описывает репозиторий в БД SQLite3"""

import sqlite3
from inspect import get_annotations
from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Реализация хранения данных в SQLite3
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.cls = cls
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute('SELECT name FROM sqlite_master')
            db_tables = [t[0].lower() for t in res.fetchall()]
            if self.table_name not in db_tables:
                col_names = ', '.join(self.fields.keys())
                query = f'CREATE TABLE {self.table_name} (' \
                    f'"pk" INTEGER PRIMARY KEY AUTOINCREMENT, {col_names})'
                cur.execute(query)
        con.close()

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'Try tp add {obj} with filled pk attribute')

        names = ', '.join(self.fields.keys())
        placeholders = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            query = f'INSERT INTO {self.table_name} ({names}) VALUES ({placeholders})'
            cur.execute(query, values)
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def __generate_object(self, db_row: tuple) -> T:
        obj = self.cls(self.fields)
        for field, value in zip(self.fields, db_row[1:]):
            setattr(obj, field, value)
        obj.pk = db_row[0]
        return obj

    def get(self, pk: int) -> T | None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            query = f'SELECT * FROM {self.table_name} WHERE pk = {pk}'
            row = cur.execute(query).fetchone()
        con.close()

        if row is None:
            return None

        return self.__generate_object(row)

    def update(self, obj: T) -> None:
        if getattr(obj, 'pk', None) is None:
            raise ValueError('Try to update object without pk attribute')

        values = [getattr(obj, x) for x in self.fields]
        values.append(obj.pk)
        fields = ", ".join([f"{field}=?" for field in self.fields.keys()])

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'UPDATE {self.table_name} SET {fields} WHERE pk = ?', values)
            if cur.rowcount == 0:
                raise ValueError('attempt to update object with unknown primary key')
        con.close()

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE pk = {pk}')
            if cur.rowcount == 0:
                raise ValueError('attempt to delete object with unknown primary key')
        con.close()

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()

            if where is not None:
                update_query = " AND ".join([f"{field} = ?" for field in where.keys()])
                rows = cur.execute(f'SELECT * FROM {self.table_name} '
                                   f'WHERE {update_query}',
                                   list(where.values())).fetchall()
            else:
                rows = cur.execute(f'SELECT * FROM {self.table_name}').fetchall()
        con.close()

        if not rows:
            return None

        return [self.__generate_object(row) for row in rows]
