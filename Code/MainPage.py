from PyQt6.QtWidgets import QWidget
from MapWidget import MapWidget

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 使用绝对定位，MainWindow 中设置 QStackedWidget 占位
        # 在此仅放置 MapWidget (内部绘制“WorldMap”文本替代)
        self.map_widget = MapWidget(self)
        self.map_widget.setGeometry(0, 0, 1000, 600)

    def open_time_window(self):
        """
        由 MainWindow 调用，点击左下角时间按钮时弹出 TimeWindow。
        """
        from TimeWindow import TimeWindow
        time_window = TimeWindow(self)
        time_window.exec()
