import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QDate
from UIDesign import UIDesign  # 导入提取的UI配置

class PieChart(QWidget):
    """
    用于显示“剩余预算 / 本月预算”的简单饼图
    """
    def __init__(self, monthly_budget=500, left_budget=100, parent=None):
        super().__init__(parent)
        self.monthly = monthly_budget
        self.left = left_budget
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.draw_chart()

    def setData(self, monthly, left):
        self.monthly = monthly
        self.left = left
        self.draw_chart()

    def draw_chart(self):
        used = self.monthly - self.left
        if self.monthly > 0:
            ratio_used = used / self.monthly
            ratio_left = self.left / self.monthly
        else:
            ratio_used = 0
            ratio_left = 0

        sizes = [ratio_used, ratio_left]
        if sum(sizes) == 0:
            sizes = [0, 1]

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = ["#cc6666", "#66cc66"]
        self.figure.patch.set_facecolor('none')
        ax.set_facecolor('none')
        ax.set_position([0, 0, 1, 1])
        ax.axis('equal')
        ax.axis('off')
        ax.pie(sizes, colors=colors, labels=None, autopct=None, startangle=90,
               wedgeprops=dict(edgecolor='none'), radius=2)
        ax.axis('equal')
        self.canvas.draw()

class CategoryButton(QWidget):
    def __init__(self, cat_id, cat_name, delete_callback, filter_callback, parent=None):
        super().__init__(parent)
        self.cat_id = cat_id
        self.cat_name = cat_name
        self.delete_callback = delete_callback
        self.filter_callback = filter_callback
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(160, 40)
        self.default_style = UIDesign.CATEGORYBUTTON_DEFAULT_STYLE
        self.hover_style = UIDesign.CATEGORYBUTTON_HOVER_STYLE
        self.setStyleSheet(self.default_style)
        self.label = QLabel(self.cat_name, self)
        self.label.setGeometry(5, 5, 140, 30)
        self.label.setStyleSheet("background-color: transparent;")
        # 删除X号定义
        self.btn_delete = QPushButton("X", self)
        self.btn_delete.setGeometry(140, 10, 20, 20)
        self.btn_delete.setStyleSheet(UIDesign.CATEGORYBUTTON_DELETE_BUTTON_STYLE)
        self.btn_delete.setVisible(False)
        self.btn_delete.clicked.connect(self.on_delete_clicked)  # 新增的连接代码
        self.setMouseTracking(True)
        self.is_hovered = False

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        self.is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        self.is_hovered = False
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.btn_delete.geometry().contains(event.pos()):
                self.filter_callback(self.cat_id, self.cat_name)
        super().mousePressEvent(event)

    def on_delete_clicked(self):
        self.delete_callback(self.cat_id)

    def show_delete_button(self, show: bool):
        self.btn_delete.setVisible(show)

