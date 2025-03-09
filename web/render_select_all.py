import http.client
import json
import html
from pathlib import Path

def get_template(template_name):
    """テンプレートファイルを読み込む"""
    template_path = Path(__file__).parent / "templates" / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def get_products_from_api():
    """DBサーバーから商品情報を取得"""
    try:
        conn = http.client.HTTPConnection("localhost", 8000)
        conn.request("GET", "/select_all")
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        return data.get('products', [])
    except Exception as e:
        print(f"APIエラー: {e}")
        return []
    finally:
        conn.close()

def create_product_rows(products):
    """商品一覧のHTML行を生成"""
    rows = []
    for product in products:
        row = f"""
        <tr>
            <td>{html.escape(str(product[0]))}</td>
            <td><a href="/product/{product[0]}">{html.escape(product[1])}</a></td>
            <td>{html.escape(str(product[2]))}</td>
            <td>{html.escape(product[3])}</td>
            <td>{html.escape(str(product[4]))}</td>
        </tr>
        """
        rows.append(row)
    return "\n".join(rows)

def render_products_page():
    """商品一覧ページのHTMLを生成"""
    products = get_products_from_api()
    template = get_template("products.html")
    product_rows = create_product_rows(products)
    return template.replace("{products}", product_rows)
