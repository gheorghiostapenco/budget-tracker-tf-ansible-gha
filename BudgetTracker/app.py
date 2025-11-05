import os
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# -----------------------------
# Data Store
# -----------------------------
data = {
    "transactions": [],
    "monthly_budget": 0.00
}

# Categories
expense_categories = ["Food", "Health", "Transportation", "Home"]
income_categories = ["Salary", "Freelance", "Other"]

# -----------------------------
# Helper: Calculate Current State
# -----------------------------
def calculate_current_state():
    total_expenses = 0.00
    total_income = 0.00

    expense_stats = {cat: 0.00 for cat in expense_categories}
    income_stats = {cat: 0.00 for cat in income_categories}

    for t in data["transactions"]:
        amount = round(float(t["amount"]), 2)
        trans_type = t.get("type", "expense")
        category = t.get("category", "Other")

        if trans_type == "expense":
            total_expenses += amount
            expense_stats[category] = round(expense_stats.get(category, 0.00) + amount, 2)
        elif trans_type == "income":
            total_income += amount
            income_stats[category] = round(income_stats.get(category, 0.00) + amount, 2)

    remaining_budget = round(data["monthly_budget"] + total_income - total_expenses, 2)
    total_expenses = round(total_expenses, 2)
    total_income = round(total_income, 2)
    monthly_budget = round(data["monthly_budget"], 2)

    return {
        "current_budget": remaining_budget,
        "monthly_budget": monthly_budget,
        "transactions": data["transactions"],
        "expense_stats": expense_stats,
        "income_stats": income_stats,
        "total_expenses": total_expenses,
        "total_income": total_income
    }

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Template error: {str(e)}")
        abort(500, description="Internal server error: Template not found")

# Transactions API
@app.route('/api/transactions', methods=['GET', 'POST'])
def transactions_api():
    global data
    if request.method == 'GET':
        return jsonify(calculate_current_state()), 200

    elif request.method == 'POST':
        if not isinstance(request.json, dict):
            return jsonify({"error": "Request body must be JSON object"}), 400

        new_transaction = request.json
        amount = new_transaction.get('amount')
        trans_type = new_transaction.get('type', 'expense')
        category = new_transaction.get('category', 'Other')
        description = new_transaction.get('description', '')

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except (TypeError, ValueError):
            return jsonify({"error": "Amount must be a number"}), 400

        # Validate type
        if trans_type not in ['expense', 'income']:
            return jsonify({"error": "Type must be 'expense' or 'income'"}), 400

        # Validate category
        if trans_type == 'expense' and category not in expense_categories:
            return jsonify({"error": f"Category must be one of {expense_categories}"}), 400
        if trans_type == 'income' and category not in income_categories:
            category = 'Other'  # default for unknown income categories

        # Save transaction
        data["transactions"].append({
            "amount": amount,
            "type": trans_type,
            "category": category,
            "description": description
        })
        app.logger.info(f"Added transaction: {trans_type}, {amount}, {category}")
        return jsonify({"message": "Transaction added successfully"}), 201

# Set Monthly Budget
@app.route('/api/budget', methods=['POST'])
def set_monthly_budget():
    global data
    if not isinstance(request.json, dict):
        return jsonify({"error": "Request body must be JSON object"}), 400

    try:
        new_budget = float(request.json.get('amount'))
        if new_budget < 0:
            return jsonify({"error": "Budget amount cannot be negative"}), 400

        data['monthly_budget'] = round(new_budget, 2)
        app.logger.info(f"Set monthly budget: {new_budget}")
        return jsonify(calculate_current_state()), 200
    except (TypeError, ValueError):
        return jsonify({"error": "Budget amount must be a number"}), 400

# Reset API
@app.route('/api/reset', methods=['POST'])
def reset_api():
    global data
    data["transactions"] = []
    data["monthly_budget"] = 0.00
    app.logger.info("Data reset performed")
    return jsonify({"message": "All data reset successfully"}), 200

# -----------------------------
# Main
# -----------------------------
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=os.environ.get('FLASK_DEBUG', 'False') == 'True'
    )
