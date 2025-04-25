import json
import os
from PyQt6.QtCore import Qt, QSize, QTimer, QTime
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QScrollArea, QDialog, QFrame,
    QLineEdit, QSizePolicy, QCheckBox, QVBoxLayout, QHBoxLayout
)
from UIDesign import UIDesign
from WheelPicker import WheelPicker


# ------------------ alarm popup ------------------
class AlarmPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("It's Time!")
        self.setFixedSize(200, 100)
        self.setStyleSheet(UIDesign.ALARMPOPUP_STYLE)
        label = QLabel("It's time！", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 10, 200, 40)
        close_btn = QPushButton("Close", self)
        close_btn.setGeometry(60, 60, 80, 30)
        close_btn.clicked.connect(self.close)

# ------------------ alarm card ------------------
class AlarmItem(QWidget):
    def __init__(self, alarm_data, parent=None, parent_window=None):
        super().__init__(parent)
        self.alarm_data = alarm_data
        self.parent_window = parent_window
        self.is_edit_mode = False

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(220, 120)
        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, 220, 120)
        self.frame.setStyleSheet(UIDesign.ALARMITEM_FRAME_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 5)
        layout.setSpacing(5)

        self.time_label = QLabel(self.alarm_data.get('time', '07:00'))
        self.time_label.setStyleSheet(UIDesign.ALARMITEM_TIME_LABEL_STYLE)
        layout.addWidget(self.time_label, 0, Qt.AlignmentFlag.AlignLeft)

        self.label_label = QLabel(self.alarm_data.get('label', 'Alarm'))
        self.label_label.setStyleSheet(UIDesign.ALARMITEM_LABEL_LABEL_STYLE)
        layout.addWidget(self.label_label, 0, Qt.AlignmentFlag.AlignLeft)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)

        self.enabled_switch = QCheckBox("Open")
        self.enabled_switch.setStyleSheet(UIDesign.ALARMITEM_CHECKBOX_STYLE)
        is_enabled = self.alarm_data.get('enabled', True)
        self.enabled_switch.setChecked(is_enabled)
        self.enabled_switch.toggled.connect(self.on_switch_toggled)
        bottom_layout.addWidget(self.enabled_switch, 0, Qt.AlignmentFlag.AlignLeft)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(UIDesign.ALARMITEM_DELETEBUTTON_STYLE)
        self.delete_button.setVisible(False)
        self.delete_button.clicked.connect(self.delete_self)
        bottom_layout.addWidget(self.delete_button, 0, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(bottom_layout)

    def sizeHint(self):
        return QSize(220, 120)

    def set_edit_mode(self, edit_mode: bool):
        self.is_edit_mode = edit_mode
        self.delete_button.setVisible(edit_mode)

    def mousePressEvent(self, event: QMouseEvent):
        if self.enabled_switch.geometry().contains(event.pos()):
            return super().mousePressEvent(event)
        if self.delete_button.isVisible() and self.delete_button.geometry().contains(event.pos()):
            return super().mousePressEvent(event)
        self.edit_alarm()

    def edit_alarm(self):
        dialog = AlarmEditDialog(self, self.alarm_data)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            new_data = dialog.get_alarm_data()
            self.alarm_data.update(new_data)
            self.update_display()
            if self.parent_window and hasattr(self.parent_window, 'save_alarm_data'):
                self.parent_window.save_alarm_data()

    def update_display(self):
        self.time_label.setText(self.alarm_data.get('time', '07:00'))
        self.label_label.setText(self.alarm_data.get('label', 'Alarm'))
        self.enabled_switch.setChecked(self.alarm_data.get('enabled', True))

    def on_switch_toggled(self, checked):
        self.alarm_data['enabled'] = checked
        if self.parent_window and hasattr(self.parent_window, 'save_alarm_data'):
            self.parent_window.save_alarm_data()

    def delete_self(self):
        parent_layout = self.parent().layout()
        if parent_layout:
            for i in range(parent_layout.count()):
                if parent_layout.itemAt(i).widget() is self:
                    parent_layout.takeAt(i)
                    break
        if self.parent_window and hasattr(self.parent_window, 'alarm_items'):
            if self in self.parent_window.alarm_items:
                self.parent_window.alarm_items.remove(self)
        self.deleteLater()
        if self.parent_window:
            if hasattr(self.parent_window, 'update_alarm_layout'):
                self.parent_window.update_alarm_layout()
            if hasattr(self.parent_window, 'save_alarm_data'):
                self.parent_window.save_alarm_data()
            if hasattr(self.parent_window, 'update_add_alarm_button_state'):
                self.parent_window.update_add_alarm_button_state()

# ------------------ Alarm Edit dialog ------------------
class AlarmEditDialog(QDialog):
    def __init__(self, alarm_item=None, alarm_data=None):
        super().__init__(alarm_item)
        self.setWindowTitle("Edite Alarm")
        self.setFixedSize(400, 300)
        self.setStyleSheet(UIDesign.ALARMEDITDIALOG_STYLE)
        self.alarm_item = alarm_item
        if alarm_data is None:
            self.alarm_data = {
                'time': '07:00',
                'label': 'Alarm',
                'enabled': True
            }
        else:
            self.alarm_data = dict(alarm_data)

        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        hour_values = [f"{i}" for i in range(24)]
        minute_values = [f"{i:02d}" for i in range(60)]
        # wheelPicker to select time
        self.hour_picker = WheelPicker(hour_values, self, visible_count=5)
        self.minute_picker = WheelPicker(minute_values, self, visible_count=5)

        try:
            hh, mm = self.alarm_data['time'].split(":")
            self.hour_picker.scroll_to_index(int(hh), animated=False)
            self.minute_picker.scroll_to_index(int(mm), animated=False)
        except:
            pass

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hour_picker)
        time_layout.addWidget(self.minute_picker)
        layout.addLayout(time_layout)

        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Label:"))
        self.label_edit = QLineEdit(self.alarm_data.get('label', 'Alarm'))
        self.label_edit.setStyleSheet(UIDesign.ALARMEDITDIALOG_LINEEDIT_STYLE)
        label_layout.addWidget(self.label_edit)
        layout.addLayout(label_layout)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Add")
        save_btn.setStyleSheet(UIDesign.ALARMEDITDIALOG_BUTTON_STYLE)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(UIDesign.ALARMEDITDIALOG_BUTTON_STYLE)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_alarm_data(self):
        hour_str = self.hour_picker.get_current_text()
        minute_str = self.minute_picker.get_current_text()
        time_str = f"{hour_str.zfill(2)}:{minute_str.zfill(2)}"
        enabled_value = True
        if self.alarm_item is not None and hasattr(self.alarm_item, "alarm_data"):
            enabled_value = self.alarm_item.alarm_data.get('enabled', True)
        return {
            'time': time_str,
            'label': self.label_edit.text(),
            'enabled': enabled_value
        }

