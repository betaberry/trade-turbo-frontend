from flask import Flask, request, redirect, url_for, render_template, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key


# Function to initialize the database
def init_db():
    if not os.path.exists('database.db'):
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()

            # Create users table with additional fields
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    walletBalance REAL NOT NULL DEFAULT 0,
                    stockAsset REAL NOT NULL DEFAULT 0,
                    totalPNL REAL NOT NULL DEFAULT 0,
                    totalBalance REAL NOT NULL DEFAULT 0  -- Use totalBalance instead of balance
                )
            ''')

            # Create stocks table with quantity, totalValue
            c.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    purchasePrice REAL NOT NULL,
                    currentPrice REAL NOT NULL,
                    pnl REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    totalPurchasePrice REAL NOT NULL DEFAULT 0,
                    totalValue REAL NOT NULL DEFAULT 0
                )
            ''')

            # Insert sample stock data if table is empty
            c.execute('SELECT COUNT(*) FROM stocks')
            if c.fetchone()[0] == 0:
                stocks = [
                    ('Apple', 0, 160, 0, 0),
                    ('Tesla', 0, 680, 0, 0),
                    ('Google', 0, 2600, 0, 0),
                    ('Amazon', 0, 3400, 0, 0),
                    ('Nike', 0, 120, 0, 0),
                ]
                c.executemany('''
                    INSERT INTO stocks (name, purchasePrice, currentPrice, pnl, quantity, totalPurchasePrice, totalValue)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [(s[0], s[1], s[2], s[3], s[4], s[1] * s[4], s[1] * s[4]) for s in stocks])
                conn.commit()

            # Insert a sample user if table is empty
            c.execute('SELECT COUNT(*) FROM users')
            if c.fetchone()[0] == 0:
                c.execute('''
                    INSERT INTO users (username, password, walletBalance, stockAsset, totalPNL, totalBalance)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ('JohnDoe', 'password', 1000, 5000, 1500, 6000))
                conn.commit()


# Initialize the database when the application starts
init_db()


@app.route('/current_prices')
def current_prices():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, currentPrice FROM stocks')
        stocks = c.fetchall()

    return render_template('current_prices.html', stocks=stocks)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO users (username, password, walletBalance, stockAsset, totalPNL, totalBalance)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password, 1000, 5000, 1500, 6000))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return 'Username already exists'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('''
                SELECT id, username, walletBalance, stockAsset, totalPNL, totalBalance
                FROM users
                WHERE username = ? AND password = ?
            ''', (username, password))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['walletBalance'] = user[2]
                session['stockAsset'] = user[3]
                session['totalPNL'] = user[4]
                session['totalBalance'] = user[5]  # Use totalBalance instead of balance
                return redirect(url_for('profile'))
            else:
                return 'Invalid credentials'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('walletBalance', None)
    session.pop('stockAsset', None)
    session.pop('totalPNL', None)
    session.pop('totalBalance', None)  # Use totalBalance instead of balance
    return redirect(url_for('login'))


