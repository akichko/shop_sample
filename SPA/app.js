// ダミーのユーザーデータ
const validUser = {
    username: 'user',
    password: 'pass'
};

// ダミーの商品データ
const products = [
    { id: 1, name: '商品1', price: 1000, image: 'https://via.placeholder.com/150' },
    { id: 2, name: '商品2', price: 2000, image: 'https://via.placeholder.com/150' },
    { id: 3, name: '商品3', price: 3000, image: 'https://via.placeholder.com/150' }
];

// カートの状態管理
let cartItems = [];

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username === validUser.username && password === validUser.password) {
        document.getElementById('login-page').style.display = 'none';
        document.getElementById('products-page').style.display = 'block';
        document.getElementById('cart-button').style.display = 'block';
        displayProducts();
    } else {
        alert('ログイン失敗');
    }
}

function displayProducts() {
    const container = document.getElementById('products-container');
    container.innerHTML = '';

    products.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = 'product-card';
        productElement.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h3 class="product-name" onclick="showProductDetail(${product.id})">${product.name}</h3>
            <p>¥${product.price}</p>
            <button onclick="addToCart(${product.id})">カートに追加</button>
        `;
        container.appendChild(productElement);
    });
}

function showProductDetail(productId) {
    const product = products.find(p => p.id === productId);
    document.getElementById('products-page').style.display = 'none';
    document.getElementById('product-detail-page').style.display = 'block';
    
    const container = document.getElementById('product-detail-container');
    container.innerHTML = `
        <div class="product-detail">
            <img src="${product.image}" alt="${product.name}">
            <h2>${product.name}</h2>
            <p class="price">¥${product.price}</p>
            <p class="description">商品の詳細説明がここに入ります。</p>
            <button onclick="addToCart(${product.id})">カートに追加</button>
        </div>
    `;
}

function backToProducts() {
    document.getElementById('product-detail-page').style.display = 'none';
    document.getElementById('cart-page').style.display = 'none';
    document.getElementById('products-page').style.display = 'block';
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const existingItem = cartItems.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cartItems.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1
        });
    }
    
    updateCartCount();
    alert(`${product.name}をカートに追加しました`);
}

function updateCartCount() {
    const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cart-count').textContent = totalItems;
}

function showCart() {
    document.getElementById('products-page').style.display = 'none';
    document.getElementById('product-detail-page').style.display = 'none';
    document.getElementById('cart-page').style.display = 'block';
    
    const container = document.getElementById('cart-container');
    container.innerHTML = '';
    
    let totalPrice = 0;
    cartItems.forEach(item => {
        const itemTotal = item.price * item.quantity;
        totalPrice += itemTotal;
        
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <span>${item.name}</span>
            <span>数量: ${item.quantity}</span>
            <span>¥${itemTotal}</span>
            <button onclick="removeFromCart(${item.id})">削除</button>
        `;
        container.appendChild(itemElement);
    });
    
    document.getElementById('cart-total').innerHTML = `
        <strong>合計: ¥${totalPrice}</strong>
    `;
}

function removeFromCart(productId) {
    cartItems = cartItems.filter(item => item.id !== productId);
    updateCartCount();
    showCart();
}
