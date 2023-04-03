"""Модель бюджета"""

from dataclasses import dataclass


@dataclass(slots=True)
class Budget:
    """
    Хранит ограничения бюджета и сумму последних расходов за день, неделю и месяц.
    """
    day: float = 0
    week: float = 0
    month: float = 0
    pk: int = 0
