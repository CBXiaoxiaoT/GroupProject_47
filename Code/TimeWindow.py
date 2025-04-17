from PyQt6.QtWidgets import QWidget, QFrame, QPushButton
from AlarmPage import AlarmClockWidget
from StopWatchPage import StopwatchPage
from TimerPage import TimerPage
from UIDesign import UIDesign  # 引入统一样式模块

class TimeWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Time Management")
        self.setFixedSize(800, 500)

        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 800, 500)
        self.main_frame.setStyleSheet(UIDesign.TIMEWINDOW_MAIN_FRAME_STYLE)

        self.close_button = QPushButton("Close", self)
        self.close_button.setGeometry(27, 15, 40, 40)
        self.close_button.setStyleSheet(UIDesign.TIMEWINDOW_CLOSE_BUTTON_STYLE)
        # 关闭按钮仅隐藏窗口
        self.close_button.clicked.connect(self.hide)

        self.clock_button = QPushButton("Clock", self)
        self.clock_button.setGeometry(183, 16, 130, 35)
        self.stopwatch_button = QPushButton("Stopwatch", self)
        self.stopwatch_button.setGeometry(331, 16, 130, 35)
        self.timer_button = QPushButton("Timer", self)
        self.timer_button.setGeometry(486, 16, 130, 35)

        self.clock_button.setStyleSheet(UIDesign.TIMEWINDOW_BUTTON_STYLE)
        self.stopwatch_button.setStyleSheet(UIDesign.TIMEWINDOW_BUTTON_STYLE)
        self.timer_button.setStyleSheet(UIDesign.TIMEWINDOW_BUTTON_STYLE)

        # 使用单一的 AlarmClockWidget 实例
        self.clock_page = AlarmClockWidget(self)

        self.stopwatch_page = StopwatchPage(self)
        self.stopwatch_page.setGeometry(20, 68, 760, 420)
        self.stopwatch_page.hide()

        self.timer_page = TimerPage(self)
        self.timer_page.setGeometry(20, 68, 760, 420)
        self.timer_page.hide()

        self.clock_button.clicked.connect(self.show_clock)
        self.stopwatch_button.clicked.connect(self.show_stopwatch)
        self.timer_button.clicked.connect(self.show_timer)

        self.show_clock()

    def show_clock(self):
        self.clock_page.show()
        self.stopwatch_page.hide()
        self.timer_page.hide()

    def show_stopwatch(self):
        self.clock_page.hide()
        self.stopwatch_page.show()
        self.timer_page.hide()

    def show_timer(self):
        self.clock_page.hide()
        self.stopwatch_page.hide()
        self.timer_page.show()

    def closeEvent(self, event):
        # 当用户点击窗口关闭时，仅隐藏窗口
        self.hide()
        event.ignore()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = TimeWindow()
    window.show()
    sys.exit(app.exec())
