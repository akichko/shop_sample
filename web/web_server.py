from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import uuid
from pathlib import Path
from render_select_all import render_products_page
import re
import http.client
import json
import html  # htmlモジュールを追加

# セッション管理（実際のアプリケーションではデータベースやRedisなどを使用すべき）
sessions = {}

# テスト用ユーザー（実際のアプリケーションではデータベースで管理すべき）
USERS = {
    "admin": "password123"
}

class WebHandler(BaseHTTPRequestHandler):
    def get_template(self, template_name):
        """テンプレートファイルを読み込む"""
        template_path = Path(__file__).parent / "templates" / template_name
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def apply_template(self, template, **kwargs):
        """テンプレートに値を適用"""
        for key, value in kwargs.items():
            template = template.replace('{{' + key + '}}', str(value))
        return template

    def check_session(self):
        """セッションの確認"""
        cookie = self.headers.get('Cookie')
        if cookie:
            for c in cookie.split(';'):
                if c.strip().startswith('session='):
                    session_id = c.split('=')[1].strip()
                    return session_id in sessions
        return False

    def get_product_from_api(self, product_id):
        """DBサーバーから特定の商品情報を取得"""
        try:
            conn = http.client.HTTPConnection("localhost", 8000)
            conn.request("GET", f"/select?id={product_id}")
            response = conn.getresponse()
            data = json.loads(response.read().decode())
            if data.get('products'):
                return data['products'][0]
            return None
        except Exception as e:
            print(f"APIエラー: {e}")
            return None
        finally:
            conn.close()

    def do_GET(self):
        """GETリクエストの処理"""
        path = urlparse(self.path).path

        # 商品詳細ページのパスパターンをチェック
        product_match = re.match(r'/product/(\d+)', path)
        
        if path == '/':
            # ログインチェック
            if self.check_session():
                # 既にログインしている場合は商品一覧へリダイレクト
                self.send_response(302)
                self.send_header('Location', '/products')
                self.end_headers()
                return

            # ログインページの表示
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            template = self.get_template("login.html")
            self.wfile.write(template.encode())

        elif path == '/products':
            # ログインチェック
            if not self.check_session():
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return

            # 商品一覧ページの表示
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html_content = render_products_page()
            self.wfile.write(html_content.encode())

        elif path == '/logout':
            # ログアウト処理
            cookie = self.headers.get('Cookie')
            if cookie:
                for c in cookie.split(';'):
                    if c.strip().startswith('session='):
                        session_id = c.split('=')[1].strip()
                        if session_id in sessions:
                            del sessions[session_id]

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

        elif product_match:
            # 商品詳細ページの表示
            if not self.check_session():
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return

            product_id = product_match.group(1)
            product = self.get_product_from_api(product_id)
            
            if product:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                template = self.get_template("product_detail.html")
                html_content = self.apply_template(
                    template,
                    id=product[0],
                    name=html.escape(product[1]),
                    price=html.escape(str(product[2])),
                    description=html.escape(product[3]),
                    stock=html.escape(str(product[4]))
                )
                self.wfile.write(html_content.encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write("商品が見つかりません".encode())

    def do_POST(self):
        """POSTリクエストの処理"""
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)

            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            # 認証チェック
            if username in USERS and USERS[username] == password:
                # セッションの作成
                session_id = str(uuid.uuid4())
                sessions[session_id] = username

                self.send_response(302)
                self.send_header('Set-Cookie', f'session={session_id}')
                self.send_header('Location', '/products')
                self.end_headers()
            else:
                # 認証失敗
                self.send_response(401)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write("認証に失敗しました".encode())

        elif self.path == '/add_to_cart':
            if not self.check_session():
                self.send_response(401)
                self.end_headers()
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            product_id = params.get('product_id', [''])[0]

            # ここでカートに商品を追加する処理を実装
            # （現在は仮の実装）
            self.send_response(302)
            self.send_header('Location', f'/product/{product_id}')
            self.end_headers()

def run_web_server(port=8001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, WebHandler)
    print(f'Starting web server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_web_server()
