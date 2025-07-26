import os
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# --- This is the start of the block to replace ---
print("--- SCRIPT START: Attempting to configure database. ---")

# Get the production database URL from the environment
db_url = os.environ.get("DATABASE_URL")

# Print what we found, so we can see it in the logs.
# This is the most important line for debugging.
print(f"--- DIAGNOSTIC: Value of DATABASE_URL is: {db_url} ---")

# If the DATABASE_URL is NOT set, it means we are running locally.
if not db_url:
    print("--- INFO: No DATABASE_URL found. Falling back to SQLite. ---")
    db_url = "sqlite:///finance.db"
else:
    print("--- INFO: DATABASE_URL found. Configuring for production. ---")

# A professional trick: Some services use 'postgres://' which is deprecated.
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
    print(f"--- INFO: Corrected URL to: {db_url} ---")

# Initialize the database connection using the determined URL
db = SQL(db_url)

print("--- SCRIPT END: Database configured. ---")
# --- This is the end of the block to replace ---
@app.route("/")
def index():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", user_id)
    income_result = db.execute("SELECT SUM(amount) as total FROM transactions WHERE type = 'income' AND user_id = ?", user_id)
    expense_result = db.execute("SELECT SUM(amount) as total FROM transactions WHERE type = 'expense' AND user_id = ?", user_id)
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
            return render_template("Error.html", message="Must provide username")

        elif len(db.execute("SELECT * FROM users WHERE username = ?", username)) > 0:
            return render_template("Error.html", message="Username already exists")

        if not password or not confirmation:
            return render_template("Error.html", message="Must provide password and confirmation")

        elif password != confirmation:
            return render_template("Error.html", message="Passwords do not match")

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
            return render_template("Error.html", message="Must provide username")
        elif not password:
            return render_template("Error.html", message="Must provide password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("Error.html", message="Invalid username or password")

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
            return render_template("Error.html", message="All fields are required")
        if trans_type not in ["income", "expense"]:
            return render_template("Error.html", message="Invalid transaction type")
        try:
            if float(amount) <= 0:
                return render_template("Error.html", message="Amount must be greater than zero")
        except ValueError:
            return render_template("Error.html", message="Invalid amount format")
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
