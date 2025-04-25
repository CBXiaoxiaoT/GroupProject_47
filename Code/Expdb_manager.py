import sqlite3
import os
import sys
from typing import List, Dict

DB_NAME = "expenses.db"  # database name

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ExpDBManager:
    def __init__(self):
        db_path = get_resource_path(DB_NAME)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS pay_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                time TEXT,
                method TEXT,
                amount REAL,
                category TEXT,
                payerOrPayee TEXT,
                comment TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS Budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                budget REAL
            )
        """)

        # Categories Table, store the information and button
        c.execute("""
                    CREATE TABLE IF NOT EXISTS Categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT UNIQUE
                    )
                """)


        # insert initial category data（only the original is empty）
        c.execute("SELECT COUNT(*) FROM Categories")
        count = c.fetchone()[0]
        if count == 0:
            initial_cats = [("Work",), ("Food",), ("Study",), ("Entertainment",)]
            c.executemany("INSERT INTO Categories (category) VALUES (?)", initial_cats)
        self.conn.commit()

    def insert_pay_data(self, data: Dict) -> int:
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO pay_data (date, time, method, amount, category, payerOrPayee, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["date"],
            data["time"],
            data["method"],
            round(float(data["amount"]),2),
            data["category"],
            data["payee"],
            data["comment"]
        ))
        self.conn.commit()
        return c.lastrowid

    def update_pay_data(self, record_id: int, data: Dict):
        c = self.conn.cursor()
        c.execute("""
            UPDATE pay_data
            SET date = ?, time = ?, method = ?, amount = ?, category = ?, payerOrPayee = ?, comment = ?
            WHERE id = ?
        """, (
            data["date"],
            data["time"],
            data["method"],
            float(data["amount"]),
            data["category"],
            data["payee"],
            data["comment"],
            record_id
        ))
        self.conn.commit()

    def delete_pay_data(self, record_id: int):
        c = self.conn.cursor()
        c.execute("DELETE FROM pay_data WHERE id = ?", (record_id,))
        self.conn.commit()

    def fetch_all_months_with_stats_by_category(self, category: str) -> List[dict]:
        c = self.conn.cursor()
        c.execute("""
            SELECT substr(date, 1, 7) AS month,
                   SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
                   ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS total_expense
            FROM pay_data
            WHERE category = ?
            GROUP BY substr(date, 1, 7)
            ORDER BY month DESC
        """, (category,))
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "month": row["month"],
                "income": row["total_income"] or 0,
                "expense": row["total_expense"] or 0
            })
        return result

    def fetch_pay_data_by_date(self, date: str) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("""
            SELECT id, date, time, method, amount, category, payerOrPayee, comment
            FROM pay_data
            WHERE date = ?
            ORDER BY time ASC
        """, (date,))
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "date": row["date"],
                "time": row["time"],
                "method": row["method"],
                "amount": str(row["amount"]),
                "category": row["category"],
                "payee": row["payerOrPayee"],
                "comment": row["comment"]
            })
        return result

    def get_daily_statistics(self, date: str) -> Dict:
        c = self.conn.cursor()
        c.execute("""
            SELECT
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS total_expense
            FROM pay_data
            WHERE date = ?
        """, (date,))
        row = c.fetchone()
        return {
            "income": row["total_income"] if row["total_income"] is not None else 0,
            "expense": abs(row["total_expense"]) if row["total_expense"] is not None else 0
        }

    def get_monthly_statistics(self, month: str) -> Dict:
        c = self.conn.cursor()
        c.execute("""
            SELECT
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS total_expense
            FROM pay_data
            WHERE date LIKE ?
        """, (month + "%",))
        row = c.fetchone()
        return {
            "income": row["total_income"] if row["total_income"] is not None else 0,
            "expense": abs(row["total_expense"]) if row["total_expense"] is not None else 0
        }

    def get_budget_for_month(self, month: str) -> float:
        first_day = month + "-01"
        c = self.conn.cursor()
        c.execute("SELECT budget FROM Budget WHERE date = ? ORDER BY id DESC LIMIT 1", (first_day,))
        row = c.fetchone()
        if row:
            return float(row["budget"])
        return 0.0

    def set_budget_for_month(self, month: str, budget: float):
        first_day = month + "-01"
        c = self.conn.cursor()
        c.execute("SELECT id FROM Budget WHERE date = ?", (first_day,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE Budget SET budget = ? WHERE id = ?", (budget, row["id"]))
        else:
            c.execute("INSERT INTO Budget (date, budget) VALUES (?, ?)", (first_day, budget))
        self.conn.commit()

    def delete_old_pay_data(self, cutoff_date: str):
        c = self.conn.cursor()
        c.execute("DELETE FROM pay_data WHERE date < ?", (cutoff_date,))
        self.conn.commit()

    def fetch_all_months_with_stats(self) -> List[dict]:
        """
        return like：
        [
          {"month": "2025-01", "income": 500, "expense": 300},
          {"month": "2025-02", "income": 1000, "expense": 700},
          ...
        ]
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT substr(date, 1, 7) AS month,
                   SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
                   ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS total_expense
            FROM pay_data
            GROUP BY substr(date, 1, 7)
            ORDER BY month DESC
        """)
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "month": row["month"],  # "yyyy-MM"
                "income": row["total_income"] or 0,  # avoid None
                "expense": row["total_expense"] or 0
            })
        return result

    def fetch_pay_data_by_category(self, category_name: str):
        c = self.conn.cursor()
        c.execute("""
            SELECT id, date, time, method, amount, category, payerOrPayee, comment
            FROM pay_data
            WHERE category = ?
            ORDER BY date DESC, time DESC
        """, (category_name,))
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "date": row["date"],
                "time": row["time"],
                "method": row["method"],
                "amount": str(row["amount"]),
                "category": row["category"],
                "payee": row["payerOrPayee"],
                "comment": row["comment"]
            })
        return result

    def fetch_pay_data_by_month(self, month_str: str) -> List[Dict]:
        """
        month_str like "2025-03"
        return all data this month
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT id, date, time, method, amount, category, payerOrPayee, comment
            FROM pay_data
            WHERE date LIKE ?
            ORDER BY date ASC, time ASC
        """, (month_str + "%",))
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "date": row["date"],
                "time": row["time"],
                "method": row["method"],
                "amount": str(row["amount"]),
                "category": row["category"],
                "payee": row["payerOrPayee"],
                "comment": row["comment"]
            })
        return result

    def fetch_pay_data_by_month_and_category(self, month_str: str, category: str) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("""
            SELECT id, date, time, method, amount, category, payerOrPayee, comment
            FROM pay_data
            WHERE date LIKE ? AND category = ?
            ORDER BY date ASC, time ASC
        """, (month_str + "%", category))
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "date": row["date"],
                "time": row["time"],
                "method": row["method"],
                "amount": str(row["amount"]),
                "category": row["category"],
                "payee": row["payerOrPayee"],
                "comment": row["comment"]
            })
        return result

    def get_categories(self) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT id, category FROM Categories ORDER BY id ASC")
        rows = c.fetchall()
        return [{"id": row["id"], "category": row["category"]} for row in rows]

    def insert_category(self, category: str) -> int:
        c = self.conn.cursor()
        # check duplicated elements
        c.execute("SELECT id FROM Categories WHERE lower(category) = lower(?)", (category,))
        existing = c.fetchone()
        if existing is not None:
            # if there have, then value
            raise ValueError("Category already exists.")
        c.execute("INSERT INTO Categories (category) VALUES (?)", (category,))
        self.conn.commit()
        return c.lastrowid

    def delete_category(self, category_id: int):
        c = self.conn.cursor()
        c.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
        self.conn.commit()

    def get_category_net_by_month(self, month_str: str):
        """
        return a list, show this month's total net (expense + income)
        like：[
          {"category": "Work", "net": -500.0},
          {"category": "Study", "net": 100.0},
          ...
        ]
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT category, SUM(amount) as net
            FROM pay_data
            WHERE date LIKE ?
            GROUP BY category
        """, (month_str + "%",))
        rows = c.fetchall()
        result = []
        for r in rows:
            cat = r["category"]
            net_val = r["net"] if r["net"] else 0
            result.append({"category": cat, "net": float(net_val)})
        return result

    def get_category_net_by_year(self, year_str: str):
        """
        return a list, show this year's total net (expense + income)
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT category, SUM(amount) as net
            FROM pay_data
            WHERE substr(date,1,4) = ?
            GROUP BY category
        """, (year_str,))
        rows = c.fetchall()
        result = []
        for r in rows:
            cat = r["category"]
            net_val = r["net"] if r["net"] else 0
            result.append({"category": cat, "net": float(net_val)})
        return result

    def get_expense_by_category_by_month(self, month_str: str):
        """
        return a list, show this month's expense(<0) by category, and get its absolute value

        like[{"category": "Food", "expense": 200.0}, {"category": "Study", "expense": 150.0}, ...]
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT category, ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS expense
            FROM pay_data
            WHERE date LIKE ?
            GROUP BY category
        """, (month_str + "%",))
        rows = c.fetchall()
        result = []
        for r in rows:
            if r["expense"] is not None and r["expense"] > 0:
                result.append({"category": r["category"], "expense": float(r["expense"])})
        return result

    def get_expense_by_category_by_year(self, year_str: str):
        """
        return a list, show this year's expense(<0) by category, and get its absolute value
        """
        c = self.conn.cursor()
        c.execute("""
            SELECT category, ABS(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END)) AS expense
            FROM pay_data
            WHERE substr(date,1,4) = ?
            GROUP BY category
        """, (year_str,))
        rows = c.fetchall()
        result = []
        for r in rows:
            if r["expense"] is not None and r["expense"] > 0:
                result.append({"category": r["category"], "expense": float(r["expense"])})
        return result

    def get_yearly_statistics(self, year: str) -> dict:
        c = self.conn.cursor()
        c.execute("""
            SELECT
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) AS total_expense
            FROM pay_data
            WHERE substr(date, 1, 4) = ?
        """, (year,))
        row = c.fetchone()
        return {
            "income": row["total_income"] if row["total_income"] is not None else 0,
            "expense": abs(row["total_expense"]) if row["total_expense"] is not None else 0
        }

    def close(self):
        self.conn.close()




