from flask import Flask, render_template, request, redirect, session, url_for
from system import auth_manager, bank_ops, init_db

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        role = request.form.get('role', 'user')

        if not username or not password:
            return render_template('register.html', error="All fields required")

        success, msg = auth_manager.register_user(username, password, role)

        if success:
            return redirect(url_for('login'))
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
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/dashboard')

        return render_template('login.html', error=msg)

    return render_template('login.html')


# ---------------- USER DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    if session.get('role') != 'user':
        return redirect('/admin/dashboard')

    user_id = session['user_id']   # ✅ FIXED

    accounts, msg = bank_ops.get_user_accounts(user_id)

    return render_template(
        'dashboard.html',
        username=session['username'],
        accounts=accounts,
        msg=msg
    )


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/')

    if session.get('role') != 'admin':
        return redirect('/dashboard')

    # 🔥 OPTIONAL: show all accounts to admin
    from system import admin_ops
    accounts, msg = admin_ops.get_all_accounts()

    return render_template(
        'dashboard.html',
        username=session['username'],
        accounts=accounts,
        msg="Admin Panel"
    )


# ---------------- CREATE ACCOUNT ----------------
@app.route('/create_account', methods=['POST'])
def create_account():
    if 'user_id' not in session:
        return redirect('/')

    acc_type = request.form['type']
    bank_ops.create_account(session['user_id'], acc_type)

    return redirect('/dashboard')


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


# ---------------- TRANSACTION HISTORY ----------------
@app.route('/transactions', methods=['GET'])
def transactions():
    if 'user_id' not in session:
        return redirect('/')

    # ✅ get account from dashboard (GET request)
    account = request.args.get('account')

    if account:
        transactions, msg = bank_ops.get_transaction_history(account)
        return render_template('transactions.html', transactions=transactions, msg=msg)

    # if no account selected → go back
    return redirect('/dashboard')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)