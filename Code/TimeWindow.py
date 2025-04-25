from PyQt6.QtWidgets import QWidget, QFrame, QPushButton
from AlarmPage import AlarmClockWidget
from StopWatchPage import StopwatchPage
from TimerPage import TimerPage
from UIDesign import UIDesign

class TimeWindow(QWidget):
    """
    Main application window for time management features:
    provides navigation between Alarm Clock, Stopwatch, and Timer pages.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set window title and fixed dimensions
        self.setWindowTitle("Time Management")
        self.setFixedSize(800, 500)

        # Main container frame with custom stylesheet
        self.main_frame = QFrame(self)
        self.main_frame.setGeometry(0, 0, 800, 500)
        self.main_frame.setStyleSheet(UIDesign.TIMEWINDOW_MAIN_FRAME_STYLE)

        # Close button: hides the window instead of closing the app
        self.close_button = QPushButton("Close", self)
        self.close_button.setGeometry(27, 15, 40, 40)
        self.close_button.setStyleSheet(UIDesign.TIMEWINDOW_CLOSE_BUTTON_STYLE)
        self.close_button.clicked.connect(self.hide)

        # Navigation buttons for switching between modes
        self.clock_button = QPushButton("Clock", self)
        self.clock_button.setGeometry(183, 16, 130, 35)
        self.stopwatch_button = QPushButton("Stopwatch", self)
        self.stopwatch_button.setGeometry(331, 16, 130, 35)
        self.timer_button = QPushButton("Timer", self)
        self.timer_button.setGeometry(486, 16, 130, 35)

        # Apply uniform styles to navigation buttons
        for btn in (self.clock_button, self.stopwatch_button, self.timer_button):
            btn.setStyleSheet(UIDesign.TIMEWINDOW_BUTTON_STYLE)

        # Initialize clock (alarm) page widget
        self.clock_page = AlarmClockWidget(self)

        # Initialize stopwatch page and hide by default
        self.stopwatch_page = StopwatchPage(self)
        self.stopwatch_page.setGeometry(20, 68, 760, 420)
        self.stopwatch_page.hide()

        # Initialize timer page and hide by default
        self.timer_page = TimerPage(self)
        self.timer_page.setGeometry(20, 68, 760, 420)
        self.timer_page.hide()

        # Connect navigation buttons to display methods
        self.clock_button.clicked.connect(self.show_clock)
        self.stopwatch_button.clicked.connect(self.show_stopwatch)
        self.timer_button.clicked.connect(self.show_timer)

        # Show clock page on startup
        self.show_clock()

    def show_clock(self):
        """Display the clock (alarm) page and hide others."""
        self.clock_page.show()
        self.stopwatch_page.hide()
        self.timer_page.hide()

    def show_stopwatch(self):
        """Display the stopwatch page and hide others."""
        self.clock_page.hide()
        self.stopwatch_page.show()
        self.timer_page.hide()

    def show_timer(self):
        """Display the timer page and hide others."""
        self.clock_page.hide()
        self.stopwatch_page.hide()
        self.timer_page.show()

    def closeEvent(self, event):
        """Override the close event to hide the window rather than exit the application."""
        self.hide()
        event.ignore()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    # Instantiate and run the application
    app = QApplication(sys.argv)
    window = TimeWindow()
    window.show()
    sys.exit(app.exec())
