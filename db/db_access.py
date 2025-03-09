import sqlite3
from pathlib import Path
from typing import List, Tuple, Any, Optional

class DatabaseAccess:
    def __init__(self):
        self.db_path = Path(__file__).parent / "shop.db"

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def select_all(self, table: str) -> List[Tuple]:
        """テーブルの全レコードを取得"""
        try:
            self.cursor.execute(f"SELECT * FROM {table}")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"選択エラー: {e}")
            return []

    def select(self, table: str, conditions: dict) -> List[Tuple]:
        """条件付きでレコードを取得"""
        try:
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            query = f"SELECT * FROM {table} WHERE {where_clause}"
            self.cursor.execute(query, tuple(conditions.values()))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"選択エラー: {e}")
            return []

    def insert(self, table: str, data: dict) -> bool:
        """新規レコードを挿入"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, tuple(data.values()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"挿入エラー: {e}")
            return False

    def update(self, table: str, data: dict, conditions: dict) -> bool:
        """レコードを更新"""
        try:
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            values = tuple(data.values()) + tuple(conditions.values())
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新エラー: {e}")
            return False

    def delete(self, table: str, conditions: dict) -> bool:
        """レコードを削除"""
        try:
            where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
            query = f"DELETE FROM {table} WHERE {where_clause}"
            self.cursor.execute(query, tuple(conditions.values()))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"削除エラー: {e}")
            return False

# 使用例
if __name__ == "__main__":
    # select_all の例
    with DatabaseAccess() as db:
        products = db.select_all("products")
        print("全商品:", products)

    # select の例
    with DatabaseAccess() as db:
        conditions = {"id": 1}
        product = db.select("products", conditions)
        print("ID=1の商品:", product)

    # insert の例
    with DatabaseAccess() as db:
        new_product = {
            "name": "新商品",
            "price": 1000,
            "description": "新商品の説明",
            "stock": 5
        }
        db.insert("products", new_product)

    # update の例
    with DatabaseAccess() as db:
        update_data = {"stock": 20}
        conditions = {"id": 1}
        db.update("products", update_data, conditions)

    # delete の例
    with DatabaseAccess() as db:
        conditions = {"id": 5}
        db.delete("products", conditions)
