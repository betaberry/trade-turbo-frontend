from flask import Flask, request, redirect, url_for, render_template, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key

@app.route('/')
def home():
    return render_template('index.html')


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
                    totalBalance REAL NOT NULL DEFAULT 0
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
                ''', ('JohnDoe', 'password', 1000, 0, 0, 1000))
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
                ''', (username, password, 1000, 0, 0, 1000))
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
                session['totalBalance'] = user[5]
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
    session.pop('totalBalance', None)
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
            updated_stocks.append((stock_id, name, average_purchase_price, current_price, round(pnl, 2), quantity, round(total_value, 2)))
        else:
            updated_stocks.append((stock_id, name, purchase_price, current_price, 0, quantity, round(total_value, 2)))

    return render_template('stocks.html', stocks=updated_stocks)

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT username, walletBalance, stockAsset
            FROM users
            WHERE id = ?
        ''', (user_id,))
        user = c.fetchone()

    if user:
        username, wallet_balance, stock_asset = user
        total_balance = round(wallet_balance + stock_asset, 2)
        total_pnl = round(total_balance - 1000, 2)  # PNL as 1000 - total balance

        return render_template('profile.html',
                               username=username,
                               wallet_balance=round(wallet_balance, 2),
                               stock_asset=round(stock_asset, 2),
                               total_pnl=total_pnl,
                               total_balance=total_balance)
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
                        new_total_value = new_total_purchase_price
                        new_quantity = stock_quantity + quantity
                        average_purchase_price = new_total_purchase_price / new_quantity

                        # Check user wallet balance
                        user_wallet_balance = session.get('walletBalance')
                        if user_wallet_balance >= total_cost:
                            # Update stock quantity, average purchase price, and total value
                            c.execute(
                                'UPDATE stocks SET quantity = ?, purchasePrice = ?, totalPurchasePrice = ?, totalValue = ? WHERE id = ?',
                                (new_quantity, round(average_purchase_price, 2), round(new_total_purchase_price, 2),
                                 round(new_total_value, 2),
                                 stock_id))

                            # Update user wallet balance and stock asset
                            c.execute(
                                'UPDATE users SET walletBalance = walletBalance - ?, stockAsset = (SELECT SUM(totalValue) FROM stocks) WHERE id = ?',
                                (total_cost, user_id))
                            conn.commit()
                            session['walletBalance'] = user_wallet_balance - total_cost
                            session['stockAsset'] = sum(
                                stock[6] for stock in get_stock_data())  # Recalculate total stock asset
                            session['totalBalance'] = round(session['walletBalance'] + session['stockAsset'], 2)
                            return redirect(url_for('manage_stock'))
                        else:
                            return render_template('manage_stock.html', error="Insufficient funds",
                                                   stocks=get_stock_data(), walletBalance=user_wallet_balance)

                    elif action == 'sell':
                        if quantity <= stock_quantity:
                            total_revenue = current_price * quantity
                            # Calculate the cost of the sold stocks
                            average_purchase_price = total_value / stock_quantity
                            cost_of_sold = average_purchase_price * quantity
                            new_total_purchase_price = total_purchase_price - cost_of_sold
                            new_total_value = new_total_purchase_price
                            new_quantity = stock_quantity - quantity
                            new_average_purchase_price = new_total_value / new_quantity if new_quantity > 0 else 0

                            # Update stock quantity, total purchase price, and total value
                            c.execute(
                                'UPDATE stocks SET quantity = ?, purchasePrice = ?, totalPurchasePrice = ?, totalValue = ? WHERE id = ?',
                                (new_quantity, round(new_average_purchase_price, 2), round(new_total_purchase_price, 2),
                                 round(new_total_value, 2),
                                 stock_id))

                            # Update user wallet balance and stock asset
                            c.execute(
                                'UPDATE users SET walletBalance = walletBalance + ?, stockAsset = (SELECT SUM(totalValue) FROM stocks) WHERE id = ?',
                                (total_revenue, user_id))
                            conn.commit()
                            session['walletBalance'] += total_revenue
                            session['stockAsset'] = sum(
                                stock[6] for stock in get_stock_data())  # Recalculate total stock asset
                            session['totalBalance'] = round(session['walletBalance'] + session['stockAsset'], 2)
                            return redirect(url_for('manage_stock'))
                        else:
                            return render_template('manage_stock.html', error="Not enough stock to sell",
                                                   stocks=get_stock_data(), walletBalance=session.get('walletBalance'))
            except sqlite3.Error as e:
                return str(e)

    # Ensure walletBalance is included in the context
    return render_template('manage_stock.html', stocks=get_stock_data(), walletBalance=session.get('walletBalance'))


def get_stock_data():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM stocks')
        stocks = c.fetchall()
    return stocks


@app.route('/update_prices', methods=['POST'])
def update_prices():
    # Placeholder logic for updating prices; replace with actual logic
    import random  # For demo purposes only

    # Define a function to simulate price updates
    def simulate_price_update(current_price):
        return round(current_price * (1 + random.uniform(-0.05, 0.05)), 2)

    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()

        # Fetch all stocks
        c.execute('SELECT id, currentPrice FROM stocks')
        stocks = c.fetchall()

        # Update the price of each stock
        for stock_id, current_price in stocks:
            new_price = simulate_price_update(current_price)
            c.execute('UPDATE stocks SET currentPrice = ? WHERE id = ?', (new_price, stock_id))

        conn.commit()

    # Redirect to the current prices page with updated data
    return redirect(url_for('current_prices'))


if __name__ == '__main__':
    app.run(debug=True)
