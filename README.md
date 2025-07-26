# Flask-Finance-Tracker

## A CS50 Final Project

A clean and simple web application for tracking personal income and expenses. Users can register for an account, log in, add transactions, and view a dashboard summary of their financial health.

### Core Features
*   User registration and secure login system with password hashing.
*   Dashboard view with a summary of total income, expenses, and net balance.
*   Detailed list of all transactions.
*   Functionality to add new income or expense transactions.

### Tech Stack
*   **Backend:** Python, Flask
*   **Database:** SQLite
*   **Frontend:** HTML, CSS
*   **Libraries:** CS50 Library, Flask, Flask-Session

### How to Run Locally
1.  Clone the repository: `git clone https://github.com/Cyber-DiGit/Flask-Finance-Tracker.git`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Initialize the database: `sqlite3 finance.db < schema.sql`
5.  Run the application: `flask run`
