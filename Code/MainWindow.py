from PyQt6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from UIDesign import UIDesign  # 导入统一样式模块
from MainPage import MainPage
from CalendarPage import CalendarPage
from ToDoPage import Todo_MainWindow
from ExpenditurePage import ExpenditurePage
from TimeLocationUtils import get_current_time, get_city
from TimeWindow import TimeWindow

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 使用统一背景色
        self.setStyleSheet(UIDesign.BG_BLACK)
        self.setFixedSize(1000, 600)
        self.setWindowTitle("Main Page")

        self.is_locked = True

        self.central_widget = QWidget(self)
        self.central_widget.setGeometry(0, 0, 1000, 600)
        self.central_widget.setStyleSheet(UIDesign.BG_BLACK)
        self.setCentralWidget(self.central_widget)

        self.top_bar_height = 50
        self.bottom_bar_height = 30

        self.pages_widget = QStackedWidget(self.central_widget)
        self.pages_widget.setGeometry(0, self.top_bar_height, 1000, 550)
        self.pages_widget.setStyleSheet(UIDesign.BG_BLACK)

        self.main_page = MainPage()
        self.pages_widget.addWidget(self.main_page)  # index 0
        self.calendar_page = CalendarPage()
        self.pages_widget.addWidget(self.calendar_page)  # index 1
        self.todo_page = Todo_MainWindow()
        self.pages_widget.addWidget(self.todo_page)  # index 2
        self.exp_page = ExpenditurePage()
        self.pages_widget.addWidget(self.exp_page)  # index 3

        self.home_button = QPushButton("Home", self.central_widget)
        self.home_button.setGeometry(10, 15, 80, 36)
        self.home_button.setVisible(False)
        self.home_button.clicked.connect(self.show_main_page)
        self.applyButtonStyle(self.home_button)

        self.calendar_button = QPushButton("Calendar", self.central_widget)
        self.calendar_button.setGeometry(125, 15, 230, 36)
        self.calendar_button.clicked.connect(lambda: self.show_function_page(1))
        self.calendar_button.setEnabled(False)
        self.applyButtonStyle(self.calendar_button)

        self.todo_button = QPushButton("To do List", self.central_widget)
        self.todo_button.setGeometry(384, 15, 230, 36)
        self.todo_button.clicked.connect(lambda: self.show_function_page(2))
        self.todo_button.setEnabled(False)
        self.applyButtonStyle(self.todo_button)

        self.exp_button = QPushButton("Expenditure", self.central_widget)
        self.exp_button.setGeometry(644, 15, 230, 36)
        self.exp_button.clicked.connect(lambda: self.show_function_page(3))
        self.exp_button.setEnabled(False)
        self.applyButtonStyle(self.exp_button)

        self.time_label = ClickableLabel("", self.central_widget)
        self.time_label.setEnabled(False)
        self.time_label.setGeometry(36, 440, 203, 130)
        # 由于 time_label 采用 HTML 格式显示，暂保留原有 hover 效果
        self.time_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: white;
            }
            QLabel:hover {
                background-color: #333333;
            }
        """)
        self.time_label.clicked.connect(self.open_time_window)

        self.lock_button = QPushButton("Unlock", self.central_widget)
        self.lock_button.setGeometry(850, 600 - self.bottom_bar_height - 60, 80, 60)
        self.applyButtonStyle(self.lock_button)
        self.lock_button.clicked.connect(self.unlock_application)

        self.location_label = QLabel("Location: None", self.central_widget)
        self.location_label.setGeometry(45, 420, 250, 20)
        loc_font = QFont()
        loc_font.setPointSize(15)
        self.location_label.setFont(loc_font)
        # 统一使用 UIDesign 中的标签样式
        self.location_label.setStyleSheet(UIDesign.LABEL_STYLE)
        self.location_label.setVisible(False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        self.time_window = TimeWindow(self)
        self.time_window.setGeometry(100, 50, 800, 500)
        self.time_window.hide()

    def applyButtonStyle(self, button):
        # 使用 UIDesign 中统一定义的按钮样式
        button.setStyleSheet(UIDesign.BUTTON_STYLE)

    def show_main_page(self):
        self.pages_widget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        if self.is_locked:
            self.lock_button.setVisible(True)
            self.location_label.setVisible(False)
        else:
            self.lock_button.setVisible(False)
            self.location_label.setVisible(True)
        self.time_label.setGeometry(36, 440, 203, 130)
        self.update_time()

    def show_function_page(self, index):
        self.pages_widget.setCurrentIndex(index)
        self.home_button.setVisible(True)
        self.lock_button.setVisible(False)
        self.location_label.setVisible(False)
        # 调整非主页页面中 time_label 的位置
        self.time_label.setGeometry(895, 12, 100, 40)
        self.update_time()

    def update_time(self):
        current_time, current_date = get_current_time()
        if self.pages_widget.currentIndex() == 0:
            text_html = (
                "<html><div style='text-align:center;'>"
                f"<span style='font-size:75px;'>{current_time}</span><br>"
                f"<span style='font-size:24px;'>{current_date}</span>"
                "</div></html>"
            )
        else:
            text_html = (
                "<html><div style='text-align:center;'>"
                f"<span style='font-size:15px;'>{current_time}</span><br>"
                f"<span style='font-size:15px;'>{current_date}</span>"
                "</div></html>"
            )
        self.time_label.setText(text_html)
        self.main_page.map_widget.update_map()

    def unlock_application(self):
        self.is_locked = False
        self.calendar_button.setEnabled(True)
        self.todo_button.setEnabled(True)
        self.exp_button.setEnabled(True)
        self.location_label.setVisible(True)
        self.time_label.setEnabled(True)
        self.lock_button.setVisible(False)
        city = get_city()
        self.location_label.setText(f"Location: {city}")
        self.main_page.map_widget.show_location = True
        self.main_page.map_widget.update_map()

    def open_time_window(self):
        self.time_window.show()
        self.time_window.raise_()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
