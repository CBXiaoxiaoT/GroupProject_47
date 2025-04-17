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
from UIDesign import UIDesign  # 引入统一样式模块

# 修改后的收支卡片，显示时间、PayerOrPayee 和 数量，整行显示
class MiniExpenseCard(QWidget):
    """
    迷你收支卡片，采用绝对定位布局，仅显示时间、PayerOrPayee 和 数量，
    并设置统一背景（如深灰色）及圆角边框，尺寸可根据需要调整。
    """
    def __init__(self, record_data: dict, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.setFixedSize(400, 40)  # 尺寸可根据需求调整
        # 设置背景、圆角以及边框
        self.back_frame = QFrame(self)
        self.back_frame.setStyleSheet("background-color: #4a4a4a; border-radius: 5px")
        self.back_frame.setGeometry(0, 0, 400, 40)
        self.time_label = QLabel(self)
        self.time_label.setGeometry(10, 10, 60, 20)
        self.time_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        self.time_label.setText(self.record_data.get("time", "00:00"))

        # PayerOrPayee标签，绝对定位
        self.payee_label = QLabel(self)
        self.payee_label.setGeometry(80, 10, 140, 20)
        self.payee_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        self.payee_label.setText(self.record_data.get("payee", "Unknown"))

        # 数量标签，绝对定位
        self.amount_label = QLabel(self)
        self.amount_label.setGeometry(230, 10, 80, 20)
        self.amount_label.setStyleSheet("color: white; font-size: 14px; background-color: transparent;")
        amt_str = self.record_data.get("amount", "0")
        self.amount_label.setText(f"{amt_str} £")

class CalendarPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.calendar = None  # 预先声明 calendar 属性
        self.initUI()

    def initUI(self):

        # 整体布局：垂直放置 日历区域 + Detail区域
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # 1. 日历控件放在一个水平容器中，实现居中显示
        calendar_container = QWidget(self)
        calendar_layout = QHBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        calendar_layout.addStretch(1)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setFixedSize(800, 250)  # 缩小日历

        # 设置日历的语言为英语（美国）
        self.calendar.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

        # 使用 UIDesign 中统一定义的日历样式
        self.calendar.setStyleSheet(UIDesign.CALENDAR_STYLE)

        calendar_layout.addWidget(self.calendar)
        calendar_layout.addStretch(1)
        self.main_layout.addWidget(calendar_container)

        # 日历点击信号
        self.calendar.clicked.connect(self.on_date_clicked)
        self.highlight_today()

        QTimer.singleShot(0, self.setArrowTexts)

        # 2. Detail区域：左右布局
        self.detail_widget = QFrame(self)
        # 使用 UIDesign 提取的 detail 区域背景样式
        self.detail_widget.setStyleSheet(UIDesign.CALENDAR_DETAIL_STYLE)
        self.detail_layout = QHBoxLayout(self.detail_widget)
        self.detail_layout.setContentsMargins(10, 10, 10, 10)
        self.detail_layout.setSpacing(10)
        self.main_layout.addWidget(self.detail_widget)

        # 左侧：待办事项，采用 QGridLayout，每行2个
        self.todo_scroll = QScrollArea(self.detail_widget)
        # 使用 UIDesign 提取的滚动区域背景样式
        self.todo_scroll.setStyleSheet(UIDesign.CALENDAR_SCROLL_STYLE)
        self.todo_scroll.setWidgetResizable(True)
        self.todo_container = QWidget()
        self.todo_grid = QGridLayout(self.todo_container)
        self.todo_grid.setContentsMargins(40, 20, 40, 40)
        # 设置水平间距为20像素
        self.todo_grid.setHorizontalSpacing(50)
        # 设置垂直间距为10像素
        self.todo_grid.setVerticalSpacing(20)
        self.todo_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.todo_scroll.setWidget(self.todo_container)
        self.detail_layout.addWidget(self.todo_scroll)

        # 右侧：收支卡片，采用 QVBoxLayout，每行显示一个卡片
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

        # 默认加载今天的数据
        today = get_today_date()
        self.load_data_for_date(today)
        self.calendar.setSelectedDate(today)

    def showEvent(self, event):
        super().showEvent(event)
        # 每次页面显示时刷新 detail 组件，刷新数据以当前选中的日期为准
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
        # 清空待办和收支区域
        while self.todo_grid.count():
            item = self.todo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.expense_vlayout.count():
            item = self.expense_vlayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        date_str = qdate.toString("yyyy-MM-dd")
        # 待办数据：使用 DBManager，筛选当天的任务
        db_todo = DBManager()
        all_tasks = db_todo.fetch_all_tasks()
        tasks_for_date = [t for t in all_tasks if t["date"] == date_str]
        db_todo.close()
        # 按2列显示代办卡片
        for idx, task in enumerate(tasks_for_date):
            card = ToDoCard(task, parent=self.todo_container)
            card.delete_btn.hide()
            card.collection_btn.hide()
            row = idx // 2
            col = idx % 2
            self.todo_grid.addWidget(card, row, col)

        # 收支数据：使用 ExpDBManager
        db_exp = ExpDBManager()
        records = db_exp.fetch_pay_data_by_date(date_str)
        db_exp.close()
        # 每行显示一个收支卡片
        for rec in records:
            expense_card = MiniExpenseCard(rec, parent=self.expense_container)
            self.expense_vlayout.addWidget(expense_card)
