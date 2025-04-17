#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from PyQt6.QtCore import Qt, QDate, QEvent, pyqtSignal, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel, QStackedWidget,
    QScrollArea, QGridLayout, QFrame, QDialog, QLineEdit, QTextEdit,
    QRadioButton, QButtonGroup, QDateEdit, QHBoxLayout, QVBoxLayout
)
from Tddb_manager import DBManager
from UIDesign import UIDesign  # 引入统一样式模块


##############################################################################
# 辅助函数：生成英文日期标签，如 "Mar 25   Tuesday   Today"
##############################################################################
def english_date_label(date: QDate, today: QDate) -> str:
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_names   = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    month_str = month_names[date.month() - 1]
    day_str   = str(date.day())
    weekday_index = date.dayOfWeek()  # 1=Mon, ...,7=Sun
    weekday_str = day_names[weekday_index - 1]
    offset = today.daysTo(date)
    suffix = ""
    if offset == 0:
        suffix = "Today"
    elif offset == 1:
        suffix = "Tomorrow"
    elif offset == -1:
        suffix = "Yesterday"
    if suffix:
        return f"{month_str} {day_str}   {weekday_str}   {suffix}"
    else:
        return f"{month_str} {day_str}   {weekday_str}"


##############################################################################
# 辅助函数：单行文本省略
##############################################################################
def setSingleLineElidedText(label: QLabel, text: str, max_width: int):
    fm = label.fontMetrics()
    elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, max_width)
    label.setText(elided)


##############################################################################
# 辅助函数：多行文本省略
##############################################################################
def setMultiLineElidedText(label: QLabel, text: str, max_width: int, max_height: int):
    fm = label.fontMetrics()
    label.setText(text)
    br = fm.boundingRect(0, 0, max_width, 0, Qt.TextFlag.TextWordWrap, text)
    if br.height() <= max_height:
        return
    display_text = text
    while len(display_text) > 0:
        display_text = display_text[:-1]
        test_text = display_text.rstrip() + "..."
        br = fm.boundingRect(0, 0, max_width, 0, Qt.TextFlag.TextWordWrap, test_text)
        if br.height() <= max_height:
            label.setText(test_text)
            return
    label.setText("...")


