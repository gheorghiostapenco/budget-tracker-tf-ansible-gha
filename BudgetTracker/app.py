import os
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

# Data store
data = {
    "transactions": [],
    "monthly_budget": 0.00
}
stats_categories = ["Food", "Health", "Transportation", "Home"]

def calculate_current_state():
    total_expenses = 0.00
    total_income = 0.00
    stats = {cat: 0.00 for cat in stats_categories}

    for t in data["transactions"]:
        amount = t["amount"]
        if t["type"] == 'expense':
            total_expenses += amount
            stats[t["category"]] += amount
        elif t["type"] == 'income':
            total_income += amount

    remaining_budget = data["monthly_budget"] + total_income - total_expenses
    
    return {
        "current_budget": remaining_budget,
        "monthly_budget": data["monthly_budget"],
        "transactions": data["transactions"],
        "stats": stats,
        "total_expenses": total_expenses,
        "total_income": total_income
    }

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Template error: {str(e)}")
        abort(500, description="Internal server error: Template not found")

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
        category = new_transaction.get('category', 'N/A')
        description = new_transaction.get('description', '')

        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except (TypeError, ValueError):
            return jsonify({"error": "Amount must be a number"}), 400

        if trans_type not in ['expense', 'income']:
            return jsonify({"error": "Type must be 'expense' or 'income'"}), 400
        if trans_type == 'expense' and category not in stats_categories:
            return jsonify({"error": f"Category must be one of {stats_categories}"}), 400

        data["transactions"].append({
            "amount": amount,
            "type": trans_type,
            "category": category,
            "description": description
        })
        app.logger.info(f"Added transaction: {trans_type}, {amount}, {category}")
        return jsonify({"message": "Transaction added successfully"}), 201

@app.route('/api/budget', methods=['POST'])
def set_monthly_budget():
    global data
    if not isinstance(request.json, dict):
        return jsonify({"error": "Request body must be JSON object"}), 400
    try:
        new_budget = float(request.json.get('amount'))
        if new_budget < 0:
            return jsonify({"error": "Budget amount cannot be negative"}), 400
        data['monthly_budget'] = new_budget
        app.logger.info(f"Set monthly budget: {new_budget}")
        return jsonify(calculate_current_state()), 200
    except (TypeError, ValueError):
        return jsonify({"error": "Budget amount must be a number"}), 400

@app.route('/api/reset', methods=['POST'])
def reset_api():
    global data
    data["transactions"] = []
    data["monthly_budget"] = 0.00
    app.logger.info("Data reset performed")
    return jsonify({"message": "All data reset successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
