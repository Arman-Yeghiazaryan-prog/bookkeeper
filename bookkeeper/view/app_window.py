"""Модуль виджета окна приложения"""
from PySide6 import QtWidgets
from bookkeeper.view.budget import BudgetWidget
from bookkeeper.view.recent_expenses import RecentExpensesWidget
from bookkeeper.view.add_expenses import AddExpensesWidget


class MainWindow(QtWidgets.QWidget):
    """
    Класс виджета окна приложения
    """
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Бухгалтерская книжка")
        self.setFixedSize(600, 550)

        layout = QtWidgets.QGridLayout(self)
        self.setLayout(layout)

        main_tab = QtWidgets.QTabWidget(self)

        first_page = QtWidgets.QWidget(self)
        first_layout = QtWidgets.QFormLayout()
        first_page.setLayout(first_layout)

        second_page = QtWidgets.QWidget(self)
        second_layout = QtWidgets.QFormLayout()
        second_page.setLayout(second_layout)

        self.expenses_widget = RecentExpensesWidget()
        self.budget = BudgetWidget()
        self.add_expenses_widget = AddExpensesWidget()

        first_layout.addWidget(self.expenses_widget)
        first_layout.addWidget(self.add_expenses_widget)
        second_layout.addWidget(self.budget)

        main_tab.addTab(first_page, 'Последние расходы')
        main_tab.addTab(second_page, 'Бюджет')

        layout.addWidget(main_tab, 0, 0)
