from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QTime, QRect, QElapsedTimer
from PyQt6.QtGui import QFont, QPainter, QPen, QColor
from WheelPicker import WheelPicker
from UIDesign import UIDesign

class TimerPopup(QDialog):
    """
    Dialog displayed when the countdown reaches zero, showing the user-defined message.
    """
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Time's Up!")
        self.setFixedSize(200, 100)
        self.setStyleSheet(UIDesign.TIMERPOPUP_STYLE)

        # Display the provided message centered in the popup
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 10, 200, 40)

        # Close button to dismiss the popup
        close_btn = QPushButton("Close", self)
        close_btn.setGeometry(60, 60, 80, 30)
        close_btn.clicked.connect(self.close)

class TimerPage(QWidget):
    """
    Widget that implements a countdown timer with hour, minute, and second selectors,
    a label input, and visual countdown display including an animated arc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set initial geometry and background style
        self.setGeometry(20, 68, 760, 420)
        self.setStyleSheet(UIDesign.TIMERPAGE_BG_STYLE)

        # -------------------- 1. Wheel selectors for hours, minutes, seconds --------------------
        picker_width = 60
        picker_height = 150
        gap = 20
        total_width = 3 * picker_width + 2 * gap
        start_x = 380 - (total_width // 2)
        start_y = 80

        # Hour selector (0-23)
        self.hour_picker = WheelPicker([str(i) for i in range(24)], self, visible_count=5)
        self.hour_picker.setGeometry(start_x, start_y, picker_width, picker_height)

        # Minute selector (00-59)
        self.minute_picker = WheelPicker([f"{i:02d}" for i in range(60)], self, visible_count=5)
        self.minute_picker.setGeometry(start_x + picker_width + gap, start_y, picker_width, picker_height)

        # Second selector (00-59)
        self.second_picker = WheelPicker([f"{i:02d}" for i in range(60)], self, visible_count=5)
        self.second_picker.setGeometry(start_x + 2 * (picker_width + gap), start_y, picker_width, picker_height)

        # -------------------- 2. Label input --------------------
        self.label_edit = QLineEdit(self)
        self.label_edit.setGeometry(270, 250, 220, 35)
        self.label_edit.setStyleSheet(UIDesign.TIMERPAGE_LINEEDIT_STYLE)
        self.label_edit.setPlaceholderText("Enter label...")

        # -------------------- 3. Countdown display (initially hidden) --------------------
        self.time_label = QLabel("00:00:00", self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(UIDesign.TIMERPAGE_TIMELABEL_STYLE)
        font = QFont()
        font.setPointSize(48)
        self.time_label.setFont(font)
        self.time_label.setGeometry(230, 140, 300, 80)
        self.time_label.hide()

        # -------------------- 4. End time display (initially hidden) --------------------
        self.end_time_label = QLabel("", self)
        self.end_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.end_time_label.setStyleSheet(UIDesign.TIMERPAGE_ENDTIMELABEL_STYLE)
        self.end_time_label.setGeometry(320, 100, 120, 30)
        self.end_time_label.hide()

        # -------------------- 5. Control buttons --------------------
        # Cancel button resets the timer
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(80, 340, 120, 40)
        self.cancel_button.setStyleSheet(UIDesign.TIMERPAGE_CANCELBUTTON_STYLE)
        self.cancel_button.clicked.connect(self.cancel_timer)

        # Start/Stop button toggles countdown
        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(560, 340, 120, 40)
        self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)
        self.start_button.clicked.connect(self.toggle_timer)

        # -------------------- 6. Internal timers and state --------------------
        # Updates the countdown text every second
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_countdown)

        # Triggers redraw of the arc animation every 10ms
        self.arc_timer = QTimer(self)
        self.arc_timer.setInterval(10)
        self.arc_timer.timeout.connect(self.update_arc)

        # Measures elapsed time for smooth animation
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_offset = 0           # Accumulated time before pause
        self.paused_elapsed = 0           # Time at pause moment

        # State flags
        self.is_running = False
        self.is_paused = False
        self.total_seconds = 0
        self.remaining_seconds = 0        # Remaining seconds in countdown
        self.end_time = None              # QTime when countdown ends

    def toggle_timer(self):
        """
        Handle Start/Stop button click:
        - On start: calculate total_seconds, hide selectors, show countdown, start timers.
        - On stop/pause: pause or resume timers and update button styles.
        """
        if not self.is_running:
            # Read selection values
            hours   = int(self.hour_picker.get_current_text() or "0")
            minutes = int(self.minute_picker.get_current_text() or "0")
            seconds = int(self.second_picker.get_current_text() or "0")
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            if self.total_seconds == 0:
                return

            # Initialize countdown state
            self.remaining_seconds = self.total_seconds
            self.is_running = True
            self.is_paused = False
            self.elapsed_offset = 0
            self.elapsed_timer.start()
            self.arc_timer.start()

            # Hide selectors and lock label input
            self.hour_picker.hide()
            self.minute_picker.hide()
            self.second_picker.hide()
            self.label_edit.setReadOnly(True)

            # Show countdown and end time
            self.time_label.show()
            self.end_time_label.show()

            # Change Start button to Stop
            self.start_button.setText("Stop")
            self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STOPBUTTON_STYLE)

            # Display the calculated end time
            self.end_time = QTime.currentTime().addSecs(self.total_seconds)
            self.end_time_label.setText(self.end_time.toString("HH:mm"))

            # Begin timers
            self.timer.start()
            self.update()
        else:
            if not self.is_paused:
                # Pause countdown
                self.paused_elapsed = self.elapsed_offset + self.elapsed_timer.elapsed()
                self.is_paused = True
                self.timer.stop()
                self.arc_timer.stop()
                self.start_button.setText("Start")
                self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)
            else:
                # Resume countdown
                self.elapsed_timer.restart()
                self.elapsed_offset = self.paused_elapsed
                self.is_paused = False
                self.timer.start()
                self.arc_timer.start()
                self.start_button.setText("Stop")
                self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STOPBUTTON_STYLE)
            self.update()

    def cancel_timer(self):
        """
        Reset the timer state and UI to initial conditions.
        """
        self.is_running = False
        self.is_paused = False
        self.timer.stop()
        self.arc_timer.stop()
        self.elapsed_offset = 0
        self.remaining_seconds = 0

        # Reset countdown display
        self.time_label.setText("00:00:00")
        self.time_label.hide()
        self.end_time_label.setText("")
        self.end_time_label.hide()

        # Restore Start button and selectors
        self.start_button.setText("Start")
        self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)
        self.hour_picker.show()
        self.minute_picker.show()
        self.second_picker.show()
        self.label_edit.setReadOnly(False)

        self.update()

    def update_countdown(self):
        """
        Called every second to decrement remaining_seconds,
        update the label, and trigger popup on completion.
        """
        if not self.is_running or self.is_paused:
            return
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            # Countdown complete
            self.remaining_seconds = 0
            self.time_label.setText("00:00:00")
            self.timer.stop()
            self.arc_timer.stop()
            self.is_running = False
            self.is_paused = False

            # Reset Start button style
            self.start_button.setText("Start")
            self.start_button.setStyleSheet(UIDesign.TIMERPAGE_STARTBUTTON_STYLE)

            # Show popup with the label message
            msg = f"{self.label_edit.text()} Time's up!"
            popup = TimerPopup(msg, self)
            popup.exec()

            # Reset UI
            self.cancel_timer()
        else:
            # Update countdown display
            self.time_label.setText(self.format_time(self.remaining_seconds))
        self.update()

    def update_arc(self):
        """
        Called frequently to trigger repaint of the animated arc.
        """
        if not self.is_running or self.is_paused:
            return
        self.update()

    def paintEvent(self, event):
        """
        Draw a circular arc representing the fraction of time remaining.
        """
        super().paintEvent(event)
        if not self.is_running:
            return
        # Compute remaining fraction
        total_elapsed_ms = self.elapsed_offset + self.elapsed_timer.elapsed()
        remaining_ms = self.total_seconds * 1000 - total_elapsed_ms
        remaining_ms = max(remaining_ms, 0)
        fraction = remaining_ms / (self.total_seconds * 1000.0)

        # Define arc geometry
        center_x, center_y = 380, 210
        radius = 170
        arc_rect = QRect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        start_angle = 90 * 16
        span_angle = -int(360 * fraction * 16)

        # Draw arc with specified pen
        painter = QPainter(self)
        pen = QPen(QColor("#F57200"), 10)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawArc(arc_rect, start_angle, span_angle)

    def format_time(self, total_sec):
        """
        Convert an integer number of seconds into HH:MM:SS string format.
        """
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
