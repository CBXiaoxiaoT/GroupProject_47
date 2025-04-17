from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QStackedWidget, QLabel, QScrollArea, QButtonGroup, \
    QVBoxLayout, QDialog, QMessageBox
from Exp_Dialogs import CategoryEditDialog
from Exp_Pages import TodayPage, AllPage, SummaryPage, CategoryFilterPage
from Exp_Widgets import CategoryButton
from Expdb_manager import ExpDBManager
from UIDesign import UIDesign  # 引入 UI 统一配置

class ExpenditurePage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setFixedSize(1000, 600)
        self.central_widget = QWidget(self)
        self.central_widget.setGeometry(0, 20, 1000, 600)
        self.setCentralWidget(self.central_widget)

        # 左侧面板
        self.left_panel = QWidget(self.central_widget)
        self.left_panel.setGeometry(0, 10, 180, 530)
        self.left_panel.setStyleSheet(UIDesign.EXP_LEFT_PANEL_BG)

        # 顶部 3 个按钮
        self.Today_btn = QPushButton("Today", self.left_panel)
        self.Today_btn.setGeometry(10, 20, 160, 40)
        self.Today_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.All_btn = QPushButton("All", self.left_panel)
        self.All_btn.setGeometry(10, 70, 160, 40)
        self.All_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.Summary_btn = QPushButton("Summary", self.left_panel)
        self.Summary_btn.setGeometry(10, 120, 160, 40)
        self.Summary_btn.setStyleSheet(UIDesign.TOP_BUTTON_STYLE)
        self.leftButtonGroup = QButtonGroup(self)
        self.leftButtonGroup.setExclusive(True)
        self.leftButtonGroup.addButton(self.Today_btn)
        self.leftButtonGroup.addButton(self.All_btn)
        self.leftButtonGroup.addButton(self.Summary_btn)

        # Category 标签及编辑按钮
        self.cat_label = QLabel("Category", self.left_panel)
        self.cat_label.setGeometry(10, 200, 160, 30)
        self.cat_label.setStyleSheet(UIDesign.EXP_CATEGORY_LABEL_STYLE)
        self.cat_add_btn = QPushButton("Add", self.left_panel)
        self.cat_add_btn.setGeometry(10, 230, 70, 30)
        self.cat_add_btn.setStyleSheet(UIDesign.EXP_ADD_BUTTON_STYLE)
        self.cat_add_btn.clicked.connect(self.open_add_category_dialog)
        self.cat_delete_btn = QPushButton("Delete", self.left_panel)
        self.cat_delete_btn.setGeometry(90, 230, 70, 30)
        self.cat_delete_btn.setStyleSheet(UIDesign.EXP_DELETE_BUTTON_STYLE)
        self.cat_delete_btn.clicked.connect(self.toggle_category_delete_mode)

        # QScrollArea 显示类别列表
        self.category_scroll = QScrollArea(self.left_panel)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setGeometry(0, 270, 180, 250)
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setStyleSheet(UIDesign.EXP_CATEGORY_SCROLL_STYLE)
        self.category_widget = QWidget()
        self.category_layout = QVBoxLayout(self.category_widget)
        self.category_layout.setSpacing(5)
        self.category_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.category_scroll.setWidget(self.category_widget)
        self.category_delete_mode = False
        self.db = ExpDBManager()
        self.load_categories()

        # 记录所有“分类筛选”页面的引用：{cat_id: CategoryFilterPage实例}
        self.category_pages = {}

        # 右侧 QStackedWidget
        self.pages_widget = QStackedWidget(self.central_widget)
        self.pages_widget.setGeometry(180, 10, 820, 530)
        self.pages_widget.setStyleSheet(UIDesign.EXP_PAGES_WIDGET_STYLE)
        self.Today_page = TodayPage()
        self.pages_widget.addWidget(self.Today_page)
        self.All_page = AllPage()
        self.pages_widget.addWidget(self.All_page)
        self.Summary_page = SummaryPage()
        self.pages_widget.addWidget(self.Summary_page)
        self.Today_btn.clicked.connect(lambda: self.pages_widget.setCurrentIndex(0))
        self.All_btn.clicked.connect(lambda: self.pages_widget.setCurrentIndex(1))
        self.Summary_btn.clicked.connect(lambda: self.pages_widget.setCurrentIndex(2))

    def toggle_category_delete_mode(self):
        self.category_delete_mode = not self.category_delete_mode
        self.cat_add_btn.setEnabled(not self.category_delete_mode)
        for i in range(self.category_layout.count()):
            w = self.category_layout.itemAt(i).widget()
            if hasattr(w, "show_delete_button"):
                w.show_delete_button(self.category_delete_mode)

    def open_add_category_dialog(self):
        # first check if there are 20 categories
        # user can only add 20 categories
        current_count = self.category_layout.count()
        if current_count >= 20:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Attention!", "You can't add more than 20 categories.")
            return

        dialog = CategoryEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cat_name = dialog.get_category_name()
            if cat_name:
                try:
                    self.db.insert_category(cat_name)
                    self.load_categories()
                #in case there is duplicated categories
                except ValueError as e:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Duplicate", str(e))

    def load_categories(self):
        for i in reversed(range(self.category_layout.count())):
            w = self.category_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)
        categories = self.db.get_categories()
        for cat in categories:
            btn = CategoryButton(
                cat_id=cat["id"],
                cat_name=cat["category"],
                delete_callback=self.delete_category,
                filter_callback=self.on_category_clicked,
                parent=self.category_widget
            )
            btn.show_delete_button(self.category_delete_mode)
            self.category_layout.addWidget(btn)

    def on_category_clicked(self, cat_id, cat_name):
        if cat_id in self.category_pages:
            self.pages_widget.setCurrentWidget(self.category_pages[cat_id])
            return
        page = CategoryFilterPage(cat_name, self.db, parent=self.pages_widget)
        self.category_pages[cat_id] = page
        self.pages_widget.addWidget(page)
        self.pages_widget.setCurrentWidget(page)

    def delete_category(self, category_id: int):
        # first check if there are datas
        categories = self.db.get_categories()
        category_name = None
        for cat in categories:
            if cat["id"] == category_id:
                category_name = cat["category"]
                break
        if not category_name:
            return

        # check if there are records
        records = self.db.fetch_pay_data_by_category(category_name)
        if records:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Can not delete.", "There are datas in this category, please manage them first！")
            return

        # No data, then delete
        self.db.delete_category(category_id)
        self.load_categories()
