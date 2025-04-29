from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="6265873339",
    database="canteen_db2"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/items_management', methods=['GET', 'POST'])
def items_management():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        action = request.form['action']
        if action == 'add':
            name = request.form['name']
            category = request.form['category']
            price = request.form['price']
            cursor.execute("INSERT INTO items (name, category, price) VALUES (%s, %s, %s)", (name, category, price))
            db.commit()
        elif action == 'modify':
            item_id = request.form['item_id']
            name = request.form['name']
            category = request.form['category']
            price = request.form['price']
            cursor.execute("UPDATE items SET name = %s, category = %s, price = %s WHERE id = %s", (name, category, price, item_id))
            db.commit()
        elif action == 'delete':
            item_id = request.form['item_id']
            cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
            db.commit()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    return render_template('items_management.html', items=items)

@app.route('/orders_view')
def orders_view():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    cursor.execute("SELECT o.order_id, c.name, i.name AS item_name, o.quantity, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.id JOIN items i ON o.item_id = i.id")
    orders = cursor.fetchall()
    return render_template('orders_view.html', orders=orders)

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        cursor.execute("SELECT * FROM customers WHERE id = %s AND password = %s", (id, password))
        customer = cursor.fetchone()
        if customer:
            session['customer'] = id
            return redirect(url_for('customer_menu'))
        return render_template('customer_login.html', error="Invalid credentials")
    return render_template('customer_login.html')

@app.route('/customer_register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        password = request.form['password']
        contact = request.form['contact']
        cursor.execute("INSERT INTO customers (id, name, password, contact) VALUES (%s, %s, %s, %s)", (id, name, password, contact))
        db.commit()
        return redirect(url_for('customer_login'))
    return render_template('customer_register.html')

@app.route('/customer_menu')
def customer_menu():
    if 'customer' not in session:
        return redirect(url_for('customer_login'))
    cursor.execute("SELECT * FROM items WHERE category = 'breakfast'")
    breakfast = cursor.fetchall()
    cursor.execute("SELECT * FROM items WHERE category = 'lunch'")
    lunch = cursor.fetchall()
    cursor.execute("SELECT * FROM items WHERE category = 'dinner'")
    dinner = cursor.fetchall()
    cursor.execute("SELECT * FROM items WHERE category = 'snacks'")
    snacks = cursor.fetchall()
    return render_template('customer_menu.html', breakfast=breakfast, lunch=lunch, dinner=dinner, snacks=snacks)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'customer' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    item_id = request.form['item_id']
    quantity = request.form['quantity']
    cursor.execute("INSERT INTO orders (customer_id, item_id, quantity) VALUES (%s, %s, %s)", (session['customer'], item_id, quantity))
    db.commit()
    return jsonify({'success': 'Item added to cart'})

@app.route('/cart')
def cart():
    if 'customer' not in session:
        return redirect(url_for('customer_login'))
    cursor.execute("SELECT o.order_id, i.name, i.price, o.quantity FROM orders o JOIN items i ON o.item_id = i.id WHERE o.customer_id = %s", (session['customer'],))
    cart_items = cursor.fetchall()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('customer', None)
    return redirect(url_for('home'))
    


# ... (existing imports and code)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'customer' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    order_id = request.form['order_id']
    # Verify that the order belongs to the logged-in customer
    cursor.execute("SELECT * FROM orders WHERE order_id = %s AND customer_id = %s", (order_id, session['customer']))
    order = cursor.fetchone()
    if not order:
        return jsonify({'error': 'Order not found or not authorized'}), 403
    # Delete the order
    cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    db.commit()
    return jsonify({'success': 'Item removed from cart'})



if __name__ == '__main__':
    app.run(debug=True)