class ExpenseCard(QWidget):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.record_data = record_data or {}
        self.setFixedSize(750, 50)
        self.setMouseTracking(True)
        self.default_style = UIDesign.EXPENSECARD_DEFAULT_STYLE
        self.hover_style = UIDesign.EXPENSECARD_HOVER_STYLE
        self.setStyleSheet(self.default_style)
        self.background_frame = QFrame(self)
        self.background_frame.setGeometry(0, 0, 750, 50)

        # 显示日期（格式处理）
        self.date_label = QLabel(self)
        self.date_label.setGeometry(10, 5, 70, 20)
        self.date_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        date_str = self.record_data.get("date", "2025-03-28")
        date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
        if date_obj.isValid():
            self.date_label.setText(date_obj.toString("MM-dd"))
        else:
            self.date_label.setText(date_str)

        # 时间标签及其它信息
        self.time_label = QLabel(self)
        self.time_label.setGeometry(10, 25, 40, 20)
        self.time_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        self.time_label.setText(self.record_data.get("time", "00:00"))

        self.category_label = QLabel(self)
        self.category_label.setGeometry(70, 15, 70, 20)
        self.category_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        self.category_label.setText(self.record_data.get("category", "Category"))

        self.method_label = QLabel(self)
        self.method_label.setGeometry(160, 15, 60, 20)
        self.method_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        self.method_label.setText(self.record_data.get("method", "Card/Cash"))

        self.payee_label = QLabel(self)
        self.payee_label.setGeometry(240, 15, 140, 20)
        self.payee_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        self.payee_label.setText(self.record_data.get("payee", "Name..."))

        self.comment_label = QLabel(self)
        self.comment_label.setGeometry(410, 15, 180, 20)
        self.comment_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        self.comment_label.setText(self.record_data.get("comment", "Comments..."))

        self.amount_label = QLabel(self)
        self.amount_label.setGeometry(620, 15, 80, 20)
        self.amount_label.setStyleSheet(UIDesign.EXPENSECARD_LABEL_STYLE)
        amt = self.record_data.get("amount", "0")
        if float(amt) > 0:
            self.amount_label.setText(f" +{amt} £")
        else:
            self.amount_label.setText(f" {amt} £")

        self.delete_btn = QPushButton("X", self)
        self.delete_btn.setGeometry(710, 15, 30, 20)
        self.delete_btn.setStyleSheet(UIDesign.EXPENSECARD_DELETE_BUTTON_STYLE)
        self.delete_btn.setVisible(False)

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)

    def show_delete_button(self, visible: bool):
        self.delete_btn.setVisible(visible)

    def set_record_data(self, new_data: dict):
        self.record_data = new_data
        self.date_label.setText(self.record_data.get("date", "2025-03-28"))
        self.time_label.setText(self.record_data.get("time", "00:00"))
        self.category_label.setText(self.record_data.get("category", "Category"))
        self.method_label.setText(self.record_data.get("method", "Card/Cash"))
        self.payee_label.setText(self.record_data.get("payee", "Name..."))
        self.comment_label.setText(self.record_data.get("comment", "Comments..."))
        amt = self.record_data.get("amount", "0")
        if float(amt) > 0:
            self.amount_label.setText(f" +{amt} £")
        else:
            self.amount_label.setText(f" {amt} £")

