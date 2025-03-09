import unittest
import json
import http.client
import threading
import time
from pathlib import Path
import sys
from urllib.parse import quote  # URLエンコード用に追加

# プロジェクトルートへのパスを追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from db.db_server import run_server
from db.db_initialize import initialize_database

class TestDBServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """テストクラスの前処理"""
        print("\nサーバーを起動します...")
        # データベースの初期化
        initialize_database()
        # サーバーを別スレッドで起動
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
        # サーバーの起動を待機
        time.sleep(1)
        print("サーバーの起動完了")

    def setUp(self):
        """各テストメソッドの前処理"""
        print("\n" + "="*50)
        self.conn = http.client.HTTPConnection("localhost", 8000)

    def tearDown(self):
        """各テストメソッドの後処理"""
        self.conn.close()
        print("="*50)

    def test_select_all(self):
        """select_all エンドポイントのテスト"""
        print("テスト: 全商品の取得 (GET /select_all)")
        print("期待する挙動: ステータスコード200で全商品データが返却されること")

        self.conn.request("GET", "/select_all")
        response = self.conn.getresponse()
        data = json.loads(response.read().decode())

        print(f"実際の挙動: ステータスコード {response.status}")
        print(f"取得データ: {data}")

        self.assertEqual(response.status, 200)
        self.assertIn('products', data)
        self.assertGreater(len(data['products']), 0)

    def test_select(self):
        """select エンドポイントのテスト"""
        print("テスト: 条件付き商品の取得 (GET /select)")
        print("期待する挙動: ノートパソコンの情報が1件取得できること")

        # パラメータをURLエンコード
        encoded_name = quote("ノートパソコン")
        self.conn.request("GET", f"/select?name={encoded_name}")
        response = self.conn.getresponse()
        data = json.loads(response.read().decode())

        print(f"実際の挙動: ステータスコード {response.status}")
        print(f"取得データ: {data}")

        self.assertEqual(response.status, 200)
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0][1], "ノートパソコン")

    def test_insert(self):
        """insert エンドポイントのテスト"""
        print("テスト: 新規商品の追加 (POST /insert)")
        print("期待する挙動: 新商品が追加され、成功メッセージが返却されること")

        new_product = {
            "name": "テスト商品",
            "price": 1500,
            "description": "テスト用の商品です",
            "stock": 10
        }
        headers = {'Content-Type': 'application/json'}
        self.conn.request("POST", "/insert", 
                         json.dumps(new_product).encode(),
                         headers)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode())

        print(f"実際の挙動: ステータスコード {response.status}")
        print(f"レスポンス: {data}")

        self.assertEqual(response.status, 200)
        self.assertIn('message', data)

    def test_update(self):
        """update エンドポイントのテスト"""
        print("テスト: 商品情報の更新 (PUT /update)")
        print("期待する挙動: 商品情報が更新され、成功メッセージが返却されること")

        update_data = {
            "conditions": {"name": "ノートパソコン"},
            "stock": 5
        }
        headers = {'Content-Type': 'application/json'}
        self.conn.request("PUT", "/update", 
                         json.dumps(update_data).encode(),
                         headers)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode())

        print(f"実際の挙動: ステータスコード {response.status}")
        print(f"レスポンス: {data}")

        self.assertEqual(response.status, 200)
        self.assertIn('message', data)

    def test_delete(self):
        """delete エンドポイントのテスト"""
        print("テスト: 商品の削除 (DELETE /delete)")
        print("期待する挙動: 指定した商品が削除され、成功メッセージが返却されること")

        # まず新しい商品を追加
        new_product = {
            "name": "削除用商品",
            "price": 1000,
            "description": "削除予定の商品です",
            "stock": 1
        }
        headers = {'Content-Type': 'application/json'}
        self.conn.request("POST", "/insert", 
                         json.dumps(new_product).encode(),
                         headers)
        self.conn.getresponse().read()

        # 追加した商品を削除
        delete_data = {"name": "削除用商品"}
        self.conn.request("DELETE", "/delete", 
                         json.dumps(delete_data).encode(),
                         headers)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode())

        print(f"実際の挙動: ステータスコード {response.status}")
        print(f"レスポンス: {data}")

        self.assertEqual(response.status, 200)
        self.assertIn('message', data)

    # def test_error_handling(self):
    #     """エラーハンドリングのテスト"""
    #     print("テスト: エラー処理")
    #     print("期待する挙動: 不正なリクエストに対して適切なエラーレスポンスが返却されること")

    #     print("\nケース1: 存在しないエンドポイントへのアクセス")
    #     self.conn.request("GET", "/non_existent")
    #     response = self.conn.getresponse()
    #     data = json.loads(response.read().decode())
    #     print(f"実際の挙動: ステータスコード {response.status}")
    #     print(f"レスポンス: {data}")
    #     self.assertEqual(response.status, 404)

    #     print("\nケース2: 不正なJSONデータでのPOSTリクエスト")
    #     headers = {'Content-Type': 'application/json'}
    #     self.conn.request("POST", "/insert", 
    #                      "invalid json".encode(),
    #                      headers)
    #     response = self.conn.getresponse()
    #     data = response.read().decode()
    #     print(f"実際の挙動: ステータスコード {response.status}")
    #     self.assertNotEqual(response.status, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)
