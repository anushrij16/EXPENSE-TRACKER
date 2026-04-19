from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

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
    type = db.Column(db.String(10))
    date = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('person', 'amount', 'type', 'date', name='unique_loan'),
    )


class EMI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    due_date = db.Column(db.Integer)

# ---------------- DASHBOARD ----------------

@app.route('/')
@app.route('/dashboard')
def dashboard():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    loans = Loan.query.all()
    emis = EMI.query.all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    loan_given = sum(l.amount for l in loans if l.type == 'given')
    loan_taken = sum(l.amount for l in loans if l.type == 'taken')

    total_emi = sum(e.amount for e in emis)

    budget = Budget.query.first()
    budget_amount = budget.amount if budget else 0

    balance = total_income - total_expense - loan_given + loan_taken - total_emi

    return render_template(
        'dashboard.html',
        incomes=incomes,
        expenses=expenses,
        loans=loans,
        emis=emis,
        total_income=total_income,
        total_expense=total_expense,
        budget=budget_amount,
        balance=balance
    )

# ---------------- INCOME ----------------

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        db.session.add(Income(
            source=request.form['source'],
            amount=float(request.form['amount']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d')
        ))
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
    db.session.delete(Income.query.get_or_404(id))
    db.session.commit()
    return redirect('/dashboard')

# ---------------- EXPENSE ----------------

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        db.session.add(Expense(
            category=request.form['category'],
            amount=float(request.form['amount']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d')
        ))
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
    db.session.delete(Expense.query.get_or_404(id))
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
        try:
            loan = Loan(
                person=request.form['person'],
                amount=float(request.form['amount']),
                type=request.form.get('type', 'given'),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d')
            )

            db.session.add(loan)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

        return redirect('/dashboard')

    return render_template('add_loan.html')


@app.route('/delete_loan/<int:id>')
def delete_loan(id):
    db.session.delete(Loan.query.get_or_404(id))
    db.session.commit()
    return redirect('/dashboard')


@app.route('/edit_loan/<int:id>', methods=['GET', 'POST'])
def edit_loan(id):
    loan = Loan.query.get_or_404(id)

    if request.method == 'POST':
        loan.person = request.form['person']
        loan.amount = float(request.form['amount'])
        loan.type = request.form.get('type', 'given')
        loan.date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_loan.html', loan=loan)

# ---------------- EMI ----------------

@app.route('/add_emi', methods=['GET', 'POST'])
def add_emi():
    if request.method == 'POST':
        db.session.add(EMI(
            name=request.form['name'],
            amount=float(request.form['amount']),
            due_date=int(request.form['due_date'])
        ))
        db.session.commit()
        return redirect('/dashboard')

    return render_template('add_emi.html')


@app.route('/delete_emi/<int:id>')
def delete_emi(id):
    db.session.delete(EMI.query.get_or_404(id))
    db.session.commit()
    return redirect('/dashboard')

# ---------------- REPORTS ----------------

@app.route('/reports')
def reports():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    loans = Loan.query.all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    # 💰 Savings
    savings = total_income - total_expense

    # 🎯 Budget
    budget = Budget.query.first()
    budget_amount = budget.amount if budget else 0

    # ⚠ Correct Status Logic (IMPORTANT FIX)
    if total_expense > budget_amount:
        status = "⚠ Overspending (Budget Exceeded)"
    elif total_expense > 0.8 * budget_amount:
        status = "⚠ Near Budget Limit"
    else:
        status = "✅ Good Financial Control"

    # 💸 Remaining Budget
    remaining = budget_amount - total_expense

    # 🥧 Category Breakdown
    from collections import defaultdict
    category_data = defaultdict(float)

    for e in expenses:
        category_data[e.category] += e.amount

    categories = list(category_data.keys())
    values = list(category_data.values())

    # 💸 Loan Summary
    loan_given = sum(l.amount for l in loans if l.type == 'given')
    loan_taken = sum(l.amount for l in loans if l.type == 'taken')

    return render_template(
        'reports.html',
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        status=status,
        categories=categories,
        values=values,
        loan_given=loan_given,
        loan_taken=loan_taken,
        budget=budget_amount,
        remaining=remaining
    )
# ---------------- PDF DOWNLOAD ----------------
@app.route('/download_report')
def download_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet

    styles = getSampleStyleSheet()
    content = []

    from datetime import datetime
    month = datetime.now().strftime("%B %Y")

    # 📊 Data
    incomes = Income.query.all()
    expenses = Expense.query.all()
    loans = Loan.query.all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    budget = Budget.query.first()
    budget_amount = budget.amount if budget else 0

    if total_expense > budget_amount:
        status = "Overspending"
    elif total_expense > 0.8 * budget_amount:
        status = "Near Budget Limit"
    else:
        status = "Good Control"

    loan_given = sum(l.amount for l in loans if l.type == 'given')
    loan_taken = sum(l.amount for l in loans if l.type == 'taken')

    # 🧾 TITLE
    content.append(Paragraph("<b>Financial Report</b>", styles['Title']))
    content.append(Paragraph(f"Month: {month}", styles['Normal']))
    content.append(Spacer(1, 20))

    # 📊 TABLE DATA
    data = [
        ["Category", "Amount"],
        ["Total Income", f"Rs. {total_income}"],
        ["Total Expense", f"Rs. {total_expense}"],
        ["Savings", f"Rs. {savings}"],
        ["Budget", f"Rs. {budget_amount}"],
        ["Status", status],
        ["Loan Given", f"Rs. {loan_given}"],
        ["Loan Taken", f"Rs. {loan_taken}"]
    ]

    table = Table(data)

    # 🎨 STYLE (EXCEL LOOK)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
    ]))

    content.append(table)

    doc.build(content)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="financial_report.pdf")
# ---------------- RUN ----------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)
