from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.String(100))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime)

# ---------------- DASHBOARD ----------------

@app.route('/')
@app.route('/dashboard')
def dashboard():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    loans = Loan.query.all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    budget = Budget.query.first()
    budget_amount = budget.amount if budget else 0

    balance = total_income - total_expense

    return render_template(
        'dashboard.html',
        incomes=incomes,
        expenses=expenses,
        loans=loans,
        total_income=total_income,
        total_expense=total_expense,
        budget=budget_amount,
        balance=balance
    )

# ---------------- INCOME ----------------

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        source = request.form['source']
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.add(Income(source=source, amount=amount, date=date))
        db.session.commit()

        return redirect('/dashboard')

    return render_template('add_income.html')


@app.route('/edit_income/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    income = Income.query.get_or_404(id)

    if request.method == 'POST':
        income.source = request.form['source']
        income.amount = float(request.form['amount'])
        income.date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_income.html', income=income)


@app.route('/delete_income/<int:id>')
def delete_income(id):
    income = Income.query.get_or_404(id)
    db.session.delete(income)
    db.session.commit()
    return redirect('/dashboard')

# ---------------- EXPENSE ----------------

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.add(Expense(category=category, amount=amount, date=date))
        db.session.commit()

        return redirect('/dashboard')

    return render_template('add_expense.html')


@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_expense.html', expense=expense)


@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/dashboard')

# ---------------- BUDGET ----------------

@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        amount = float(request.form['amount'])

        budget = Budget.query.first()
        if budget:
            budget.amount = amount
        else:
            db.session.add(Budget(amount=amount))

        db.session.commit()
        return redirect('/dashboard')

    return render_template('budget.html')

# ---------------- LOAN ----------------

@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if request.method == 'POST':
        person = request.form['person']
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.add(Loan(person=person, amount=amount, date=date))
        db.session.commit()

        return redirect('/dashboard')

    return render_template('add_loan.html')

# ---------------- REPORTS ----------------

@app.route('/reports')
def reports():
    incomes = Income.query.all()
    expenses = Expense.query.all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    return render_template(
        'reports.html',
        income=total_income,
        expense=total_expense
    )

# ---------------- RUN ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)