from flask import Flask, render_template, request, redirect, session
from system import auth_manager, bank_ops, init_db

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        success, msg = auth_manager.register_user(username, password)

        if success:
            return redirect('/')   # go to login after register
        else:
            return render_template('register.html', error=msg)

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user, msg = auth_manager.login_user(username, password)

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            return render_template('login.html', error=msg)

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    return render_template('dashboard.html')


# ---------------- DEPOSIT ----------------
@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user_id' not in session:
        return redirect('/')

    account = request.form['account']
    amount = float(request.form['amount'])

    bank_ops.deposit(account, amount)
    return redirect('/dashboard')


# ---------------- WITHDRAW ----------------
@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect('/')

    account = request.form['account']
    amount = float(request.form['amount'])

    bank_ops.withdraw(account, amount)
    return redirect('/dashboard')


# ---------------- TRANSFER ----------------
@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session:
        return redirect('/')

    source = request.form['source']
    target = request.form['target']
    amount = float(request.form['amount'])

    bank_ops.transfer(source, target, amount)
    return redirect('/dashboard')


# ---------------- CREATE ACCOUNT ----------------
@app.route('/create_account', methods=['POST'])
def create_account():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']
    acc_type = request.form['type']

    bank_ops.create_account(user_id, acc_type)
    return redirect('/dashboard')

# ---------------- TRANSACTION HISTORY ----------------
@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        account = request.form['account']

        transactions, msg = bank_ops.get_transaction_history(account)

        return render_template('transactions.html', transactions=transactions, msg=msg)

    return render_template('transactions.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)