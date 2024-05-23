from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ProductItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='product_item', lazy=True)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    cart_items = db.relationship('CartProduct', backref='client', lazy=True)
    orders = db.relationship('Order', backref='client', lazy=True)

class CartProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_item.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product_item.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

ProductItem.to_dict = model_to_dict
Client.to_dict = model_to_dict
Order.to_dict = model_to_dict

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def list_products():
    products = ProductItem.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = ProductItem(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201

@app.route('/clients', methods=['GET'])
def list_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@app.route('/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    new_client = Client(name=data['name'], email=data['email'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

@app.route('/clients/<int:client_id>/cart', methods=['POST'])
def add_to_client_cart(client_id):
    data = request.get_json()
    product_id = data['product_id']
    client = Client.query.get(client_id)
    product = ProductItem.query.get(product_id)
    
    if not client or not product:
        return jsonify({'error': 'Client or product not found'}), 404

    cart_item = CartProduct(client_id=client_id, product_id=product_id)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify(cart_item.client.to_dict()), 201

@app.route('/clients/<int:client_id>/cart', methods=['GET'])
def view_client_cart(client_id):
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    cart_items = CartProduct.query.filter_by(client_id=client_id).all()
    products = [ProductItem.query.get(item.product_id).to_dict() for item in cart_items]
    return jsonify(products)

@app.route('/clients/<int:client_id>/checkout', methods=['POST'])
def checkout_client_cart(client_id):
    client = Client.query.get(client_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    cart_items = CartProduct.query.filter_by(client_id=client_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total = sum(ProductItem.query.get(item.product_id).price for item in cart_items)
    new_order = Order(client_id=client_id, total=total)
    db.session.add(new_order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, price=ProductItem.query.get(item.product_id).price)
        db.session.add(order_item)
        db.session.delete(item)
    db.session.commit()

    return jsonify(new_order.to_dict()), 201

@app.route('/orders', methods=['GET'])
def list_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

if __name__ == '__main__':
    app.run(debug=True)