# ------------------ Alarm main widget, use JSON to store  ------------------
class AlarmClockWidget(QWidget):
    MAX_ALARMS = 6  # we can only add 6 alarms
    COLS = 3
    MARGIN = 10
    SPACING = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(UIDesign.ALARMCLOCK_BG_STYLE)
        self.setGeometry(20, 68, 760, 420)

        self.alarm_file = os.path.join(os.path.dirname(__file__), "alarms.json")

        self.edit_button = QPushButton("Edit", self)
        self.edit_button.setGeometry(10, 10, 80, 30)
        self.edit_button.setStyleSheet(UIDesign.ALARMCLOCK_EDIT_BUTTON_STYLE)
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.is_edit_mode = False

        self.alarm_list_area = QScrollArea(self)
        self.alarm_list_area.setGeometry(0, 50, 760, 320)
        self.alarm_list_area.setWidgetResizable(True)

        self.alarm_content = QWidget()
        self.alarm_list_area.setWidget(self.alarm_content)

        self.add_alarm_button = QPushButton("Add Alarm", self)
        self.add_alarm_button.setGeometry(320, 375, 120, 35)
        self.add_alarm_button.setStyleSheet(UIDesign.ALARMCLOCK_ADD_BUTTON_STYLE)
        self.add_alarm_button.clicked.connect(self.add_alarm)

        self.alarm_items = []

        self.load_alarm_data()
        self.update_add_alarm_button_state()

        QTimer.singleShot(0, self.schedule_alarm_check)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_alarm_layout()

    def toggle_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        self.edit_button.setText("Done" if self.is_edit_mode else "Edit")
        for item in self.alarm_items:
            item.set_edit_mode(self.is_edit_mode)
        self.update_add_alarm_button_state()

    def add_alarm(self):
        dialog = AlarmEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.create_alarm_item(dialog.get_alarm_data())

    def create_alarm_item(self, alarm_data):
        item = AlarmItem(alarm_data, parent=self.alarm_content, parent_window=self)
        self.alarm_items.append(item)
        item.show()
        self.update_alarm_layout()
        self.save_alarm_data()
        self.update_add_alarm_button_state()

    def update_alarm_layout(self):
        if not self.alarm_items:
            return
        item_w = self.alarm_items[0].sizeHint().width()
        item_h = self.alarm_items[0].sizeHint().height()
        total_rows = (len(self.alarm_items) + AlarmClockWidget.COLS - 1) // AlarmClockWidget.COLS
        total_width = AlarmClockWidget.MARGIN * 2 + AlarmClockWidget.COLS * item_w + (AlarmClockWidget.COLS - 1) * AlarmClockWidget.SPACING
        total_height = AlarmClockWidget.MARGIN * 2 + total_rows * item_h + (total_rows - 1) * AlarmClockWidget.SPACING
        self.alarm_content.setMinimumSize(total_width, total_height)
        container_width = self.alarm_list_area.viewport().width()
        offset_x = max(0, (container_width - total_width) // 2)
        offset_y = AlarmClockWidget.MARGIN
        for idx, item in enumerate(self.alarm_items):
            row, col = divmod(idx, AlarmClockWidget.COLS)
            x = offset_x + AlarmClockWidget.MARGIN + col * (item_w + AlarmClockWidget.SPACING)
            y = offset_y + row * (item_h + AlarmClockWidget.SPACING)
            item.setGeometry(x, y, item_w, item_h)
        self.alarm_content.update()

    def update_add_alarm_button_state(self):
        if self.is_edit_mode:
            self.add_alarm_button.setEnabled(False)
            return
        if len(self.alarm_items) >= AlarmClockWidget.MAX_ALARMS:
            self.add_alarm_button.setEnabled(False)
        else:
            self.add_alarm_button.setEnabled(True)

    def schedule_alarm_check(self):
        current = QTime.currentTime()
        msec = (60 - current.second()) * 1000 - current.msec()
        QTimer.singleShot(msec, self.alarm_check_callback)

    def alarm_check_callback(self):
        self.check_alarms()
        self.schedule_alarm_check()

    def check_alarms(self):
        now = QTime.currentTime().toString("HH:mm")
        for item in self.alarm_items:
            alarm = item.alarm_data
            if alarm.get("enabled", True):
                if now == alarm["time"] and not alarm.get("triggered", False):
                    self.show_alarm_popup()
                    alarm["triggered"] = True
                elif now != alarm["time"]:
                    alarm["triggered"] = False

    def show_alarm_popup(self):
        popup = AlarmPopup(self)
        popup.exec()

    def save_alarm_data(self):
        alarm_data_list = [item.alarm_data for item in self.alarm_items]
        try:
            with open(self.alarm_file, "w", encoding="utf-8") as f:
                json.dump(alarm_data_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error saving alarms:", e)

    def load_alarm_data(self):
        if not os.path.exists(self.alarm_file):
            return
        try:
            with open(self.alarm_file, "r", encoding="utf-8") as f:
                alarm_data_list = json.load(f)
            for alarm_data in alarm_data_list:
                self.create_alarm_item(alarm_data)
        except Exception as e:
            print("Error loading alarms:", e)
