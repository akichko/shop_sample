import unittest
import sys
from pathlib import Path
import os

# プロジェクトルートへのパスを追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from db.db_access import DatabaseAccess
from db.db_initialize import initialize_database

class TestDatabaseAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """テストクラスの前処理"""
        # データベースの初期化
        initialize_database()

    def setUp(self):
        """各テストメソッドの前処理"""
        self.db = DatabaseAccess()
        self.db.__enter__()
        print("\n" + "="*50)  # 区切り線

    def tearDown(self):
        """各テストメソッドの後処理"""
        self.db.__exit__(None, None, None)
        print("="*50)  # 区切り線

    # def test_select_all(self):
    #     """select_all メソッドのテスト"""
    #     print("テスト: 全商品の取得")
    #     print("期待する挙動: 5件の初期データが取得できること")
        
    #     results = self.db.select_all('products')
        
    #     print(f"実際の挙動: {len(results)}件のデータを取得")
    #     print(f"取得データ: {results}")
        
    #     self.assertIsInstance(results, list)
    #     self.assertGreater(len(results), 0)
    #     # 初期データが5件あることを確認
    #     self.assertEqual(len(results), 5)

    def test_select(self):
        """select メソッドのテスト"""
        print("テスト: 条件付き商品の取得")
        print("期待する挙動: 'ノートパソコン'という名前の商品が1件取得できること")
        
        conditions = {"name": "ノートパソコン"}
        results = self.db.select('products', conditions)
        
        print(f"実際の挙動: {len(results)}件のデータを取得")
        print(f"取得データ: {results}")
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "ノートパソコン")

    def test_insert(self):
        """insert メソッドのテスト"""
        print("テスト: 新規商品の追加")
        print("期待する挙動: 新しい商品がデータベースに追加されること")
        
        new_product = {
            "name": "テスト商品",
            "price": 1500,
            "description": "テスト用の商品です",
            "stock": 10
        }
        success = self.db.insert('products', new_product)
        print(f"挿入結果: {'成功' if success else '失敗'}")

        # 挿入されたデータを確認
        conditions = {"name": "テスト商品"}
        results = self.db.select('products', conditions)
        print(f"実際の挙動: 追加した商品を取得 - {results}")
        
        self.assertTrue(success)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "テスト商品")

    def test_update(self):
        """update メソッドのテスト"""
        print("テスト: 商品情報の更新")
        print("期待する挙動: 商品の価格と説明が更新されること")
        
        # まず新しい商品を追加
        new_product = {
            "name": "更新テスト商品",
            "price": 2000,
            "description": "更新前",
            "stock": 5
        }
        self.db.insert('products', new_product)
        print("更新前のデータ:", new_product)

        # データを更新
        conditions = {"name": "更新テスト商品"}
        update_data = {"price": 2500, "description": "更新後"}
        success = self.db.update('products', update_data, conditions)
        
        results = self.db.select('products', conditions)
        print(f"実際の挙動: 更新後のデータ - {results}")
        
        self.assertTrue(success)
        self.assertEqual(results[0][2], 2500)  # price
        self.assertEqual(results[0][3], "更新後")  # description

    def test_delete(self):
        """delete メソッドのテスト"""
        print("テスト: 商品の削除")
        print("期待する挙動: 指定した商品が削除されること")
        
        # まず新しい商品を追加
        new_product = {
            "name": "削除テスト商品",
            "price": 3000,
            "description": "削除予定",
            "stock": 1
        }
        self.db.insert('products', new_product)
        print("削除前の商品データ:", new_product)

        # データを削除
        conditions = {"name": "削除テスト商品"}
        success = self.db.delete('products', conditions)
        
        # 削除されたことを確認
        results = self.db.select('products', conditions)
        print(f"実際の挙動: 削除後の検索結果 - {results}")
        
        self.assertTrue(success)
        self.assertEqual(len(results), 0)

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        print("テスト: エラーハンドリング")
        print("期待する挙動: エラー時に適切に処理されること")
        
        # 存在しないテーブルへのアクセス
        print("\nケース1: 存在しないテーブルへのアクセス")
        results = self.db.select_all('non_existent_table')
        print(f"実際の挙動: {results}")
        self.assertEqual(results, [])

        # 不正なデータでの挿入
        print("\nケース2: 不正なデータでの挿入")
        invalid_data = {"invalid_column": "value"}
        success = self.db.insert('products', invalid_data)
        print(f"実際の挙動: 挿入{'成功' if success else '失敗'}")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main(verbosity=2)
