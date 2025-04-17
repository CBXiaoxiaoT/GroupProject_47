import numpy as np
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QScrollArea, QVBoxLayout, QHBoxLayout, QComboBox, QInputDialog, QDialog
from Exp_Dialogs import AddExpenseDialog
from Exp_Widgets import ExpenseCard, MonthSummaryWidget, PieChart
from Expdb_manager import ExpDBManager
from UIDesign import UIDesign  # 导入 UI 配置
from matplotlib import cm

class TodayPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(UIDesign.TODAY_PAGE_BG)
        self.records = []
        self.record_cards = []
        self.delete_mode = False
        self.db = ExpDBManager()

        # 左上部分（本日数据）
        self.daily_box = QFrame(self)
        self.daily_box.setGeometry(10, 10, 200, 70)
        self.daily_box.setStyleSheet(UIDesign.TODAY_DAILY_BOX_STYLE)
        self.label_daily_expense = QLabel("Today's expense: 0 £", self.daily_box)
        self.label_daily_expense.setGeometry(10, 10, 200, 20)
        self.label_daily_expense.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)
        self.label_daily_income = QLabel("Today's income: 0 £", self.daily_box)
        self.label_daily_income.setGeometry(10, 40, 200, 20)
        self.label_daily_income.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)

        # 中间部分（本月数据）
        self.daily_box2 = QFrame(self)
        self.daily_box2.setGeometry(230, 10, 220, 70)
        self.daily_box2.setStyleSheet(UIDesign.TODAY_DAILY_BOX_STYLE)
        self.label_daily_expense2 = QLabel("Month's expense: 0 £", self.daily_box2)
        self.label_daily_expense2.setGeometry(10, 10, 200, 20)
        self.label_daily_expense2.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)
        self.label_daily_income2 = QLabel("Month's income: 0 £", self.daily_box2)
        self.label_daily_income2.setGeometry(10, 40, 200, 20)
        self.label_daily_income2.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)

        # 右上部分（预算信息及饼图）
        self.monthly_box = QFrame(self)
        self.monthly_box.setGeometry(470, 10, 340, 70)
        self.monthly_box.setStyleSheet(UIDesign.TODAY_DAILY_BOX_STYLE)
        self.label_monthly_budget = QLabel("Month budget: 0 £", self.monthly_box)
        self.label_monthly_budget.setGeometry(10, 10, 200, 20)
        self.label_monthly_budget.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)
        self.label_left_budget = QLabel("Left budget: 0 £", self.monthly_box)
        self.label_left_budget.setGeometry(10, 40, 200, 20)
        self.label_left_budget.setStyleSheet(UIDesign.TODAY_LABEL_STYLE_SMALL)
        self.btn_edit_budget = QPushButton("...", self.monthly_box)
        self.btn_edit_budget.setGeometry(220, 10, 30, 20)
        self.btn_edit_budget.setStyleSheet(UIDesign.TODAY_BTN_EDIT_BUDGET_STYLE)
        self.btn_edit_budget.clicked.connect(self.edit_monthly_budget)
        self.pie_chart = PieChart(monthly_budget=1, left_budget=1, parent=self.monthly_box)
        self.pie_chart.setGeometry(270, 5, 60, 60)

        # 下方：今日账单区域
        self.bottom_frame = QFrame(self)
        self.bottom_frame.setGeometry(10, 100, 800, 420)
        self.bottom_frame.setStyleSheet(UIDesign.TODAY_BOTTOM_FRAME_STYLE)
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        self.label_today_title = QLabel("Today's Spreadsheet " + today_str, self.bottom_frame)
        self.label_today_title.setGeometry(10, 10, 400, 20)
        self.label_today_title.setStyleSheet(UIDesign.TODAY_TITLE_LABEL_STYLE)
        self.btn_delete = QPushButton("Delete", self.bottom_frame)
        self.btn_delete.setGeometry(700, 10, 80, 30)
        self.btn_delete.setStyleSheet(UIDesign.EXP_DELETE_BUTTON_STYLE)
        self.btn_delete.clicked.connect(self.toggle_delete_mode)
        self.btn_add = QPushButton("Add", self.bottom_frame)
        self.btn_add.setGeometry(610, 10, 80, 30)
        self.btn_add.setStyleSheet(UIDesign.EXP_ADD_BUTTON_STYLE)
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.content_back = QFrame(self.bottom_frame)
        self.content_back.setGeometry(10, 80, 780, 330)
        self.content_back.setStyleSheet(UIDesign.TODAY_CONTENT_BACK_STYLE)
        self.label_header_time = QLabel("Time", self.bottom_frame)
        self.label_header_time.setGeometry(35, 50, 40, 20)
        self.label_header_time.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.label_header_category = QLabel("Category", self.bottom_frame)
        self.label_header_category.setGeometry(95, 50, 70, 20)
        self.label_header_category.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.label_header_method = QLabel("Method", self.bottom_frame)
        self.label_header_method.setGeometry(185, 50, 60, 20)
        self.label_header_method.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.label_header_payee = QLabel("Payer or Payee", self.bottom_frame)
        self.label_header_payee.setGeometry(265, 50, 130, 20)
        self.label_header_payee.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.label_header_note = QLabel("Comment", self.bottom_frame)
        self.label_header_note.setGeometry(435, 50, 70, 20)
        self.label_header_note.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.label_header_amount = QLabel("Amount", self.bottom_frame)
        self.label_header_amount.setGeometry(645, 50, 70, 20)
        self.label_header_amount.setStyleSheet(UIDesign.TODAY_HEADER_LABEL_STYLE)
        self.today_scroll_area = QScrollArea(self.bottom_frame)
        self.today_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.today_scroll_area.setGeometry(25, 90, 780, 310)
        self.today_scroll_area.setStyleSheet(UIDesign.TODAY_SCROLL_AREA_STYLE)
        self.today_scroll_area.setWidgetResizable(True)
        self.records_container = QWidget()
        self.vlayout = QVBoxLayout(self.records_container)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(10)
        self.vlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.today_scroll_area.setWidget(self.records_container)
        self.load_data_for_today()
        self.update_labels_and_pie_chart()

    def load_data_for_today(self):
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        self.records = self.db.fetch_pay_data_by_date(today_str)
        self.refresh_table()

    def update_labels_and_pie_chart(self):
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        month_str = QDate.currentDate().toString("yyyy-MM")

        #load datas
        daily_stats = self.db.get_daily_statistics(today_str)
        daily_income = daily_stats["income"]
        daily_expense = daily_stats["expense"]
        self.label_daily_income.setText(f"Today's income: {daily_income:.2f} £")
        self.label_daily_expense.setText(f"Today's expense: {daily_expense:.2f} £")

        monthly_stats = self.db.get_monthly_statistics(month_str)
        monthly_income = monthly_stats["income"]
        monthly_expense = monthly_stats["expense"]
        self.label_daily_income2.setText(f"Month's income: {monthly_income:.2f} £")
        self.label_daily_expense2.setText(f"Month's expense: {monthly_expense:.2f} £")

        #load budgets
        budget_val = self.db.get_budget_for_month(month_str)
        self.label_monthly_budget.setText(f"Month budget: {budget_val:.2f} £")
        left_budget = budget_val - monthly_expense + monthly_income

        self.label_left_budget.setText(f"Left budget: {left_budget:.2f} £")
        pie_left = left_budget if left_budget > 0 else 0
        # To prevent the left budget > budget_val, which will cause error in pie chart
        if pie_left > budget_val:
            self.pie_chart.setData(budget_val, budget_val)
        else:
            self.pie_chart.setData(budget_val, pie_left)

    def open_add_dialog(self):
        if self.delete_mode:
            return
        dialog = AddExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.db.insert_pay_data(data)
            self.load_data_for_today()
            self.update_labels_and_pie_chart()

    def open_edit_dialog(self, card):
        if self.delete_mode:
            return
        old_data = card.record_data.copy()
        dialog = AddExpenseDialog(self)
        dialog.date_edit.setDate(QDate.fromString(old_data["date"], "yyyy-MM-dd"))
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
            self.load_data_for_today()
            self.update_labels_and_pie_chart()

    def delete_one_card(self, card):
        record_id = card.record_data.get("id")
        if record_id is not None:
            self.db.delete_pay_data(record_id)
        self.load_data_for_today()
        self.update_labels_and_pie_chart()

    def edit_monthly_budget(self):
        new_val, ok = QInputDialog.getInt(self, "Edit Budget", "Please type this month's budget:",
                                          500, 0, 99999999, 100)
        if ok:
            month_str = QDate.currentDate().toString("yyyy-MM")
            self.db.set_budget_for_month(month_str, float(new_val))
            self.update_labels_and_pie_chart()

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self.btn_add.setEnabled(not self.delete_mode)
        for card in self.record_cards:
            card.show_delete_button(self.delete_mode)

    def refresh_table(self):
        for c in self.record_cards:
            c.setParent(None)
        self.record_cards.clear()
        for rec in self.records:
            card = ExpenseCard(rec, parent=self.records_container)
            self.vlayout.addWidget(card)
            self.record_cards.append(card)
            card.mousePressEvent = lambda e, c=card: self.on_card_clicked(e, c)
            card.delete_btn.clicked.connect(lambda _, c=card: self.delete_one_card(c))
            card.show_delete_button(self.delete_mode)

    def on_card_clicked(self, event, card):
        btn_rect = card.delete_btn.geometry()
        if btn_rect.contains(event.pos()):
            return super(QWidget, card).mousePressEvent(event)
        else:
            self.open_edit_dialog(card)

    def showEvent(self, event):
        self.load_data_for_today()
        self.update_labels_and_pie_chart()
        super().showEvent(event)


class AllPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(UIDesign.ALL_PAGE_BG)
        self.db = ExpDBManager()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.toolbar = QHBoxLayout()
        self.label_title = QLabel("All Page", self)
        self.label_title.setStyleSheet(UIDesign.ALL_TITLE_LABEL_STYLE)
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.toolbar.addWidget(self.label_title)
        self.toolbar.addStretch(1)
        self.btn_add = QPushButton("Add", self)
        self.btn_add.setStyleSheet(UIDesign.EXP_ALL_ADD_BUTTON_STYLE)
        self.btn_add.clicked.connect(self.add_record)
        self.toolbar.addWidget(self.btn_add)
        self.btn_delete = QPushButton("Delete", self)
        self.btn_delete.setStyleSheet(UIDesign.EXP_ALL_DELETE_BUTTON_STYLE)
        self.btn_delete.clicked.connect(self.toggle_delete_mode)
        self.toolbar.addWidget(self.btn_delete)
        self.main_layout.addLayout(self.toolbar)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setStyleSheet(UIDesign.ALL_SCROLL_AREA_STYLE)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.delete_mode = False
        self.expanded_months = set()
        self.load_monthly_summary()

    def load_monthly_summary(self):
        self.expanded_months.clear()
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if isinstance(w, MonthSummaryWidget):
                if w.is_detail_loaded and w.detail_frame.isVisible():
                    self.expanded_months.add(w.month_str)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        months_info = self.db.fetch_all_months_with_stats()
        for m_info in months_info:
            widget = MonthSummaryWidget(m_info, db=self.db, parent=self.scroll_widget)
            self.scroll_layout.addWidget(widget)
            if m_info["month"] in self.expanded_months:
                widget.toggle_detail()

    def add_record(self):
        dialog = AddExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.db.insert_pay_data(data)
            self.load_monthly_summary()

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self.btn_add.setEnabled(not self.delete_mode)
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget and hasattr(widget, "detail_cards"):
                for card in widget.detail_cards:
                    card.show_delete_button(self.delete_mode)

    def refresh_data(self):
        self.load_monthly_summary()

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)


class SummaryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = ExpDBManager()
        self.setStyleSheet(UIDesign.SUMMARY_PAGE_BG)

        self.mode_combo = QComboBox(self)
        self.mode_combo.setGeometry(20, 10, 200, 40)
        self.mode_combo.setStyleSheet(UIDesign.SUMMARY_COMBO_STYLE)
        self.mode_combo.addItems(["Monthly", "Yearly"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        self.infor_frame = QFrame(self)
        self.infor_frame.setGeometry(20, 60, 300, 150)
        self.infor_frame.setStyleSheet(UIDesign.SUMMARY_INFOR_FRAME_STYLE)

        self.period_combo = QComboBox(self.infor_frame)
        self.period_combo.setGeometry(10, 10, 120, 40)
        self.period_combo.setStyleSheet(UIDesign.SUMMARY_PERIOD_COMBO_STYLE)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)

        self.label_income = QLabel("Income: 0", self.infor_frame)
        self.label_income.setGeometry(10, 60, 200, 20)
        self.label_income.setStyleSheet(UIDesign.SUMMARY_LABEL_INFO_STYLE)

        self.label_expense = QLabel("Expense: 0", self.infor_frame)
        self.label_expense.setGeometry(10, 85, 200, 20)
        self.label_expense.setStyleSheet(UIDesign.SUMMARY_LABEL_INFO_STYLE)

        self.label_net = QLabel("Total: 0", self.infor_frame)
        self.label_net.setGeometry(10, 110, 200, 20)
        self.label_net.setStyleSheet(UIDesign.SUMMARY_LABEL_INFO_STYLE)

        #The pie chart area
        self.pie_frame = QFrame(self)
        self.pie_frame.setGeometry(300, 20, 400, 400)
        self.pie_frame.setStyleSheet(UIDesign.SUMMARY_PIE_FRAME_STYLE)

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


        self.pie_figure = Figure(figsize=(2, 2), dpi=100)
        self.pie_figure.patch.set_facecolor('none')
        self.pie_canvas = FigureCanvasQTAgg(self.pie_figure)

        layout = QVBoxLayout(self.pie_frame)
        layout.setContentsMargins(0, 0, 0, 0)  # 去除边距
        layout.addWidget(self.pie_canvas)

        #use QScrollArea to show the labels
        self.custom_legend_scroll = QScrollArea(self.pie_frame)
        self.custom_legend_scroll.setGeometry(200, 50, 200, 130)
        self.custom_legend_scroll.setWidgetResizable(True)
        self.custom_legend_scroll.setStyleSheet(UIDesign.PIE_LABELS_STYLE)

        # 2) used to show the lables area
        self.legend_container = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(10, 10, 0, 0)
        self.legend_layout.setSpacing(2)
        self.custom_legend_scroll.setWidget(self.legend_container)

        #The bar chart area

        self.bar_frame = QFrame(self)
        self.bar_frame.setGeometry(60, 248, 700, 250)
        self.bar_frame.setStyleSheet(UIDesign.SUMMARY_BAR_FRAME_STYLE)

        self.bar_figure = Figure(figsize=(6, 2), dpi=100)
        self.bar_figure.patch.set_facecolor('none')

        self.bar_canvas = FigureCanvasQTAgg(self.bar_figure)
        self.bar_canvas.setParent(self.bar_frame)
        self.bar_canvas.setGeometry(0, 0, 700, 250)
        
        self._populate_period_combo()
        self.update_all_charts()

    def showEvent(self, event):
        self.update_all_charts()
        self._populate_period_combo()
        super().showEvent(event)

    def on_mode_changed(self, index):
        self._populate_period_combo()
        self.update_all_charts()

    def on_period_changed(self, index):
        self.update_all_charts()

    def _populate_period_combo(self):
        self.period_combo.blockSignals(True)
        self.period_combo.clear()
        mode = self.mode_combo.currentText()
        if mode == "Monthly":
            months_info = self.db.fetch_all_months_with_stats()
            month_list = sorted({m["month"] for m in months_info}, reverse=True) #reverse make sure we are in the latest day
            if not month_list:
                month_list = ["2025-01"]
            for m in month_list:
                self.period_combo.addItem(m)
        else:
            c = self.db.conn.cursor()
            c.execute("SELECT DISTINCT substr(date,1,4) AS y FROM pay_data ORDER BY y ASC")
            rows = c.fetchall()
            years = sorted({r["y"] for r in rows if r["y"]}, reverse=True)
            if not years:
                years = ["2025"]
            for y in years:
                self.period_combo.addItem(y)
        self.period_combo.blockSignals(False)

    def update_all_charts(self):
        mode = self.mode_combo.currentText()
        period_str = self.period_combo.currentText()
        if mode == "Monthly":
            self._update_monthly_info(period_str)
            self._update_monthly_pie(period_str)
            self._update_monthly_bar(period_str)
        else:
            self._update_yearly_info(period_str)
            self._update_yearly_pie(period_str)
            self._update_yearly_bar(period_str)

    def _update_monthly_info(self, month_str):
        stats = self.db.get_monthly_statistics(month_str)
        income = stats["income"]
        expense = stats["expense"]
        net = income - expense
        self.label_income.setText(f"Income: {income:.2f}")
        self.label_expense.setText(f"Expense: {expense:.2f}")
        self.label_net.setText(f"Total: {net:.2f}")

    def _update_monthly_pie(self, month_str):
        cat_list = self.db.get_expense_by_category_by_month(month_str)
        total_expense = sum(item["expense"] for item in cat_list)
        fig = self.pie_figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')

        if total_expense == 0:
            # If there is no data, then show no data
            patches = []
            ax.pie([1], colors=["#aaaaaa"], startangle=90)
            ax.text(0, 0, "No Data", ha="center", va="center", color="white", fontsize=12)
            ax.set_title("Expenses", color="white")
            labels = []
            percentages = []
        else:
            labels = [item["category"] for item in cat_list]
            values = [item["expense"] for item in cat_list]

            # use colormap to provide some colors that are not the same
            num_colors = len(values)
            cmap = cm.get_cmap("tab20")
            colors = [cmap(i) for i in np.linspace(0, 1, num_colors)]

            # not use autopct, so we don't have percent in the pie
            patches, _ = ax.pie(values, colors = colors ,startangle=90)
            percentages = [v / total_expense * 100 for v in values]
            ax.set_title("Expenses", color="white")

        ax.axis("equal")
        fig.subplots_adjust(right=0.5, left=0.1, top=0.9, bottom=0.5)
        self.pie_canvas.draw()

        # The label area
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        #if no data
        if total_expense == 0:
            no_data_label = QLabel("No Data")
            no_data_label.setStyleSheet("font-size: 8pt; color: white;")
            self.legend_layout.addWidget(no_data_label)
            return

        # else
        from matplotlib.colors import to_hex
        values = [item["expense"] for item in cat_list]
        for patch, category, pct, amount in zip(patches, labels, percentages, values):
            # 小容器：水平布局
            item_widget = QWidget()
            h_layout = QHBoxLayout(item_widget)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(2)

            # a color cycle
            rgba = patch.get_facecolor()
            hex_color = to_hex(rgba)
            color_label = QLabel()
            color_label.setFixedSize(10, 10)
            color_label.setStyleSheet(f"background-color: {hex_color}; border-radius: 5px;")

            # test and percentage
            text_label = QLabel(f"{category}  {amount:.0f}£ ({pct:.1f}%)")
            text_label.setStyleSheet("font-size: 8pt; color: white;")

            # put them together
            h_layout.addWidget(color_label)
            h_layout.addWidget(text_label)
            h_layout.addStretch(1)

            self.legend_layout.addWidget(item_widget)

    def _update_monthly_bar(self, month_str):
        try:
            year, mon = map(int, month_str.split("-"))
        except:
            return
        months_list = []
        y, m = year, mon
        for _ in range(4):
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            months_list.append(f"{y:04d}-{m:02d}")
        months_list.reverse()
        months_list.append(month_str)
        incomes, expenses = [], []
        for ms in months_list:
            st = self.db.get_monthly_statistics(ms)
            incomes.append(st["income"])
            expenses.append(st["expense"])
        fig = self.bar_figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        x = np.arange(len(months_list))
        bar_width = 0.35
        bars_income = ax.bar(x, incomes, bar_width, label="Income", color="#66cc66")
        bars_expense = ax.bar(x + bar_width, expenses, bar_width, label="Expense", color="#cc6666")
        ax.bar_label(bars_income, fmt="%.0f", label_type='edge', color="white", fontsize=9)
        ax.bar_label(bars_expense, fmt="%.0f", label_type='edge', color="white", fontsize=9)
        ax.set_xticks(x + bar_width / 2)
        ax.set_xticklabels(months_list, rotation=45)
        ax.set_ylabel("Amount", color="white")
        ax.legend(facecolor='none', edgecolor='none', fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        fig.tight_layout()
        self.bar_canvas.draw()

    def _update_yearly_info(self, year_str):
        stats = self.db.get_yearly_statistics(year_str)
        income = stats["income"]
        expense = stats["expense"]
        net = income - expense
        self.label_income.setText(f"Income: {income}")
        self.label_expense.setText(f"Expense: {expense}")
        self.label_net.setText(f"Net: {net}")

    def _update_yearly_pie(self, year_str):
        # get data from database
        cat_list = self.db.get_expense_by_category_by_year(year_str)
        total_expense = sum(item["expense"] for item in cat_list)
        fig = self.pie_figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')

        if total_expense == 0:
            # no data then show no data
            patches = []
            ax.pie([1], colors=["#aaaaaa"], startangle=90)
            ax.text(0, 0, "No Data", ha="center", va="center",
                    color="white", fontsize=12)
            ax.set_title("Expenses", color="white")
            labels = []
            percentages = []
        else:
            labels = [item["category"] for item in cat_list]
            values = [item["expense"] for item in cat_list]

            #make sure every category has unique color
            num_colors = len(values)
            cmap = cm.get_cmap("tab20")
            colors = [cmap(i) for i in np.linspace(0, 1, num_colors)]
            # use colors
            patches, _ = ax.pie(values, colors=colors, startangle=90)
            percentages = [v / total_expense * 100 for v in values]
            ax.set_title("Expenses", color="white")

        ax.axis("equal")
        fig.subplots_adjust(right=0.5, left=0.1, top=0.9, bottom=0.5)
        self.pie_canvas.draw()

        # update labels area
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if total_expense == 0:
            no_data_label = QLabel("No Data")
            no_data_label.setStyleSheet("font-size: 8pt; color: white;")
            self.legend_layout.addWidget(no_data_label)
            return

        from matplotlib.colors import to_hex
        values = [item["expense"] for item in cat_list]
        for patch, category, pct, amount in zip(patches, labels, percentages, values):
            item_widget = QWidget()
            h_layout = QHBoxLayout(item_widget)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(2)

            rgba = patch.get_facecolor()
            hex_color = to_hex(rgba)
            color_label = QLabel()
            color_label.setFixedSize(10, 10)
            color_label.setStyleSheet(f"background-color: {hex_color}; border-radius: 5px;")

            text_label = QLabel(f"{category}  {amount:.0f}£ ({pct:.1f}%)")
            text_label.setStyleSheet("font-size: 8pt; color: white;")

            h_layout.addWidget(color_label)
            h_layout.addWidget(text_label)
            h_layout.addStretch(1)
            self.legend_layout.addWidget(item_widget)

    def _update_yearly_bar(self, year_str):
        try:
            current_year = int(year_str)
        except:
            return
        years_list = []
        for i in range(4):
            years_list.append(str(current_year - 4 + i))
        years_list.append(year_str)
        year_incomes = []
        year_expenses = []
        for y in years_list:
            cat_list = self.db.get_category_net_by_year(y)
            tincome, texpense = 0, 0
            for item in cat_list:
                net = item["net"]
                if net > 0:
                    tincome += net
                else:
                    texpense += abs(net)
            year_incomes.append(tincome)
            year_expenses.append(texpense)
        fig = self.bar_figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor('none')
        x = np.arange(len(years_list))
        bar_width = 0.35
        bars_income = ax.bar(x, year_incomes, bar_width, label="Income", color="#66cc66")
        bars_expense = ax.bar(x + bar_width, year_expenses, bar_width, label="Expense", color="#cc6666")
        ax.bar_label(bars_income, fmt="%.0f", label_type='edge', color="white", fontsize=9)
        ax.bar_label(bars_expense, fmt="%.0f", label_type='edge', color="white", fontsize=9)
        ax.set_xticks(x + bar_width / 2)
        ax.set_xticklabels(years_list, rotation=45)
        ax.set_ylabel("Amount", color="white")
        ax.legend(facecolor='none', edgecolor='none', fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        fig.tight_layout()
        self.bar_canvas.draw()


class CategoryFilterPage(QWidget):
    def __init__(self, category_name, db: ExpDBManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.category_name = category_name
        self.setStyleSheet(UIDesign.CATEGORY_PAGE_BG)
        self.delete_mode = False
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.toolbar = QHBoxLayout()
        self.label_title = QLabel(f"Category: {self.category_name}", self)
        self.label_title.setStyleSheet(UIDesign.CATEGORY_TITLE_LABEL_STYLE)
        self.toolbar.addWidget(self.label_title)
        self.toolbar.addStretch(1)
        self.btn_add = QPushButton("Add", self)
        self.btn_add.setStyleSheet(UIDesign.CATEGORY_BTN_ADD_STYLE)
        self.btn_add.clicked.connect(self.add_record)
        self.toolbar.addWidget(self.btn_add)
        self.btn_delete = QPushButton("Delete", self)
        self.btn_delete.setStyleSheet(UIDesign.CATEGORY_BTN_DELETE_STYLE)
        self.btn_delete.clicked.connect(self.toggle_delete_mode)
        self.toolbar.addWidget(self.btn_delete)
        self.main_layout.addLayout(self.toolbar)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setStyleSheet(UIDesign.CATEGORY_SCROLL_AREA_STYLE)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.expanded_months = set()
        self.load_monthly_summary()

    def load_monthly_summary(self):
        self.expanded_months.clear()
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if isinstance(w, MonthSummaryWidget):
                if w.is_detail_loaded and w.detail_frame.isVisible():
                    self.expanded_months.add(w.month_str)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        months_info = self.db.fetch_all_months_with_stats_by_category(self.category_name)
        for m_info in months_info:
            widget = MonthSummaryWidget(m_info, db=self.db, parent=self.scroll_widget,
                                        forced_category=self.category_name)
            self.scroll_layout.addWidget(widget)
            if m_info["month"] in self.expanded_months:
                widget.toggle_detail()

    def add_record(self):
        if self.delete_mode:
            return
        dialog = AddExpenseDialog(self)
        index = dialog.category_combo.findText(self.category_name)
        if index >= 0:
            dialog.category_combo.setCurrentIndex(index)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            data["category"] = self.category_name
            self.db.insert_pay_data(data)
            self.load_monthly_summary()

    def toggle_delete_mode(self):
        self.delete_mode = not self.delete_mode
        self.btn_add.setEnabled(not self.delete_mode)
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if w and hasattr(w, "detail_cards"):
                for card in w.detail_cards:
                    card.show_delete_button(self.delete_mode)

    def showEvent(self, event):
        self.load_monthly_summary()
        super().showEvent(event)