@app.route('/stocks')
def stocks():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM stocks')
        stocks = c.fetchall()

    # Calculate PNL for each stock
    updated_stocks = []
    for stock in stocks:
        stock_id, name, purchase_price, current_price, pnl, quantity, total_purchase_price, total_value = stock
        if quantity > 0:
            average_purchase_price = total_value / quantity
            pnl = (current_price - average_purchase_price) * quantity
            updated_stocks.append((stock_id, name, average_purchase_price, current_price, pnl, quantity, total_value))
        else:
            updated_stocks.append((stock_id, name, purchase_price, current_price, 0, quantity, total_value))

    return render_template('stocks.html', stocks=updated_stocks)


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT username, walletBalance, stockAsset, totalPNL, totalBalance
            FROM users
            WHERE id = ?
        ''', (user_id,))
        user = c.fetchone()

    if user:
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/manage_stock', methods=['GET', 'POST'])
def manage_stock():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form['action']
        stock_id = request.form['stock_id']
        quantity = int(request.form['quantity'])

        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            try:
                # Fetch current stock data
                c.execute(
                    'SELECT purchasePrice, currentPrice, quantity, totalPurchasePrice, totalValue FROM stocks WHERE id = ?',
                    (stock_id,))
                stock = c.fetchone()
                if stock:
                    purchase_price, current_price, stock_quantity, total_purchase_price, total_value = stock

                    if action == 'buy':
                        total_cost = current_price * quantity
                        new_total_purchase_price = total_purchase_price + (current_price * quantity)
                        new_total_value = total_value + (current_price * quantity)
                        new_quantity = stock_quantity + quantity
                        average_purchase_price = new_total_purchase_price / new_quantity

                        # Check user wallet balance
                        user_wallet_balance = session.get('walletBalance')
                        if user_wallet_balance >= total_cost:
                            # Update stock quantity, average purchase price, and total value
                            c.execute(
                                'UPDATE stocks SET quantity = ?, purchasePrice = ?, totalPurchasePrice = ?, totalValue = ? WHERE id = ?',
                                (new_quantity, average_purchase_price, new_total_purchase_price, new_total_value,
                                 stock_id))

                            # Update user wallet balance and stock asset
                            c.execute(
                                'UPDATE users SET walletBalance = walletBalance - ?, stockAsset = stockAsset + ?, totalBalance = walletBalance + stockAsset WHERE id = ?',
                                (total_cost, total_cost, user_id))
                            conn.commit()
                            session['walletBalance'] = user_wallet_balance - total_cost  # Update session walletBalance
                            session['stockAsset'] += total_cost  # Update session stockAsset
                            session['totalBalance'] = session['walletBalance'] + session[
                                'stockAsset']  # Update session totalBalance
                            return redirect(url_for('manage_stock'))
                        else:
                            return render_template('manage_stock.html', error="Insufficient funds",
                                                   stocks=get_stock_data())

                    elif action == 'sell':
                        if quantity <= stock_quantity:
                            total_revenue = current_price * quantity
                            # Calculate the cost of the sold stocks
                            average_purchase_price = total_value / stock_quantity
                            cost_of_sold = average_purchase_price * quantity
                            new_total_purchase_price = total_purchase_price - cost_of_sold
                            new_total_value = total_value - cost_of_sold
                            new_quantity = stock_quantity - quantity
                            new_average_purchase_price = new_total_value / new_quantity if new_quantity > 0 else 0

                            # Update stock quantity, total purchase price, and total value
                            c.execute(
                                'UPDATE stocks SET quantity = ?, purchasePrice = ?, totalPurchasePrice = ?, totalValue = ? WHERE id = ?',
                                (new_quantity, new_average_purchase_price, new_total_purchase_price, new_total_value,
                                 stock_id))

                            # Update user wallet balance and stock asset
                            c.execute(
                                'UPDATE users SET walletBalance = walletBalance + ?, stockAsset = stockAsset - ?, totalBalance = walletBalance + stockAsset WHERE id = ?',
                                (total_revenue, total_revenue, user_id))
                            conn.commit()
                            session['walletBalance'] += total_revenue  # Update session walletBalance
                            session['stockAsset'] -= total_revenue  # Update session stockAsset
                            session['totalBalance'] = session['walletBalance'] + session[
                                'stockAsset']  # Update session totalBalance
                            return redirect(url_for('manage_stock'))
                        else:
                            return render_template('manage_stock.html', error="Not enough stock to sell",
                                                   stocks=get_stock_data())
            except sqlite3.Error as e:
                return str(e)

    return render_template('manage_stock.html', stocks=get_stock_data())


def get_stock_data():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM stocks')
        stocks = c.fetchall()
    return stocks


if __name__ == '__main__':
    app.run(debug=True)
