import sqlite3
import os
import sys
from typing import List, Dict

DB_NAME = "ToDoLists.db"  # the datbase name, you can choose your own

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DBManager:
    def __init__(self):
        db_path = get_resource_path(DB_NAME)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        """
        Create the tasks table if it doesn't exist.
        Columns:
          - id: INTEGER PRIMARY KEY AUTOINCREMENT
          - color: TEXT (one of six hex colors)
          - category: TEXT
          - title: TEXT
          - date: TEXT (yyyy-MM-dd)
          - degree: TEXT (Easy/Normal/Hard)
          - description: TEXT
          - collected: INTEGER (0 or 1)
        """
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            category TEXT,
            title TEXT,
            date TEXT,
            degree TEXT,
            description TEXT,
            collected INTEGER
        )
        """
        self.conn.execute(sql)
        self.conn.commit()

    def insert_task(self, data: Dict) -> int:
        """
        Insert a new record and return its auto-incremented id.
        Expects data dict with keys:
          - color
          - category
          - title
          - date
          - degree
          - description
          - collected (0 or 1)
        """
        sql = """
        INSERT INTO tasks (color, category, title, date, degree, description, collected)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cur = self.conn.cursor()
        cur.execute(sql, (
            data["color"],
            data["category"],
            data["title"],
            data["date"],
            data["degree"],
            data["description"],
            data.get("collected", 0),
        ))
        self.conn.commit()
        return cur.lastrowid  # 返回自增ID

    def update_task(self, task_id: int, data: Dict):
        """
        update an existing record by its task_id
        """
        sql = """
        UPDATE tasks
           SET color = ?,
               category = ?,
               title = ?,
               date = ?,
               degree = ?,
               description = ?,
               collected = ?
         WHERE id = ?
        """
        self.conn.execute(sql, (
            data["color"],
            data["category"],
            data["title"],
            data["date"],
            data["degree"],
            data["description"],
            data.get("collected", 0),
            task_id
        ))
        self.conn.commit()

    def delete_task(self, task_id: int):
        """
        delete task
        """
        sql = "DELETE FROM tasks WHERE id = ?"
        self.conn.execute(sql, (task_id,))
        self.conn.commit()

    def fetch_all_tasks(self) -> List[Dict]:
        """
        Fetch all tasks, ordered by date ascending, and return as list of dicts.
        """
        sql = "SELECT * FROM tasks ORDER BY date ASC"
        cur = self.conn.execute(sql)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "color": row["color"],
                "category": row["category"],
                "title": row["title"],
                "date": row["date"],
                "degree": row["degree"],
                "description": row["description"],
                "collected": row["collected"]
            })
        return result

    def close(self):
        self.conn.close()
