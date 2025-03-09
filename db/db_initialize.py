import sqlite3
from pathlib import Path
import os

def initialize_database():
    # データベースファイルのパスを設定
    db_path = Path(__file__).parent / "shop.db"
    
    # 既存のDBファイルがあれば削除
    if db_path.exists():
        os.remove(db_path)
        print("既存のデータベースファイルを削除しました。")

    try:
        # データベースに接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 商品テーブルの作成
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT,
            stock INTEGER NOT NULL DEFAULT 0
        )
        ''')

        # サンプルデータの準備
        sample_products = [
            ('ノートパソコン', 89800, 'Core i5搭載の高性能ノートPC', 10),
            ('ワイヤレスマウス', 2980, 'Bluetooth対応ワイヤレスマウス', 50),
            ('キーボード', 4980, 'メカニカルキーボード', 30),
            ('モニター', 19800, '23.8インチフルHDディスプレイ', 15),
            ('USBメモリ', 1980, '32GB USB3.0対応', 100)
        ]

        # サンプルデータの挿入
        cursor.executemany('''
        INSERT INTO products (name, price, description, stock)
        VALUES (?, ?, ?, ?)
        ''', sample_products)

        # 変更を確定
        conn.commit()
        print("データベースの初期化が完了しました。")

    except sqlite3.Error as e:
        print(f"エラーが発生しました: {e}")
    
    finally:
        # 接続を閉じる
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
