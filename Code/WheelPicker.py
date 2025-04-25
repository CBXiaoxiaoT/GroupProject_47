from PyQt6.QtWidgets import (QWidget,
    QScrollArea, QVBoxLayout, QLabel,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from UIDesign import UIDesign

class WheelPicker(QScrollArea):
    """
    use QScrollArea + QVBoxLayout + QLabel to implement。
    """
    def __init__(self, values, parent=None, visible_count=5):
        super().__init__(parent)
        self.values = values
        self.visible_count = visible_count

        self.current_index = 0

        # hide the scroll bar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setStyleSheet(UIDesign.WHEELPICKER_STYLE)

        # container and layout
        self.container = QWidget(self)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # init labels
        self.labels = []
        for val in values:
            label = QLabel(val, self.container)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.labels.append(label)
            self.layout.addWidget(label)

        self.setWidget(self.container)
        self.setWidgetResizable(True)

        # single row height
        self.item_height = 30
        total_height = self.item_height * visible_count
        self.setFixedHeight(total_height)

        # blank margins at top and bottom to center items
        top_and_bottom_margin = self.item_height * (visible_count // 2)
        self.layout.setContentsMargins(0, top_and_bottom_margin, 0, top_and_bottom_margin)
        self.container.setMinimumHeight(
            self.item_height * len(self.labels) + top_and_bottom_margin * 2
        )

        # # Delayed scroll to the default index without animation
        QTimer.singleShot(50, lambda: self.scroll_to_index(self.current_index, animated=False))

        # Timer auto-align 200ms after dragging stops
        self._scroll_timer = QTimer()
        self._scroll_timer.setInterval(200)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self.snap_to_nearest)

        # restart timer and update label after scroll bar changed
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # store animation object
        self._animation = None

        # Initial label style
        self.update_label_styles()

    def wheelEvent(self, event):
        """
        Override mouse wheel event:
        - Each wheel notch (±120) moves one index.
        - Use animation for smooth scrolling.
        """
        delta = event.angleDelta().y()
        steps = delta // 120  # 一般鼠标一格是 ±120
        if steps != 0:
            new_index = self.current_index - steps
            new_index = max(0, min(len(self.labels) - 1, new_index))
            self.scroll_to_index(new_index, animated=True)
            event.accept()
        else:
            super().wheelEvent(event)

    def on_scroll(self):
        """
        Called when scrollbar value changes:
        - Restart the snap timer.
        - Update label styles dynamically.
        """
        self._scroll_timer.start(200)
        self.update_label_styles()

    def snap_to_nearest(self):
        """
        Snap to the nearest option after dragging stops, with animation.
        """
        scroll_pos = self.verticalScrollBar().value()
        center_pos = scroll_pos + self.height() // 2

        best_index = 0
        min_dist = float('inf')
        for i, label in enumerate(self.labels):
            label_top = label.y()
            label_bottom = label.y() + label.height()
            label_center = (label_top + label_bottom) // 2
            dist = abs(label_center - center_pos)
            if dist < min_dist:
                min_dist = dist
                best_index = i

        self.scroll_to_index(best_index, animated=True)

    def scroll_to_index(self, index, animated=True):
        """
        Scroll to the specified index, centering it in the view.
        If animated=True, use QPropertyAnimation for smooth transition.
        """
        if index < 0 or index >= len(self.labels):
            return

        self.current_index = index
        label = self.labels[index]
        label_center = label.y() + label.height() // 2
        target_scroll = label_center - self.height() // 2

        if not animated:
            self.verticalScrollBar().setValue(target_scroll)
            return

        start_val = self.verticalScrollBar().value()

        if self._animation and self._animation.state() != 0:
            self._animation.stop()

        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setDuration(200)
        self._animation.setStartValue(start_val)
        self._animation.setEndValue(target_scroll)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._animation.start()

    def update_label_styles(self):
        """
        Dynamically adjust each label's font size and color based on distance
        from the center: closer items are larger and brighter.
        """
        scroll_pos = self.verticalScrollBar().value()
        center_pos = scroll_pos + self.height() // 2

        for label in self.labels:
            label_center = label.y() + label.height() // 2
            dist = abs(label_center - center_pos)

            max_font_size = 18
            min_font_size = 12
            max_color = 255
            min_color = 120

            ratio = min(dist / 80, 1.0)
            font_size = int(max_font_size - (max_font_size - min_font_size) * ratio)
            color_val = int(max_color - (max_color - min_color) * ratio)

            font = QFont("微软雅黑", font_size)
            label.setFont(font)
            label.setStyleSheet(f"{UIDesign.WHEELPICKER_LABEL_BASE} color: rgb({color_val}, {color_val}, {color_val});")

    def get_current_text(self):
        """return current text"""
        if 0 <= self.current_index < len(self.labels):
            return self.labels[self.current_index].text()
        return ""