##############################################################################
# 颜色选择对话框
##############################################################################
class ColorPickerDialog(QDialog):
    COLOR_ITEMS = [
        ("#FF6666", "#DD4444"),
        ("#66CC66", "#44AA44"),
        ("#66CCCC", "#44AAAA"),
        ("#FFCC66", "#DDAA44"),
        ("#CC66FF", "#AA44DD"),
        ("#CCCC66", "#AAAA44"),
    ]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #333333;")
        self.setFixedSize(220, 60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.selected_color = None
        for (normal_color, hover_color) in self.COLOR_ITEMS:
            btn = QPushButton(self)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {normal_color};
                    border-radius: 5px;
                    border: 1px solid #888;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
            btn.clicked.connect(lambda _, col=normal_color: self.select_color(col))
            layout.addWidget(btn)
    def select_color(self, color_value):
        self.selected_color = color_value
        self.accept()


##############################################################################
# 代办卡片
##############################################################################
class ToDoCard(QWidget):
    def __init__(self, todo_data, parent=None, parent_page=None):
        super().__init__(parent)
        self.todo_data = todo_data or {}
        self.parent_page = parent_page
        self.setFixedSize(160, 140)
        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, 160, 140)
        self.frame.setStyleSheet(UIDesign.TODO_CARD_FRAME_STYLE)
        self.category_circle = QLabel(self.frame)
        self.category_circle.setGeometry(10, 10, 14, 14)
        circle_color = self.todo_data.get("category_color") or self.todo_data.get("color") or "#FF6666"
        self.category_circle.setStyleSheet(f"background-color: {circle_color}; border-radius: 7px;")
        self.title_label = QLabel(self.frame)
        self.title_label.setGeometry(30, 2, 110, 20)
        self.title_label.setStyleSheet("color: #fff; font-size: 12px;")
        self.date_label = QLabel(self.frame)
        self.date_label.setGeometry(30, 20, 120, 20)
        self.date_label.setStyleSheet("color: #aaa; font-size: 11px;")
        self.detail_back = QFrame(self.frame)
        self.detail_back.setGeometry(10, 45, 140, 65)
        self.detail_back.setStyleSheet("background-color: #6C6A6A; border-radius: 5px;")
        self.desc_label = QLabel(self.frame)
        self.desc_label.setGeometry(10, 45, 140, 65)
        self.desc_label.setStyleSheet("color: #ccc; font-size: 11px; background-color: #6C6A6A;")
        self.desc_label.setWordWrap(True)
        self.diff_label = QLabel(self.frame)
        self.diff_label.setGeometry(10, 115, 80, 20)
        self.diff_label.setStyleSheet("color: #fff; font-size: 11px;")
        self.collection_btn = QPushButton("Collect", self.frame)
        self.collection_btn.setGeometry(90, 115, 60, 25)
        self.collection_btn.setStyleSheet(UIDesign.CARD_COLLECTION_BUTTON_STYLE)
        self.collection_btn.clicked.connect(self.toggle_collection)
        if self.todo_data.get("collected", False):
            self.collection_btn.setText("★")
        self.delete_btn = QPushButton("X", self.frame)
        self.delete_btn.setGeometry(135, 5, 20, 20)
        self.delete_btn.setStyleSheet(UIDesign.CARD_DELETE_BUTTON_STYLE)
        self.delete_btn.clicked.connect(self.delete_card)
        self.refresh_card_ui()

    def refresh_card_ui(self):
        title_text = self.todo_data.get("title", "Title...")
        date_text = self.todo_data.get("date", "Select")
        desc_text = self.todo_data.get("description", "Description...")
        diff_text = self.todo_data.get("degree", "Easy")
        setSingleLineElidedText(self.title_label, title_text, self.title_label.width())
        setSingleLineElidedText(self.date_label, date_text, self.date_label.width())
        setMultiLineElidedText(self.desc_label, desc_text, 140, 65)
        self.diff_label.setText(diff_text)

    def mousePressEvent(self, event: QMouseEvent):
        if self.collection_btn.geometry().contains(event.pos()):
            return super().mousePressEvent(event)
        if self.delete_btn.geometry().contains(event.pos()):
            return super().mousePressEvent(event)
        if self.parent_page and hasattr(self.parent_page, "open_edit_dialog"):
            self.parent_page.open_edit_dialog(self.todo_data, self)

    def toggle_collection(self):
        current = self.todo_data.get("collected", False)
        self.todo_data["collected"] = not current
        if self.todo_data["collected"]:
            self.collection_btn.setText("★")
        else:
            self.collection_btn.setText("Collect")
        task_id = self.todo_data.get("id")
        if task_id and self.parent_page and hasattr(self.parent_page, "db"):
            update_data = {
                "color": self.todo_data.get("category_color", "#FF6666"),
                "category": self.todo_data.get("category", "Unknown"),
                "title": self.todo_data.get("title", ""),
                "date": self.todo_data.get("date", "2025-01-01"),
                "degree": self.todo_data.get("degree", "Easy"),
                "description": self.todo_data.get("description", ""),
                "collected": 1 if self.todo_data["collected"] else 0
            }
            self.parent_page.db.update_task(task_id, update_data)
        if self.parent_page:
            if hasattr(self.parent_page, "after_db_changed"):
                self.parent_page.after_db_changed()
            elif hasattr(self.parent_page, "refresh_view"):
                self.parent_page.refresh_view()

    def delete_card(self):
        if self.parent_page and hasattr(self.parent_page, "remove_card"):
            self.parent_page.remove_card(self)