class MonthSummaryWidget(QWidget):
    def __init__(self, month_info: dict, db, parent=None, forced_category=None):
        """
        month_info: {"month": "2025-03", "income": 100, "expense": 80}
        db: ExpDBManager 实例，用来查询该月的详细记录
        forced_category: 如果指定，则只加载该类别的记录
        """
        super().__init__(parent)
        self.db = db
        self.month_str = month_info["month"]
        self.income = month_info["income"]
        self.expense = month_info["expense"]
        self.forced_category = forced_category

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # 顶部汇总区域
        self.summary_frame = QFrame(self)
        self.summary_frame.setStyleSheet(UIDesign.MONTHSUMMARY_FRAME_STYLE)
        self.summary_frame.setFixedHeight(40)
        summary_layout = QHBoxLayout(self.summary_frame)
        summary_layout.setContentsMargins(10, 5, 10, 5)
        summary_layout.setSpacing(10)

        self.label_month = QLabel(f"{self.month_str}", self.summary_frame)
        self.label_month.setStyleSheet(UIDesign.MONTHSUMMARY_LABEL_STYLE)
        self.label_income = QLabel(f"Income:{self.income:.2f} £", self.summary_frame)
        self.label_income.setStyleSheet(UIDesign.MONTHSUMMARY_LABEL_STYLE)
        self.label_expense = QLabel(f"Expense:{self.expense:.2f} £", self.summary_frame)
        self.label_expense.setStyleSheet(UIDesign.MONTHSUMMARY_LABEL_STYLE)

        self.btn_detail = QPushButton("Detail", self.summary_frame)
        self.btn_detail.setStyleSheet(UIDesign.MONTHSUMMARY_BTN_DETAIL_STYLE)
        self.btn_detail.clicked.connect(self.toggle_detail)

        summary_layout.addWidget(self.label_month)
        summary_layout.addWidget(self.label_income)
        summary_layout.addWidget(self.label_expense)
        summary_layout.addStretch(1)
        summary_layout.addWidget(self.btn_detail)

        # 详细列表区域（初始隐藏）
        self.detail_frame = QFrame(self)
        self.detail_frame.setStyleSheet(UIDesign.MONTHSUMMARY_DETAIL_FRAME_STYLE)
        detail_layout = QVBoxLayout(self.detail_frame)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        detail_layout.setSpacing(10)
        self.detail_frame.setVisible(False)

        self.main_layout.addWidget(self.summary_frame)
        self.main_layout.addWidget(self.detail_frame)

        self.detail_cards = []
        self.is_detail_loaded = False

    def toggle_detail(self):
        visible = not self.detail_frame.isVisible()
        self.detail_frame.setVisible(visible)
        if visible:
            self.btn_detail.setText("Hide")
            if not self.is_detail_loaded:
                self.load_detail_cards()
                self.is_detail_loaded = True
        else:
            self.btn_detail.setText("Detail")

    def load_detail_cards(self):
        if self.forced_category:
            records = self.db.fetch_pay_data_by_month_and_category(self.month_str, self.forced_category)
        else:
            records = self.db.fetch_pay_data_by_month(self.month_str)
        layout = self.detail_frame.layout()
        for rec in records:
            card = ExpenseCard(rec, parent=self.detail_frame)
            layout.addWidget(card)
            self.detail_cards.append(card)
            card.mousePressEvent = lambda e, c=card: self.on_card_clicked(e, c)
            card.delete_btn.clicked.connect(lambda _, c=card: self.delete_one_card(c))
            # 根据上级页面的 delete_mode 标志显示/隐藏 X 按钮
            parent_page = self.parent()
            # make sure keeping the delete mode
            while parent_page and not hasattr(parent_page, "delete_mode"):
                parent_page = parent_page.parent()

            delete_mode = getattr(parent_page, "delete_mode", False)
            card.show_delete_button(delete_mode)

    def on_card_clicked(self, event, card):
        parent_page = self.parent()
        while parent_page and not hasattr(parent_page, "delete_mode"):
            parent_page = parent_page.parent()
        if parent_page and parent_page.delete_mode:
            return
        self.open_edit_dialog(card)

    def open_edit_dialog(self, card):
        old_data = card.record_data.copy()
        from Exp_Dialogs import AddExpenseDialog
        from PyQt6.QtWidgets import QDialog
        dialog = AddExpenseDialog(None)
        dialog.date_edit.setDate(QDate.fromString(old_data["date"], "yyyy-MM-dd"))
        # 使用 QTime.fromString 来设置时间
        from PyQt6.QtCore import QTime
        dialog.time_edit.setTime(QTime.fromString(old_data["time"], "HH:mm"))
        dialog.method_combo.setCurrentText(old_data["method"])

        original_amount = float(old_data["amount"])
        dialog.amount_edit.setText(str(abs(original_amount)))
        if original_amount < 0:
            dialog.type_combo.setCurrentText("Expense")
        else:
            dialog.type_combo.setCurrentText("Income")


        dialog.category_combo.setCurrentText(old_data["category"])
        dialog.payee_edit.setText(old_data["payee"])
        dialog.comment_edit.setPlainText(old_data["comment"])

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            record_id = old_data.get("id")
            if record_id is not None:
                self.db.update_pay_data(record_id, new_data)
            self.reload_detail_cards()

    def delete_one_card(self, card):
        record_id = card.record_data.get("id")
        if record_id:
            self.db.delete_pay_data(record_id)
        self.reload_detail_cards()

    def reload_detail_cards(self):
        layout = self.detail_frame.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.detail_cards.clear()
        self.is_detail_loaded = False
        self.load_detail_cards()
        self.is_detail_loaded = True
        self.detail_frame.setVisible(True)
        self.btn_detail.setText("Hide")
