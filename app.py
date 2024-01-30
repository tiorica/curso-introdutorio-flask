from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha_chave_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Modelagem
# User (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)
    cart = db.relationship('CartItem', backref='user', lazy=True)

# Product(id, name, price, description)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Authentication
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  

# Rota raiz
@app.route('/')
def hello_world():
    return 'Oi imundo!'

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({"message": "User logged in"}), 200
    
    return jsonify({"message": "Unauthorized! Invalid credentials."}), 400
    
@app.route('/logout', methods=["POST"])
# @login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out"}), 200 

# Add product route
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"], price=data["price"], description=data.get("description",""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product inserterd in Database"}), 200 
    return jsonify({"message": "Invalid product data"}), 400

# Delete product route
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product removed from database"}), 200
    return jsonify({"message": "Product not found"}), 404

# Get product detail route
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "price": product.price,
            "name": product.name,
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404

# Update product detail route
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
        
    if 'price' in data:
        product.price = data['price']
        
    if 'description' in data:
        product.description = data['description']
    
    db.session.commit()
    return jsonify({"message": "Product updated"})

# Get all products route
@app.route('/api/products', methods=["GET"])
def get_all_products():
    response_product_list = Product.query.all()
    product_list = []
    for product in response_product_list:
        product_data = {
            "id": product.id,
            "name": product.name
        }
        product_list.append(product_data)
    
    return jsonify(product_list)

# Cart routes
@app.route('/api/cart/add/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    user = User.query.get(current_user.id)
    product = Product.query.get(product_id)

    if user and product:
        cart_item = CartItem(user_id=user.id, product_id=product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message":"Item added to the cart"})
    return jsonify({"message":"Failed to add item to the cart"}), 400

@app.route('/api/cart/remove/<int:product_id>', methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from the cart successfully.'})
    return jsonify({'message': 'Failed to remove item from the cart.'}), 400

@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
    user = User.query.get(current_user.id)
    cart_items = user.cart
    cart_content = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        cart_content.append({
            "id": item.id,
            "user_id": item.user_id,
            "product_id": item.product_id,
            "product_name": product.name,
            "product_price": product.price
        })
    return jsonify(cart_content)

@app.route('/api/cart/checkout', methods=['POST'])
@login_required
def checkout():
    user = User.query.get(current_user.id)
    cart_items = user.cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Checkout successful. Cart has been cleared.'})

if __name__ == "__main__":
    app.run(debug=True)