##############################################################################
# 编辑对话框
##############################################################################
class ToDoEditDialog(QDialog):
    def __init__(self, todo_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Todo Card")
        self.setFixedSize(530, 367)

        self.todo_data = todo_data or {}
        self.setStyleSheet("background-color: #4c4c4c; color: #ffffff;")

        self.category_circle = QLabel(self)
        self.category_circle.setGeometry(10, 10, 30, 30)
        circle_color = self.todo_data.get("category_color", "#FF6666")
        self.category_circle.setStyleSheet(f"background-color: {circle_color}; border-radius: 15px;")
        self.category_circle.installEventFilter(self)

        self.category_label = QLabel("Category:", self)
        self.category_label.setGeometry(50, 15, 70, 20)

        self.category_edit = QLineEdit(self)
        self.category_edit.setGeometry(130, 15, 120, 24)
        self.category_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        self.category_edit.setText(self.todo_data.get("category", "Work"))

        self.title_label = QLabel("Title:", self)
        self.title_label.setGeometry(10, 60, 40, 20)
        self.title_edit = QLineEdit(self)
        self.title_edit.setGeometry(60, 60, 200, 24)
        self.title_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        default_title = self.todo_data.get("title", "")
        if not default_title:
            default_title = "Title....."
        self.title_edit.setText(default_title)

        self.date_label = QLabel("Date:", self)
        self.date_label.setGeometry(280, 60, 40, 20)
        self.date_edit = QDateEdit(self)
        self.date_edit.setGeometry(330, 60, 150, 24)
        self.date_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        self.date_edit.setCalendarPopup(True)
        old_date = self.todo_data.get("date", "")
        if old_date and len(old_date.split("-")) == 3:
            y, m, d = old_date.split("-")
            try:
                self.date_edit.setDate(QDate(int(y), int(m), int(d)))
            except:
                self.date_edit.setDate(QDate.currentDate())
        else:
            self.date_edit.setDate(QDate.currentDate())
        self.degree_label = QLabel("Degree:", self)
        self.degree_label.setGeometry(10, 100, 50, 20)

        self.rb_easy = QRadioButton("Easy", self)
        self.rb_easy.setGeometry(70, 100, 60, 20)
        self.rb_easy.setStyleSheet("color: #fff;")
        self.rb_normal = QRadioButton("Normal", self)
        self.rb_normal.setGeometry(130, 100, 70, 20)
        self.rb_normal.setStyleSheet("color: #fff;")
        self.rb_hard = QRadioButton("Hard", self)
        self.rb_hard.setGeometry(200, 100, 60, 20)
        self.rb_hard.setStyleSheet("color: #fff;")

        self.degree_group = QButtonGroup(self)
        self.degree_group.addButton(self.rb_easy)
        self.degree_group.addButton(self.rb_normal)
        self.degree_group.addButton(self.rb_hard)
        current_diff = self.todo_data.get("degree", "Easy")
        if current_diff == "Easy":
            self.rb_easy.setChecked(True)
        elif current_diff == "Normal":
            self.rb_normal.setChecked(True)
        else:
            self.rb_hard.setChecked(True)


        self.desc_label = QLabel("Description:", self)
        self.desc_label.setGeometry(10, 140, 80, 20)
        self.desc_edit = QTextEdit(self)
        self.desc_edit.setGeometry(10, 165, 510, 140)
        self.desc_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        default_desc = self.todo_data.get("description", "")
        if not default_desc:
            default_desc = "Description..."
        self.desc_edit.setPlainText(default_desc)

        self.cancel_btn = QPushButton("cancel", self)
        self.cancel_btn.setGeometry(340, 320, 80, 30)
        self.cancel_btn.setStyleSheet(UIDesign.EDIT_DIALOG_BUTTON_STYLE)
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn = QPushButton("Confirm", self)
        self.confirm_btn.setGeometry(430, 320, 80, 30)
        self.confirm_btn.setStyleSheet(UIDesign.EDIT_DIALOG_BUTTON_STYLE)
        self.confirm_btn.clicked.connect(self.save_data)

    def eventFilter(self, obj, event):
        if obj == self.category_circle and event.type() == QEvent.Type.MouseButtonPress:
            self.pick_color()
            return True
        return super().eventFilter(obj, event)

    def pick_color(self):
        picker = ColorPickerDialog(self)
        picker.move(self.mapToGlobal(self.category_circle.pos()) + QPoint(0, 30))
        if picker.exec() == QDialog.DialogCode.Accepted:
            chosen_color = picker.selected_color
            if chosen_color:
                self.category_circle.setStyleSheet(f"background-color: {chosen_color}; border-radius:15px;")

    def save_data(self):
        circle_style = self.category_circle.styleSheet()
        color_str = "#FF6666"
        if "background-color:" in circle_style:
            part = circle_style.split("background-color:")[-1]
            color_str = part.split(";")[0].strip()
        self.todo_data["category_color"] = color_str
        self.todo_data["category"] = self.category_edit.text()
        self.todo_data["title"] = self.title_edit.text()
        date_val = self.date_edit.date()
        self.todo_data["date"] = date_val.toString("yyyy-MM-dd")
        if self.rb_easy.isChecked():
            self.todo_data["degree"] = "Easy"
        elif self.rb_normal.isChecked():
            self.todo_data["degree"] = "Normal"
        else:
            self.todo_data["degree"] = "Hard"
        self.todo_data["description"] = self.desc_edit.toPlainText()
        self.accept()


##############################################################################
# Recent Page (带日期选择组件，显示当天任务)
##############################################################################
class RecentPage(QWidget):
    newCategory = pyqtSignal(str, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(820, 600)
        self.setStyleSheet(UIDesign.PAGE_BG)
        self.db = DBManager()
        self.today = QDate.currentDate()
        self.selected_date = self.today
        self.day_count = 7
        self.offset = 3
        self.base_date = self.today.addDays(-self.offset)
        self.style_normal = """
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """
        self.style_selected = """
            QPushButton {
                background-color: #3399FF;
                color: white;
                border-radius: 5px;
            }
        """
        self.date_buttons = []
        self.selected_index = self.offset
        for i in range(self.day_count):
            btn = QPushButton(self)
            btn.setGeometry(20 + i * 50, 10, 40, 30)
            btn.clicked.connect(lambda _, idx=i: self.handle_date_button_click(idx))
            self.date_buttons.append(btn)
        self.date_label = QLabel("", self)
        self.date_label.setGeometry(380, 10, 220, 30)
        self.date_label.setStyleSheet("color: white; font-size: 16px;")
        self.add_button = QPushButton("Add", self)
        self.add_button.setGeometry(720, 10, 80, 30)
        self.add_button.setStyleSheet(UIDesign.TODO_ADD_STYLE)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(10, 50, 800, 440)
        self.scroll_area.setStyleSheet("background-color: #3c3c3c;")
        self.scroll_area.setWidgetResizable(True)
        self.cards_widget = QWidget()
        self.grid_layout = QGridLayout(self.cards_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(30)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        for c in range(4):
            self.grid_layout.setColumnMinimumWidth(c, 160)
        self.scroll_area.setWidget(self.cards_widget)
        self.all_tasks = []
        self.todo_list = []
        self.card_widgets = []
        self.load_tasks_from_db()
        self.update_date_buttons()
        self.update_button_styles()
        self.set_date_label_text()

    def load_tasks_from_db(self):
        rows = self.db.fetch_all_tasks()
        self.all_tasks.clear()
        for row in rows:
            data = {
                "id": row["id"],
                "category_color": row["color"],
                "category": row["category"],
                "title": row["title"],
                "date": row["date"],
                "degree": row["degree"],
                "description": row["description"],
                "collected": bool(row["collected"])
            }
            self.all_tasks.append(data)
        self.do_date_filter(self.selected_date)

    def update_date_buttons(self):
        for i, btn in enumerate(self.date_buttons):
            day = self.base_date.addDays(i)
            btn.setText(str(day.day()))

    def update_button_styles(self):
        for i, btn in enumerate(self.date_buttons):
            btn.setStyleSheet(self.style_selected if i == self.selected_index else self.style_normal)

    def handle_date_button_click(self, idx: int):
        self.selected_index = idx
        self.selected_date = self.base_date.addDays(idx)
        self.update_button_styles()
        self.set_date_label_text()
        self.do_date_filter(self.selected_date)

    def set_date_label_text(self):
        self.date_label.setText(english_date_label(self.selected_date, self.today))

    def do_date_filter(self, date: QDate):
        date_str = date.toString("yyyy-MM-dd")
        self.todo_list.clear()
        self.card_widgets.clear()
        for task in self.all_tasks:
            if task["date"] == date_str:
                self.todo_list.append(task)
                card = ToDoCard(task, parent=self.cards_widget, parent_page=self)
                self.card_widgets.append(card)
        self.refresh_cards()

    def refresh_cards(self):
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        for i, data in enumerate(self.todo_list):
            card = self.card_widgets[i]
            card.refresh_card_ui()
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        self.cards_widget.update()

    def refresh_view(self):
        self.load_tasks_from_db()

    def remove_card(self, card_widget):
        idx = -1
        for i, w in enumerate(self.card_widgets):
            if w == card_widget:
                idx = i
                break
        if idx != -1:
            card_data = self.todo_list[idx]
            task_id = card_data.get("id")
            if task_id:
                self.db.delete_task(task_id)
            self.load_tasks_from_db()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_add_dialog(self):
        default_data = {"date": self.selected_date.toString("yyyy-MM-dd")}
        dialog = ToDoEditDialog(todo_data=default_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.todo_data
            new_data.setdefault("collected", False)
            self.db.insert_task({
                "color": new_data["category_color"],
                "category": new_data["category"],
                "title": new_data["title"],
                "date": new_data["date"],
                "degree": new_data["degree"],
                "description": new_data["description"],
                "collected": 1 if new_data["collected"] else 0
            })
            self.load_tasks_from_db()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_edit_dialog(self, todo_data, card_widget):
        dialog = ToDoEditDialog(todo_data=todo_data.copy(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo_data.update(dialog.todo_data)
            cat_text = todo_data.get("category", "Unknown")
            cat_color = todo_data.get("category_color", "#FF6666")
            if not any(t["category"] == cat_text for t in self.all_tasks if t is not todo_data):
                self.newCategory.emit(cat_text, cat_color)
            task_id = todo_data.get("id")
            if task_id:
                update_data = {
                    "color": cat_color,
                    "category": cat_text,
                    "title": todo_data.get("title", ""),
                    "date": todo_data.get("date", "2025-01-01"),
                    "degree": todo_data.get("degree", "Easy"),
                    "description": todo_data.get("description", ""),
                    "collected": 1 if todo_data.get("collected", False) else 0
                }
                self.db.update_task(task_id, update_data)
            card_widget.refresh_card_ui()
            circle_color = todo_data.get("category_color", "#FF6666")
            card_widget.category_circle.setStyleSheet(f"background-color: {circle_color}; border-radius: 7px;")
            self.do_date_filter(self.selected_date)

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()


##############################################################################
# Collection Page
##############################################################################
class CollectionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(820, 600)
        self.setStyleSheet(UIDesign.PAGE_BG)
        self.db = DBManager()
        self.add_button = QPushButton("Add", self)
        self.add_button.setGeometry(720, 10, 80, 30)
        self.add_button.setStyleSheet(UIDesign.TODO_ADD_STYLE)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(10, 50, 800, 440)
        self.scroll_area.setStyleSheet("background-color: #3c3c3c;")
        self.scroll_area.setWidgetResizable(True)
        self.cards_widget = QWidget()
        self.grid_layout = QGridLayout(self.cards_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(30)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        for c in range(4):
            self.grid_layout.setColumnMinimumWidth(c, 160)
        self.scroll_area.setWidget(self.cards_widget)
        self.todo_list = []
        self.card_widgets = []
        self.load_tasks()

    def load_tasks(self):
        rows = self.db.fetch_all_tasks()
        self.todo_list.clear()
        self.card_widgets.clear()
        for row in rows:
            if row["collected"] == 1:
                data = {
                    "id": row["id"],
                    "category_color": row["color"],
                    "category": row["category"],
                    "title": row["title"],
                    "date": row["date"],
                    "degree": row["degree"],
                    "description": row["description"],
                    "collected": True
                }
                self.todo_list.append(data)
                card = ToDoCard(data, parent=self.cards_widget, parent_page=self)
                self.card_widgets.append(card)
        self.refresh_cards()

    def refresh_cards(self):
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.todo_list.sort(key=lambda t: t["date"])
        for i, data in enumerate(self.todo_list):
            card = self.card_widgets[i]
            card.refresh_card_ui()
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        self.cards_widget.update()

    def refresh_view(self):
        self.load_tasks()

    def remove_card(self, card_widget):
        idx = -1
        for i, w in enumerate(self.card_widgets):
            if w == card_widget:
                idx = i
                break
        if idx != -1:
            card_data = self.todo_list[idx]
            task_id = card_data.get("id")
            if task_id:
                self.db.delete_task(task_id)
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_add_dialog(self):
        default_data = {"date": QDate.currentDate().toString("yyyy-MM-dd")}
        dialog = ToDoEditDialog(todo_data=default_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.todo_data
            new_data.setdefault("collected", False)
            self.db.insert_task({
                "color": new_data["category_color"],
                "category": new_data["category"],
                "title": new_data["title"],
                "date": new_data["date"],
                "degree": new_data["degree"],
                "description": new_data["description"],
                "collected": 1 if new_data["collected"] else 0
            })
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()


##############################################################################
# All Page
##############################################################################
class AllPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(820, 600)
        self.setStyleSheet(UIDesign.PAGE_BG)
        self.db = DBManager()
        self.add_button = QPushButton("Add", self)
        self.add_button.setGeometry(720, 10, 80, 30)
        self.add_button.setStyleSheet(UIDesign.TODO_ADD_STYLE)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(10, 50, 800, 440)
        self.scroll_area.setStyleSheet("background-color: #3c3c3c;")
        self.scroll_area.setWidgetResizable(True)
        self.cards_widget = QWidget()
        self.grid_layout = QGridLayout(self.cards_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(30)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        for c in range(4):
            self.grid_layout.setColumnMinimumWidth(c, 160)
        self.scroll_area.setWidget(self.cards_widget)
        self.todo_list = []
        self.card_widgets = []
        self.load_tasks()

    def load_tasks(self):
        rows = self.db.fetch_all_tasks()
        self.todo_list.clear()
        self.card_widgets.clear()
        for row in rows:
            data = {
                "id": row["id"],
                "category_color": row["color"],
                "category": row["category"],
                "title": row["title"],
                "date": row["date"],
                "degree": row["degree"],
                "description": row["description"],
                "collected": bool(row["collected"])
            }
            self.todo_list.append(data)
            card = ToDoCard(data, parent=self.cards_widget, parent_page=self)
            self.card_widgets.append(card)
        self.refresh_cards()

    def refresh_cards(self):
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.todo_list.sort(key=lambda t: t["date"])
        for i, data in enumerate(self.todo_list):
            card = self.card_widgets[i]
            card.refresh_card_ui()
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        self.cards_widget.update()

    def refresh_view(self):
        self.load_tasks()

    def remove_card(self, card_widget):
        idx = -1
        for i, w in enumerate(self.card_widgets):
            if w == card_widget:
                idx = i
                break
        if idx != -1:
            card_data = self.todo_list[idx]
            task_id = card_data.get("id")
            if task_id:
                self.db.delete_task(task_id)
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_add_dialog(self):
        default_data = {"date": QDate.currentDate().toString("yyyy-MM-dd")}
        dialog = ToDoEditDialog(todo_data=default_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.todo_data
            new_data.setdefault("collected", False)
            self.db.insert_task({
                "color": new_data["category_color"],
                "category": new_data["category"],
                "title": new_data["title"],
                "date": new_data["date"],
                "degree": new_data["degree"],
                "description": new_data["description"],
                "collected": 1 if new_data["collected"] else 0
            })
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_edit_dialog(self, todo_data, card_widget):
        dialog = ToDoEditDialog(todo_data=todo_data.copy(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo_data.update(dialog.todo_data)
            task_id = todo_data.get("id")
            if task_id:
                self.db.update_task(task_id, {
                    "color": todo_data["category_color"],
                    "category": todo_data["category"],
                    "title": todo_data["title"],
                    "date": todo_data["date"],
                    "degree": todo_data["degree"],
                    "description": todo_data["description"],
                    "collected": 1 if todo_data["collected"] else 0
                })
            card_widget.refresh_card_ui()
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()


##############################################################################
# 新增：CategoryPage —— 根据特定 color 和 category 过滤待办事项
##############################################################################
class CategoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(820, 600)
        self.setStyleSheet(UIDesign.PAGE_BG)
        self.db = DBManager()
        self.filter_color = None
        self.filter_category = None

        self.add_button = QPushButton("Add", self)
        self.add_button.setGeometry(720, 10, 80, 30)
        self.add_button.setStyleSheet(UIDesign.TODO_ADD_STYLE)
        self.add_button.clicked.connect(self.open_add_dialog)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(10, 50, 800, 540)
        self.scroll_area.setStyleSheet("background-color: #3c3c3c;")
        self.scroll_area.setWidgetResizable(True)
        self.cards_widget = QWidget()
        self.grid_layout = QGridLayout(self.cards_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(30)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        for c in range(4):
            self.grid_layout.setColumnMinimumWidth(c, 160)
        self.scroll_area.setWidget(self.cards_widget)

        self.todo_list = []
        self.card_widgets = []

    def set_filter(self, color: str, category: str):
        self.filter_color = color
        self.filter_category = category
        self.load_tasks()

    def load_tasks(self):
        rows = self.db.fetch_all_tasks()
        self.todo_list.clear()
        self.card_widgets.clear()
        for row in rows:
            if row["color"] == self.filter_color and row["category"] == self.filter_category:
                data = {
                    "id": row["id"],
                    "category_color": row["color"],
                    "category": row["category"],
                    "title": row["title"],
                    "date": row["date"],
                    "degree": row["degree"],
                    "description": row["description"],
                    "collected": bool(row["collected"])
                }
                self.todo_list.append(data)
                card = ToDoCard(data, parent=self.cards_widget, parent_page=self)
                self.card_widgets.append(card)
        self.refresh_cards()

    def refresh_cards(self):
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.todo_list.sort(key=lambda t: t["date"])
        for i, data in enumerate(self.todo_list):
            card = self.card_widgets[i]
            card.refresh_card_ui()
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        self.cards_widget.update()

    def refresh_view(self):
        self.load_tasks()

    def remove_card(self, card_widget):
        idx = -1
        for i, w in enumerate(self.card_widgets):
            if w == card_widget:
                idx = i
                break
        if idx != -1:
            card_data = self.todo_list[idx]
            task_id = card_data.get("id")
            if task_id:
                self.db.delete_task(task_id)
            self.load_tasks()

    def open_add_dialog(self):
        default_data = {
            "date": QDate.currentDate().toString("yyyy-MM-dd"),
            "category": self.filter_category if self.filter_category else "",
            "category_color": self.filter_color if self.filter_color else "#FF6666"
        }
        dialog = ToDoEditDialog(todo_data=default_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.todo_data
            new_data.setdefault("collected", False)
            self.db.insert_task({
                "color": new_data["category_color"],
                "category": new_data["category"],
                "title": new_data["title"],
                "date": new_data["date"],
                "degree": new_data["degree"],
                "description": new_data["description"],
                "collected": 1 if new_data["collected"] else 0
            })
            self.load_tasks()

    def open_edit_dialog(self, todo_data, card_widget):
        dialog = ToDoEditDialog(todo_data=todo_data.copy(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo_data.update(dialog.todo_data)
            task_id = todo_data.get("id")
            if task_id:
                self.db.update_task(task_id, {
                    "color": todo_data["category_color"],
                    "category": todo_data["category"],
                    "title": todo_data["title"],
                    "date": todo_data["date"],
                    "degree": todo_data["degree"],
                    "description": todo_data["description"],
                    "collected": 1 if todo_data["collected"] else 0
                })
            card_widget.refresh_card_ui()
            self.load_tasks()


##############################################################################
# 新增：FuturePage —— 显示日期为今天及之后的代办事项
##############################################################################
class FuturePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(820, 600)
        self.setStyleSheet(UIDesign.PAGE_BG)
        self.db = DBManager()

        self.add_button = QPushButton("Add", self)
        self.add_button.setGeometry(720, 10, 80, 30)
        self.add_button.setStyleSheet(UIDesign.TODO_ADD_STYLE)
        self.add_button.clicked.connect(self.open_add_dialog)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(10, 50, 800, 440)
        self.scroll_area.setStyleSheet("background-color: #3c3c3c;")
        self.scroll_area.setWidgetResizable(True)

        self.cards_widget = QWidget()
        self.grid_layout = QGridLayout(self.cards_widget)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setHorizontalSpacing(30)
        self.grid_layout.setVerticalSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        for c in range(4):
            self.grid_layout.setColumnMinimumWidth(c, 160)

        self.scroll_area.setWidget(self.cards_widget)

        self.todo_list = []
        self.card_widgets = []

        self.load_tasks()

    def load_tasks(self):
        rows = self.db.fetch_all_tasks()
        self.todo_list.clear()
        self.card_widgets.clear()

        today = QDate.currentDate()
        for row in rows:
            task_date = QDate.fromString(row["date"], "yyyy-MM-dd")
            if task_date.isValid() and task_date >= today:
                data = {
                    "id": row["id"],
                    "category_color": row["color"],
                    "category": row["category"],
                    "title": row["title"],
                    "date": row["date"],
                    "degree": row["degree"],
                    "description": row["description"],
                    "collected": bool(row["collected"])
                }
                self.todo_list.append(data)
                card = ToDoCard(data, parent=self.cards_widget, parent_page=self)
                self.card_widgets.append(card)

        self.refresh_cards()

    def refresh_cards(self):
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        self.todo_list.sort(key=lambda t: t["date"])
        for i, data in enumerate(self.todo_list):
            card = self.card_widgets[i]
            card.refresh_card_ui()
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        self.cards_widget.update()

    def refresh_view(self):
        self.load_tasks()

    def remove_card(self, card_widget):
        idx = -1
        for i, w in enumerate(self.card_widgets):
            if w == card_widget:
                idx = i
                break
        if idx != -1:
            card_data = self.todo_list[idx]
            task_id = card_data.get("id")
            if task_id:
                self.db.delete_task(task_id)
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_add_dialog(self):
        default_data = {"date": QDate.currentDate().toString("yyyy-MM-dd")}
        dialog = ToDoEditDialog(todo_data=default_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.todo_data
            new_data.setdefault("collected", False)
            self.db.insert_task({
                "color": new_data["category_color"],
                "category": new_data["category"],
                "title": new_data["title"],
                "date": new_data["date"],
                "degree": new_data["degree"],
                "description": new_data["description"],
                "collected": 1 if new_data["collected"] else 0
            })
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()

    def open_edit_dialog(self, todo_data, card_widget):
        dialog = ToDoEditDialog(todo_data=todo_data.copy(), parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            todo_data.update(dialog.todo_data)
            task_id = todo_data.get("id")
            if task_id:
                self.db.update_task(task_id, {
                    "color": todo_data["category_color"],
                    "category": todo_data["category"],
                    "title": todo_data["title"],
                    "date": todo_data["date"],
                    "degree": todo_data["degree"],
                    "description": todo_data["description"],
                    "collected": 1 if todo_data["collected"] else 0
                })
            card_widget.refresh_card_ui()
            self.load_tasks()

        if hasattr(self, 'after_db_changed'):
            self.after_db_changed()


##############################################################################
# 主窗口：左侧按钮和右侧页面切换
##############################################################################
class Todo_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setFixedSize(1000, 600)

        # 主窗口持有一个 DBManager
        self.db = DBManager()

        self.central_widget = QWidget(self)
        self.central_widget.setGeometry(0, 20, 1000, 600)
        self.setCentralWidget(self.central_widget)

        # 左侧面板
        self.left_panel = QWidget(self.central_widget)
        self.left_panel.setGeometry(0, 10, 180, 530)
        self.left_panel.setStyleSheet(UIDesign.LEFT_PANEL_BG)

        # 上方 4 个页面按钮，均设置为 checkable 并使用统一顶部按钮样式
        self.recent_btn = QPushButton("Recent", self.left_panel)
        self.recent_btn.setGeometry(10, 20, 160, 40)
        self.recent_btn.setCheckable(True)
        self.recent_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.recent_btn.clicked.connect(lambda: self.switch_page(0))

        self.collection_btn = QPushButton("Collection", self.left_panel)
        self.collection_btn.setGeometry(10, 70, 160, 40)
        self.collection_btn.setCheckable(True)
        self.collection_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.collection_btn.clicked.connect(lambda: self.switch_page(1))

        self.all_btn = QPushButton("All", self.left_panel)
        self.all_btn.setGeometry(10, 120, 160, 40)
        self.all_btn.setCheckable(True)
        self.all_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.all_btn.clicked.connect(lambda: self.switch_page(2))

        # 将原 "Calendar" 改为 "Future"
        self.future_btn = QPushButton("Future", self.left_panel)
        self.future_btn.setGeometry(10, 170, 160, 40)
        self.future_btn.setCheckable(True)
        self.future_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.future_btn.clicked.connect(lambda: self.switch_page(3))

        # 将上方按钮加入同一个 QButtonGroup，实现互斥
        self.leftButtonGroup = QButtonGroup(self)
        self.leftButtonGroup.setExclusive(True)
        self.leftButtonGroup.addButton(self.recent_btn)
        self.leftButtonGroup.addButton(self.collection_btn)
        self.leftButtonGroup.addButton(self.all_btn)
        self.leftButtonGroup.addButton(self.future_btn)

        # Category 标签
        self.category_label = QLabel("Category", self.left_panel)
        self.category_label.setGeometry(10, 230, 160, 30)
        self.category_label.setStyleSheet("color: white; font-size: 18px;")

        # 创建一个 QScrollArea 用于存放动态生成的分类按钮
        self.category_scroll = QScrollArea(self.left_panel)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setGeometry(0, 270, 180, 250)
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setStyleSheet("background: transparent; border: none;")
        self.category_widget = QWidget()
        self.category_layout = QVBoxLayout(self.category_widget)
        self.category_layout.setSpacing(5)
        self.category_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.category_scroll.setWidget(self.category_widget)

        # 用一个字典维护动态生成的“(color, category) -> 按钮”
        self.category_buttons = {}
        self.category_start_y = 270

        # 右侧 QStackedWidget，使用统一页面背景样式
        self.pages_widget = QStackedWidget(self.central_widget)
        self.pages_widget.setGeometry(180, 10, 820, 530)
        self.pages_widget.setStyleSheet(UIDesign.PAGE_BG)

        # 页面：Recent, Collection, All, Future
        self.recent_page = RecentPage()
        self.recent_page.db = self.db
        self.recent_page.after_db_changed = self.refresh_all_views
        self.pages_widget.addWidget(self.recent_page)

        self.collection_page = CollectionPage()
        self.collection_page.db = self.db
        self.collection_page.after_db_changed = self.refresh_all_views
        self.pages_widget.addWidget(self.collection_page)

        self.all_page = AllPage()
        self.all_page.db = self.db
        self.all_page.after_db_changed = self.refresh_all_views
        self.pages_widget.addWidget(self.all_page)

        self.future_page = FuturePage()
        self.future_page.db = self.db
        self.future_page.after_db_changed = self.refresh_all_views
        self.pages_widget.addWidget(self.future_page)

        # Category 页面延迟创建
        self.category_page = None

        # 默认选中 Recent 按钮
        self.recent_btn.setChecked(True)
        self.pages_widget.setCurrentIndex(0)

        # 同步动态 Category 按钮
        self.update_category_buttons()

    def clean_old_tasks(self):
        today = QDate.currentDate()
        cutoff = today.addDays(-31)
        tasks = self.db.fetch_all_tasks()
        for task in tasks:
            task_date = QDate.fromString(task["date"], "yyyy-MM-dd")
            if task_date.isValid() and task_date < cutoff:
                self.db.delete_task(task["id"])

    def refresh_all_views(self):
        for i in range(self.pages_widget.count()):
            widget = self.pages_widget.widget(i)
            if hasattr(widget, "refresh_view"):
                widget.refresh_view()
        self.update_category_buttons()

    def showEvent(self, event):
        self.clean_old_tasks()
        self.refresh_all_views()
        super().showEvent(event)

    def switch_page(self, index: int):
        self.pages_widget.setCurrentIndex(index)

    def update_category_buttons(self):
        all_tasks = self.db.fetch_all_tasks()
        combos_in_db = set()
        for t in all_tasks:
            c = t["color"]
            cat = t["category"]
            if c and cat:
                combos_in_db.add((c, cat))
        combos_current = set(self.category_buttons.keys())
        to_delete = combos_current - combos_in_db
        to_add = combos_in_db - combos_current

        for combo in to_delete:
            btn = self.category_buttons[combo]
            btn.deleteLater()
            self.leftButtonGroup.removeButton(btn)
            del self.category_buttons[combo]

        for combo in to_add:
            color, cat_text = combo
            btn = QPushButton(cat_text, self.left_panel)
            btn.setCheckable(True)
            btn.setStyleSheet(UIDesign.get_category_button_style(color))
            btn.clicked.connect(partial(self.on_category_button_clicked, color, cat_text, btn))
            self.leftButtonGroup.addButton(btn)
            self.category_buttons[combo] = btn

        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        new_combos = sorted(list(self.category_buttons.keys()), key=lambda x: x[1])
        for combo in new_combos:
            btn = self.category_buttons[combo]
            btn.setFixedSize(160, 40)
            self.category_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def on_category_button_clicked(self, color: str, cat_text: str, btn: QPushButton):
        print(f"分类按钮点击: color={color}, category={cat_text}")
        if self.category_page is None:
            self.category_page = CategoryPage()
            self.category_page.db = self.db
            self.category_page.after_db_changed = self.refresh_all_views
            self.pages_widget.addWidget(self.category_page)
        self.category_page.set_filter(color, cat_text)
        idx = self.pages_widget.indexOf(self.category_page)
        self.pages_widget.setCurrentIndex(idx)
