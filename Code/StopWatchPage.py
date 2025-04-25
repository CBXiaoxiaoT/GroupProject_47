from PyQt6.QtCore import QTimer, Qt, QTime, QRect
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QListWidget, QListWidgetItem
)

from UIDesign import UIDesign


class StopwatchPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(UIDesign.STOPWATCH_BG_STYLE)

        # ============= The big time =============
        self.time_label = QLabel("00:00.00", self)
        self.time_label.setGeometry(QRect(179, 26, 400, 80))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(50)
        self.time_label.setFont(font)
        self.time_label.setStyleSheet(UIDesign.STOPWATCH_TIME_LABEL_STYLE)

        # ============= 2. index  lap   total =============
        self.label_lap_index = QLabel("Index", self)
        self.label_lap_index.setGeometry(QRect(168, 120, 150, 40))
        self.label_lap_index.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_lap_index.setStyleSheet(UIDesign.STOPWATCH_LAP_LABEL_STYLE)

        self.label_lap_duration = QLabel("Lap", self)
        self.label_lap_duration.setGeometry(QRect(302, 120, 150, 40))
        self.label_lap_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_lap_duration.setStyleSheet(UIDesign.STOPWATCH_LAP_LABEL_STYLE)

        self.label_lap_total = QLabel("Total", self)
        self.label_lap_total.setGeometry(QRect(445, 120, 150, 40))
        self.label_lap_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_lap_total.setStyleSheet(UIDesign.STOPWATCH_LAP_LABEL_STYLE)

        # ============= 3. the lapping lists =============
        self.lap_list = QListWidget(self)
        self.lap_list.setGeometry(QRect(165, 170, 400, 200))
        self.lap_list.setStyleSheet(UIDesign.STOPWATCH_LAP_LIST_STYLE)
        # set scroll bar invisible
        self.lap_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ============= 4. buttons in bottom: restart and start =============
        self.left_button = QPushButton("reset", self)
        self.left_button.setGeometry(QRect(73, 375, 150, 30))
        self.left_button.setStyleSheet(UIDesign.STOPWATCH_LEFT_BUTTON_STYLE)
        self.left_button.clicked.connect(self.on_left_button_clicked)

        self.right_button = QPushButton("Start", self)
        self.right_button.setGeometry(QRect(537, 375, 150, 30))
        self.right_button.setStyleSheet(UIDesign.STOPWATCH_RIGHT_BUTTON_START_STYLE)
        self.right_button.clicked.connect(self.on_right_button_clicked)


        self.is_running = False
        self.start_time = None
        self.base_elapsed = 0
        self.laps = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.setInterval(10)  #  refresh every 10ms

        self.reset_stopwatch()

    def on_right_button_clicked(self):
        # show lap / stop when running
        if not self.is_running:
            self.is_running = True
            self.right_button.setText("Stop")
            self.right_button.setStyleSheet(UIDesign.STOPWATCH_RIGHT_BUTTON_STOP_STYLE)
            self.left_button.setText("Lap")
            self.start_time = QTime.currentTime()
            self.timer.start()
        # normal condition
        else:
            elapsed_now = self.get_current_elapsed_ms()
            self.base_elapsed = elapsed_now
            self.timer.stop()
            self.is_running = False
            self.right_button.setText("Start")
            self.right_button.setStyleSheet(UIDesign.STOPWATCH_RIGHT_BUTTON_START_STYLE)
            self.left_button.setText("Reset")
            self.update_display()

    def on_left_button_clicked(self):
        """lap/ restart"""
        if self.is_running:
            elapsed_now = self.get_current_elapsed_ms()
            if self.laps:
                last_total = self.laps[-1][1]
                lap_duration = elapsed_now - last_total
            else:
                lap_duration = elapsed_now
            self.laps.append((lap_duration, elapsed_now))
            self.update_lap_list()
        else:
            self.reset_stopwatch()

    def reset_stopwatch(self):
        self.is_running = False
        self.base_elapsed = 0
        self.laps.clear()
        self.timer.stop()
        self.time_label.setText("00:00.00")
        self.lap_list.clear()
        self.right_button.setText("Start")
        self.right_button.setStyleSheet(UIDesign.STOPWATCH_RIGHT_BUTTON_START_STYLE)
        self.left_button.setText("Reset")

    def get_current_elapsed_ms(self):
        if not self.is_running or self.start_time is None:
            return self.base_elapsed
        delta = self.start_time.msecsTo(QTime.currentTime())
        return self.base_elapsed + delta

    def update_display(self):
        ms = self.get_current_elapsed_ms()
        self.time_label.setText(self.format_time(ms))

    def format_time(self, ms):
        total_seconds = ms // 1000
        mm = total_seconds // 60
        ss = total_seconds % 60
        xx = (ms % 1000) // 10
        return f"{mm:02d}:{ss:02d}.{xx:02d}"

    def update_lap_list(self):
        self.lap_list.clear()
        if not self.laps:
            return

        durations = [lap[0] for lap in self.laps]
        min_lap = min(durations)
        max_lap = max(durations)

        for i, (lap_duration, total_msec) in enumerate(self.laps):
            lap_str = self.format_time(lap_duration)
            total_str = self.format_time(total_msec)
            lap_index = i + 1
            text = f"lap {lap_index}           {lap_str}           {total_str}"
            item = QListWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            if lap_duration == min_lap:
                item.setForeground(QColor("green"))
            elif lap_duration == max_lap:
                item.setForeground(QColor("red"))
            self.lap_list.insertItem(0, item)
