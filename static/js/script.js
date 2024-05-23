document.addEventListener("DOMContentLoaded", () => {
    getGoods();
    getUsers();
    getOrders();
    document.getElementById("client-select").addEventListener("change", checkCart);
});

async function getGoods() {
    const response = await fetch("/products");
    const products = await response.json();
    const productSelect = document.getElementById("product-select");
    const productList = document.getElementById("product-list");
    productList.innerHTML = "";
    productSelect.innerHTML = '<option value="" disabled selected>Choose the goods</option>';

    products.forEach(product => {
        const option = document.createElement("option");
        option.value = product.id;
        option.textContent = product.name;
        productSelect.appendChild(option);

        const li = document.createElement("li");
        li.textContent = `${product.name} - $${product.price.toFixed(2)}`;
        productList.appendChild(li);
    });
}

async function getUsers() {
    const response = await fetch("/clients");
    const clients = await response.json();
    const clientSelect = document.getElementById("client-select");
    const clientList = document.getElementById("client-list");
    clientList.innerHTML = "";
    clientSelect.innerHTML = '<option value="" disabled selected>Choose the user</option>';

    clients.forEach(client => {
        const option = document.createElement("option");
        option.value = client.id;
        option.textContent = client.name;
        clientSelect.appendChild(option);

        const li = document.createElement("li");
        li.textContent = `${client.name} (${client.email})`;
        clientList.appendChild(li);
    });
}

async function getOrders() {
    const response = await fetch("/orders");
    const orders = await response.json();
    const orderList = document.getElementById("order-list");
    orderList.innerHTML = "";

    orders.forEach(order => {
        const li = document.createElement("li");
        li.textContent = `Order #${order.id} - Total: $${order.total.toFixed(2)}`;
        orderList.appendChild(li);
    });
}

async function addUser() {
    const name = document.getElementById("client-name-input").value;
    const email = document.getElementById("client-email-input").value;

    if (name && email) {
        await fetch("/clients", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email })
        });
        document.getElementById("client-name-input").value = "";
        document.getElementById("client-email-input").value = "";
        getUsers();
    } else {
        alert("Please enter valid client details.");
    }
}

async function addGoods() {
    const name = document.getElementById("product-name-input").value;
    const price = parseFloat(document.getElementById("product-price-input").value);

    if (name && !isNaN(price)) {
        await fetch("/products", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, price })
        });
        document.getElementById("product-name-input").value = "";
        document.getElementById("product-price-input").value = "";
        getGoods();
    } else {
        alert("Please enter valid product details.");
    }
}

async function checkCart() {
    const clientSelect = document.getElementById("client-select");
    const clientId = parseInt(clientSelect.value);

    if (!isNaN(clientId)) {
        const response = await fetch(`/clients/${clientId}/cart`);
        const cartItems = await response.json();
        const cartList = document.getElementById("cart-list");
        cartList.innerHTML = "";

        cartItems.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.name} - $${item.price.toFixed(2)}`;
            cartList.appendChild(li);
        });
    }
}

async function addToCart() {
    const clientSelect = document.getElementById("client-select");
    const productSelect = document.getElementById("product-select");
    const clientId = parseInt(clientSelect.value);
    const productId = parseInt(productSelect.value);

    if (!isNaN(clientId) && !isNaN(productId)) {
        await fetch(`/clients/${clientId}/cart`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId })
        });
        checkCart();
    } else {
        alert("Please select a client and a product.");
    }
}

async function checkout() {
    const clientSelect = document.getElementById("client-select");
    const clientId = parseInt(clientSelect.value);

    if (!isNaN(clientId)) {
        await fetch(`/clients/${clientId}/checkout`, {
            method: "POST"
        });
        checkCart();
        getOrders();
    } else {
        alert("Please select a client.");
    }
}
