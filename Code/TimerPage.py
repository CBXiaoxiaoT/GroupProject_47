from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QTime, QRect, QElapsedTimer
from PyQt6.QtGui import QFont, QPainter, QPen, QColor
from WheelPicker import WheelPicker
from UIDesign import UIDesign  # 引入统一样式模块

class TimerPopup(QDialog):
    """计时器提醒弹窗，显示标签内容和“时间到了”"""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("It's time!")
        self.setFixedSize(200, 100)
        self.setStyleSheet(UIDesign.TIMERPOPUP_STYLE)
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 10, 200, 40)
        close_btn = QPushButton("Close", self)
        close_btn.setGeometry(60, 60, 80, 30)
        close_btn.clicked.connect(self.close)

class TimerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 固定窗体大小：760×420（示例）
        self.setGeometry(20, 68, 760, 420)
        self.setStyleSheet(UIDesign.TIMERPAGE_BG_STYLE)

        # ============= 1. 轮盘：时 / 分 / 秒（绝对居中） =============
        picker_width = 60
        picker_height = 150
        gap = 20
        total_width = 3 * picker_width + 2 * gap  # 220
        start_x = 380 - (total_width // 2)           # 270
        start_y = 80                                 # 固定上边距

        self.hour_picker = WheelPicker([str(i) for i in range(24)], self, visible_count=5)
        self.hour_picker.setGeometry(start_x, start_y, picker_width, picker_height)

        self.minute_picker = WheelPicker([f"{i:02d}" for i in range(60)], self, visible_count=5)
        self.minute_picker.setGeometry(start_x + picker_width + gap, start_y, picker_width, picker_height)

        self.second_picker = WheelPicker([f"{i:02d}" for i in range(60)], self, visible_count=5)
        self.second_picker.setGeometry(start_x + 2 * (picker_width + gap), start_y, picker_width, picker_height)

        # ============= 2. 标签输入框（绝对定位，放在靠下位置） =============
        self.label_edit = QLineEdit(self)
        self.label_edit.setGeometry(270, 250, 220, 35)
        self.label_edit.setStyleSheet(UIDesign.TIMERPAGE_LINEEDIT_STYLE)
        self.label_edit.setPlaceholderText("label...")

        # ============= 3. 剩余时间显示（初始隐藏） =============
        self.time_label = QLabel("00:00:00", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(UIDesign.TIMERPAGE_TIMELABEL_STYLE)
        font = QFont()
        font.setPointSize(48)
        self.time_label.setFont(font)
        self.time_label.setGeometry(230, 140, 300, 80)
        self.time_label.hide()

        # ============= 4. 结束时间显示（初始隐藏） =============
        self.end_time_label = QLabel("", self)
        self.end_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.end_time_label.setStyleSheet(UIDesign.TIMERPAGE_ENDTIMELABEL_STYLE)
        self.end_time_label.setGeometry(320, 100, 120, 30)
        self.end_time_label.hide()

        # ============= 5. 左右按钮：取消 / 开始(暂停) =============
        self.cancel_button = QPushButton("cancel", self)
        self.cancel_button.setGeometry(80, 340, 120, 40)
        self.cancel_button.setStyleSheet(UIDesign.TIMERPAGE_CANCELBUTTON_STYLE)
        self.cancel_button.clicked.connect(self.cancel_timer)

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(560, 340, 120, 40)
        self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)
        self.start_button.clicked.connect(self.toggle_timer)

        # ============= 6. 定时器状态与平滑动画的定时器 =============
        self.timer = QTimer(self)           # 每秒更新倒计时文本
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)

        self.arc_timer = QTimer(self)        # 平滑更新圆环动画
        self.arc_timer.setInterval(10)
        self.arc_timer.timeout.connect(self.update_arc)

        self.elapsed_timer = QElapsedTimer()  # 计时用
        self.elapsed_offset = 0               # 暂停前累计毫秒数
        self.paused_elapsed = 0               # 暂停时保存累计毫秒数

        self.is_running = False
        self.is_paused = False
        self.total_seconds = 0
        self.remaining_seconds = 0  # 以秒为单位（可为浮点数，用于平滑显示）
        self.end_time = None

    def toggle_timer(self):
        """点击‘开始’/‘暂停’按钮时的响应"""
        if not self.is_running:
            hours = int(self.hour_picker.get_current_text() or "0")
            minutes = int(self.minute_picker.get_current_text() or "0")
            seconds = int(self.second_picker.get_current_text() or "0")
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            if self.total_seconds == 0:
                return

            self.remaining_seconds = self.total_seconds
            self.is_running = True
            self.is_paused = False
            self.elapsed_offset = 0
            self.elapsed_timer.start()
            self.arc_timer.start()

            self.hour_picker.hide()
            self.minute_picker.hide()
            self.second_picker.hide()
            self.label_edit.setReadOnly(True)

            self.time_label.show()
            self.end_time_label.show()

            self.start_button.setText("Stop")
            self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STOPBUTTON_STYLE)

            self.end_time = QTime.currentTime().addSecs(self.total_seconds)
            self.end_time_label.setText(self.end_time.toString("HH:mm"))

            self.timer.start()
            self.update()
        else:
            if not self.is_paused:
                self.paused_elapsed = self.elapsed_offset + self.elapsed_timer.elapsed()
                self.is_paused = True
                self.timer.stop()
                self.arc_timer.stop()
                self.start_button.setText("Start")
                self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)
            else:
                self.elapsed_timer.restart()
                self.elapsed_offset = self.paused_elapsed
                self.is_paused = False
                self.timer.start()
                self.arc_timer.start()
                self.start_button.setText("Stop")
                self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STOPBUTTON_STYLE)
            self.update()

    def cancel_timer(self):
        """取消计时并重置界面"""
        self.is_running = False
        self.is_paused = False
        self.timer.stop()
        self.arc_timer.stop()
        self.elapsed_offset = 0
        self.remaining_seconds = 0

        self.time_label.setText("00:00:00")
        self.time_label.hide()
        self.end_time_label.setText("")
        self.end_time_label.hide()

        self.start_button.setText("Start")
        self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)

        self.hour_picker.show()
        self.minute_picker.show()
        self.second_picker.show()
        self.label_edit.setReadOnly(False)

        self.update()

    def update_countdown(self):
        """每秒更新倒计时显示，时间到则弹窗提醒"""
        if not self.is_running or self.is_paused:
            return
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.time_label.setText("00:00:00")
            self.timer.stop()
            self.arc_timer.stop()
            self.is_running = False
            self.is_paused = False

            self.start_button.setText("Start")
            self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)

            msg = f"{self.label_edit.text()} It's time!"
            popup = TimerPopup(msg, self)
            popup.exec()

            self.cancel_timer()
        else:
            self.time_label.setText(self.format_time(self.remaining_seconds))
        self.update()

    def update_arc(self):
        """每10ms更新一次圆环动画，实现平滑效果"""
        if not self.is_running or self.is_paused:
            return
        total_elapsed_ms = self.elapsed_offset + self.elapsed_timer.elapsed()
        remaining_ms = self.total_seconds * 1000 - total_elapsed_ms
        if remaining_ms < 0:
            remaining_ms = 0
        self.update()

    def paintEvent(self, event):
        """在界面上绘制圆环"""
        super().paintEvent(event)
        if not self.is_running:
            return
        total_elapsed_ms = self.elapsed_offset + self.elapsed_timer.elapsed()
        remaining_ms = self.total_seconds * 1000 - total_elapsed_ms
        if remaining_ms < 0:
            remaining_ms = 0
        fraction = remaining_ms / (self.total_seconds * 1000.0)
        center_x = 380
        center_y = 210
        radius = 170
        arc_rect = QRect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        start_angle = 90 * 16
        span_angle = -int(360 * fraction * 16)
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(10)
        pen.setColor(QColor("#F57200"))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawArc(arc_rect, start_angle, span_angle)

    def format_time(self, total_sec):
        """将秒数格式化为 HH:MM:SS 格式"""
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
