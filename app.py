from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

# Rota raiz
@app.route('/')
def hello_world():
    return 'Oi imundo!'

# Add product route
@app.route('/api/products/add', methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)