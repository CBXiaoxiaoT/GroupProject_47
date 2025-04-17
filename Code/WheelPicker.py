from PyQt6.QtWidgets import (QWidget,
    QScrollArea, QVBoxLayout, QLabel,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from UIDesign import UIDesign  # 引入统一样式模块

class WheelPicker(QScrollArea):
    """
    自定义滚轮选择器，使用 QScrollArea + QVBoxLayout + QLabel 实现。
    支持：
      1. 鼠标滚轮一次滚动一个选项，并带动画。
      2. 拖拽停止后自动对齐到最近选项，也带动画。
    """
    def __init__(self, values, parent=None, visible_count=5):
        super().__init__(parent)
        self.values = values
        self.visible_count = visible_count

        # 当前选中索引（默认选中中间）
        self.current_index = 0

        # 隐藏滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 使用 UIDesign 中统一定义的 WheelPicker 样式
        self.setStyleSheet(UIDesign.WHEELPICKER_STYLE)

        # 内部容器和布局
        self.container = QWidget(self)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 创建并添加所有选项标签
        self.labels = []
        for val in values:
            label = QLabel(val, self.container)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.labels.append(label)
            self.layout.addWidget(label)

        self.setWidget(self.container)
        self.setWidgetResizable(True)

        # 单行高度及总高度
        self.item_height = 30  # 单行高度（可根据需要调整）
        total_height = self.item_height * visible_count
        self.setFixedHeight(total_height)

        # 在顶部和底部添加空白边距
        top_and_bottom_margin = self.item_height * (visible_count // 2)
        self.layout.setContentsMargins(0, top_and_bottom_margin, 0, top_and_bottom_margin)
        self.container.setMinimumHeight(
            self.item_height * len(self.labels) + top_and_bottom_margin * 2
        )

        # 延时滚动到默认索引
        QTimer.singleShot(50, lambda: self.scroll_to_index(self.current_index, animated=False))

        # 定时器：拖动停止 200ms 后自动对齐
        self._scroll_timer = QTimer()
        self._scroll_timer.setInterval(200)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(self.snap_to_nearest)

        # 滚动条变化时，重置定时器并更新样式
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # 存放动画对象，避免被垃圾回收
        self._animation = None

        # 首次更新标签样式
        self.update_label_styles()

    def wheelEvent(self, event):
        """
        重写鼠标滚轮事件：
        - 每滚动一格 (±120) 移动索引 ±1
        - 使用动画平滑滚动到新选项
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
        """滚动条变化时启动定时器，200ms 后若无继续滚动则自动对齐"""
        self._scroll_timer.start(200)
        self.update_label_styles()

    def snap_to_nearest(self):
        """拖动停止后自动对齐到最近的选项，并带动画"""
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
        滚动到指定索引，使其位于滚轮视图的正中。
        如果 animated=True，则使用 QPropertyAnimation 实现平滑动画。
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
        根据与中心距离动态调整标签的字体大小和颜色：
        - 中心项字体较大，颜色较亮（纯白）。
        - 离中心越远字体越小，颜色越灰。
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
            # 使用 UIDesign 中定义的基础标签背景样式
            label.setStyleSheet(f"{UIDesign.WHEELPICKER_LABEL_BASE} color: rgb({color_val}, {color_val}, {color_val});")

    def get_current_text(self):
        """返回当前选中的文本"""
        if 0 <= self.current_index < len(self.labels):
            return self.labels[self.current_index].text()
        return ""
