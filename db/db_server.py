from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from db_access import DatabaseAccess  # 相対インポートに変更

class DBHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET リクエストの処理 (select_all, select)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path.strip('/')
        
        if path == 'select_all':
            self._handle_select_all()
        elif path == 'select':
            params = parse_qs(parsed_path.query)
            conditions = {k: v[0] for k, v in params.items()}
            self._handle_select(conditions)
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """POST リクエストの処理 (insert)"""
        if self.path.strip('/') == 'insert':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self._handle_insert(data)
        else:
            self._send_error(404, "Not Found")

    def do_PUT(self):
        """PUT リクエストの処理 (update)"""
        if self.path.strip('/') == 'update':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self._handle_update(data)
        else:
            self._send_error(404, "Not Found")

    def do_DELETE(self):
        """DELETE リクエストの処理 (delete)"""
        if self.path.strip('/') == 'delete':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self._handle_delete(data)
        else:
            self._send_error(404, "Not Found")

    def _send_response_json(self, data, status=200):
        """JSON形式でレスポンスを返す"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error(self, status, message):
        """エラーレスポンスを返す"""
        self._send_response_json({'error': message}, status)

    def _handle_select_all(self):
        """全件取得の処理"""
        with DatabaseAccess() as db:
            results = db.select_all('products')
            self._send_response_json({'products': results})

    def _handle_select(self, conditions):
        """条件付き取得の処理"""
        with DatabaseAccess() as db:
            results = db.select('products', conditions)
            self._send_response_json({'products': results})

    def _handle_insert(self, data):
        """データ挿入の処理"""
        with DatabaseAccess() as db:
            success = db.insert('products', data)
            if success:
                self._send_response_json({'message': '商品を追加しました'})
            else:
                self._send_error(500, '商品の追加に失敗しました')

    def _handle_update(self, data):
        """データ更新の処理"""
        conditions = data.pop('conditions', {})
        with DatabaseAccess() as db:
            success = db.update('products', data, conditions)
            if success:
                self._send_response_json({'message': '商品を更新しました'})
            else:
                self._send_error(500, '商品の更新に失敗しました')

    def _handle_delete(self, conditions):
        """データ削除の処理"""
        with DatabaseAccess() as db:
            success = db.delete('products', conditions)
            if success:
                self._send_response_json({'message': '商品を削除しました'})
            else:
                self._send_error(500, '商品の削除に失敗しました')

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DBHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
