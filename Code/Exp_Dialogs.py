
from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QTimeEdit, QTextEdit, \
    QMessageBox

from Expdb_manager import ExpDBManager
from UIDesign import UIDesign

class CategoryEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Categories")
        self.setFixedSize(300, 120)
        self.setStyleSheet(UIDesign.DIALOG_STYLE)

        # Label and input text
        self.label_input = QLabel("New Category:", self)
        self.label_input.setGeometry(10, 10, 100, 20)

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(120, 10, 160, 24)
        self.line_edit.setStyleSheet(UIDesign.DIALOG_INPUT_STYLE)
        # limit 15 long
        self.line_edit.setMaxLength(14)

        # Cancel and Confirm
        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.setGeometry(140, 70, 60, 30)
        self.btn_cancel.setStyleSheet(UIDesign.DIALOG_BUTTON_STYLE)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("Confirm", self)
        self.btn_confirm.setGeometry(210, 70, 70, 30)
        self.btn_confirm.setStyleSheet(UIDesign.DIALOG_BUTTON_STYLE)
        self.btn_confirm.clicked.connect(self.on_confirm)

        self.category_name = ""

    def on_confirm(self):
        text = self.line_edit.text().strip()
        if text:
            self.category_name = text
            self.accept()
        else:
            self.reject()

    def get_category_name(self):
        return self.category_name


class AddExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New")
        self.setFixedSize(400, 300)
        self.setStyleSheet(UIDesign.DIALOG_STYLE)

        # Date part
        self.label_date = QLabel("Date:", self)
        self.label_date.setGeometry(10, 10, 50, 20)
        self.date_edit = QDateEdit(self)
        self.date_edit.setGeometry(70, 10, 100, 24)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(UIDesign.DIALOG_BACK)

        # Time part
        self.label_time = QLabel("Time:", self)
        self.label_time.setGeometry(200, 10, 50, 20)
        self.time_edit = QTimeEdit(self)
        self.time_edit.setGeometry(250, 10, 90, 24)
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setStyleSheet(UIDesign.DIALOG_BACK)


        # Method、Amount and Category
        self.label_method = QLabel("Method:", self)
        self.label_method.setGeometry(10, 50, 60, 20)
        # use QComboBox, we can only choose Card or Cash
        self.method_combo = QComboBox(self)
        self.method_combo.setGeometry(70, 50, 100, 24)
        self.method_combo.setStyleSheet(UIDesign.DIALOG_BACK)
        self.method_combo.addItems(["Card", "Cash"])

        self.label_amount = QLabel("Amount:", self)
        self.label_amount.setGeometry(200, 50, 60, 20)
        self.amount_edit = QLineEdit("", self)
        self.amount_edit.setGeometry(260, 50, 80, 24)
        self.amount_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        self.label_pound = QLabel("£", self)
        self.label_pound.setGeometry(345, 53, 50, 20)
        # limit the input, and only 2 decimal
        validator = QDoubleValidator(0, 999999.99, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_edit.setValidator(validator)

        # choose income or expense
        self.type_combo = QComboBox(self)
        self.type_combo.setGeometry(260, 90, 80, 24)
        self.type_combo.setStyleSheet(UIDesign.DIALOG_BACK)
        self.type_combo.addItems(["Income", "Expense"])

        #category
        self.label_category = QLabel("Category:", self)
        self.label_category.setGeometry(10, 90, 70, 20)
        self.category_combo = QComboBox(self)
        self.category_combo.setGeometry(90, 90, 130, 24)
        self.category_combo.setStyleSheet(UIDesign.DIALOG_BACK)
        # load category from database
        temp_db = ExpDBManager()
        categories = temp_db.get_categories()
        for cat in categories:
            self.category_combo.addItem(cat["category"])
        temp_db.close()

        # Payee/Payer and Comment
        self.label_payee = QLabel("Payee/Payer:", self)
        self.label_payee.setGeometry(10, 130, 80, 20)
        self.payee_edit = QLineEdit("Name...", self)
        self.payee_edit.setGeometry(90, 130, 250, 24)
        self.payee_edit.setStyleSheet(UIDesign.DIALOG_BACK)

        self.label_comment = QLabel("Comment:", self)
        self.label_comment.setGeometry(10, 170, 60, 20)
        self.comment_edit = QTextEdit(self)
        self.comment_edit.setGeometry(10, 195, 380, 60)
        self.comment_edit.setStyleSheet(UIDesign.DIALOG_BACK)
        self.comment_edit.setPlainText("Comments...")

        # cancel and confirm 按钮
        self.btn_cancel = QPushButton("cancel", self)
        self.btn_cancel.setGeometry(220, 260, 80, 30)
        self.btn_cancel.setStyleSheet(UIDesign.DIALOG_BACK)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("Confirm", self)
        self.btn_confirm.setGeometry(310, 260, 80, 30)
        self.btn_confirm.setStyleSheet(UIDesign.DIALOG_BACK)
        self.btn_confirm.clicked.connect(self.on_confirm)
        self.btn_confirm.setFocus()



        self.result_data = {}

    def on_confirm(self):
        # check if the amount is numbers!
        amount_str = self.amount_edit.text().strip()
        try:
            amount = float(amount_str)
        except ValueError:
            QMessageBox.warning(self, "Invalid input", "Amount must be numbers!")
            return
        # valid input
        type = self.type_combo.currentText()
        if type == "Income":
            amount = abs(amount)
        else:
            amount = -abs(amount)

        self.result_data = {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "time": self.time_edit.time().toString("HH:mm"),
            "method": self.method_combo.currentText(),
            "amount": amount,
            "category": self.category_combo.currentText(),
            "payee": self.payee_edit.text(),
            "comment": self.comment_edit.toPlainText()
        }
        self.accept()  # return Accepted

    def get_data(self):
        return self.result_data
