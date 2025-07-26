from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")
users = db.execute("SELECT * FROM users")
transactions = db.execute("SELECT * FROM transactions")

@app.route("/")
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", user_id)
    income_result = db.execute("SELECT SUM(amount) as total FROM transactions WHERE type IS 'income' AND user_id = ?", user_id)
    expense_result = db.execute("SELECT SUM(amount) as total FROM transactions WHERE type IS 'expense' AND user_id = ?", user_id)
    total_income = income_result[0]["total"] or 0
    total_expenses = expense_result[0]["total"] or 0
    net_balance = total_income - total_expenses
    return render_template("index.html",
                           transactions=transactions,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           net_balance=net_balance)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        print(request.form)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return("Error: must provide username")

        elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) > 0:
            return("Error: Username is already taken")

        if not password or not confirmation:
            return("Error: must provide password and confirmation")

        elif password != confirmation:
            return("Error: passwords do not match")

        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password_hash)
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return "Error: Please enter Username"
        elif not password:
            return "Error: Please enter Password"

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Error: invalid username or password"

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add", methods = ["GET", "POST"])
def add():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    if request.method == "POST":
        trans_type = request.form.get("type")
        description = request.form.get("description")
        amount = request.form.get("amount")
        category = request.form.get("category")
        date = request.form.get("date")

        if not all([trans_type, description, amount, category, date]):
            return "Error: *All Fields are Required*"
        if trans_type not in ["income", "expense"]:
            return "Error: Invalid transaction type"
        try:
            if float(amount) <= 0:
                return "Error: Amount must be a positive number"
        except ValueError:
            return "Error: Invalid Amount"
        db.execute(
            "INSERT INTO transactions (user_id, type, description, amount, category, date) VALUES (?, ?, ?, ?, ?, ?)",
            user_id,
            trans_type,
            description,
            float(amount),
            category,
            date
        )
        return redirect("/")

    else:
        return render_template("add.html")
