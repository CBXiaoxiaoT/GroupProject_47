from PyQt6.QtCore import QTimer, QDate, Qt, QLocale
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget, QHBoxLayout, QFrame,
    QScrollArea, QGridLayout, QLabel, QToolButton
)
from TimeLocationUtils import get_today_date
from ToDoPage import ToDoCard
from Expdb_manager import ExpDBManager
from Tddb_manager import DBManager
from UIDesign import UIDesign

# This is the mini expense card in calendar page
class MiniExpenseCard(QWidget):

    def __init__(self, record_data: dict, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.setFixedSize(400, 40)

        self.back_frame = QFrame(self)
        self.back_frame.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.back_frame.setGeometry(0, 0, 400, 40)
        self.time_label = QLabel(self)
        self.time_label.setGeometry(10, 10, 60, 20)
        self.time_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        self.time_label.setText(self.record_data.get("time", "00:00"))

        # PayerOrPayee
        self.payee_label = QLabel(self)
        self.payee_label.setGeometry(80, 10, 140, 20)
        self.payee_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        self.payee_label.setText(self.record_data.get("payee", "Unknown"))

        # Amount
        self.amount_label = QLabel(self)
        self.amount_label.setGeometry(230, 10, 80, 20)
        self.amount_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        amt_str = self.record_data.get("amount", "0")
        self.amount_label.setText(f"{amt_str} £")

class CalendarPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calendar = None
        self.initUI()

    def initUI(self):


        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        calendar_container = QWidget(self)
        calendar_layout = QHBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.addStretch(1)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setFixedSize(800, 250)

        # set language
        self.calendar.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

        self.calendar.setStyleSheet(UIDesign.CALENDAR_STYLE)

        calendar_layout.addWidget(self.calendar)
        calendar_layout.addStretch(1)
        self.main_layout.addWidget(calendar_container)

        # click signel
        self.calendar.clicked.connect(self.on_date_clicked)
        self.highlight_today()

        QTimer.singleShot(0, self.setArrowTexts)

        # Details area
        self.detail_widget = QFrame(self)

        self.detail_widget.setStyleSheet(UIDesign.CALENDAR_DETAIL_STYLE)
        self.detail_layout = QHBoxLayout(self.detail_widget)
        self.detail_layout.setContentsMargins(10, 10, 10, 10)
        self.detail_layout.setSpacing(10)
        self.main_layout.addWidget(self.detail_widget)

        # left area, to show to do card
        self.todo_scroll = QScrollArea(self.detail_widget)
        self.todo_scroll.setStyleSheet(UIDesign.CALENDAR_SCROLL_STYLE)
        self.todo_scroll.setWidgetResizable(True)
        self.todo_container = QWidget()
        self.todo_grid = QGridLayout(self.todo_container)
        self.todo_grid.setContentsMargins(40, 20, 40, 40)
        self.todo_grid.setHorizontalSpacing(50)
        self.todo_grid.setVerticalSpacing(20)
        self.todo_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.todo_scroll.setWidget(self.todo_container)
        self.detail_layout.addWidget(self.todo_scroll)

        # left area：to show expense card
        self.expense_scroll = QScrollArea(self.detail_widget)
        self.expense_scroll.setStyleSheet(UIDesign.CALENDAR_SCROLL_STYLE)
        self.expense_scroll.setWidgetResizable(True)
        self.expense_container = QWidget()
        self.expense_vlayout = QVBoxLayout(self.expense_container)
        self.expense_vlayout.setContentsMargins(10, 10, 10, 10)
        self.expense_vlayout.setSpacing(10)
        self.expense_vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.expense_scroll.setWidget(self.expense_container)
        self.detail_layout.addWidget(self.expense_scroll)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.highlight_today)
        self.refresh_timer.start(60 * 1000)

        # load today's record by default
        today = get_today_date()
        self.load_data_for_date(today)
        self.calendar.setSelectedDate(today)

    def showEvent(self, event):
        super().showEvent(event)
        # every time you click, load the data agin
        if self.calendar:
            self.load_data_for_date(self.calendar.selectedDate())

    def highlight_today(self):
        today = get_today_date()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#F57200"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(18)
        fmt.setFont(font)
        self.calendar.setDateTextFormat(today, fmt)

    def setArrowTexts(self):
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setText("◀")
        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setText("▶")

    def on_date_clicked(self, qdate: QDate):
        self.load_data_for_date(qdate)

    def load_data_for_date(self, qdate: QDate):
        while self.todo_grid.count():
            item = self.todo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.expense_vlayout.count():
            item = self.expense_vlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        date_str = qdate.toString("yyyy-MM-dd")
        # select today's record
        db_todo = DBManager()
        all_tasks = db_todo.fetch_all_tasks()
        tasks_for_date = [t for t in all_tasks if t["date"] == date_str]
        db_todo.close()
        # two column to show to do card
        for idx, task in enumerate(tasks_for_date):
            card = ToDoCard(task, parent=self.todo_container)
            card.delete_btn.hide()
            card.collection_btn.hide()
            row = idx // 2
            col = idx % 2
            self.todo_grid.addWidget(card, row, col)

        # show expense card
        db_exp = ExpDBManager()
        records = db_exp.fetch_pay_data_by_date(date_str)
        db_exp.close()
        # one card in one row
        for rec in records:
            expense_card = MiniExpenseCard(rec, parent=self.expense_container)
            self.expense_vlayout.addWidget(expense_card)
