from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
PORT = 5000

# Global in-memory data store. 
# We only store base data: the list of transactions and the budget limit.
# All derived metrics (Remaining Budget, Total Expenses, Stats) are calculated dynamically.
data = {
    "transactions": [],
    "monthly_budget": 0.00
}

# Categories for expense tracking
stats_categories = ["Food", "Health", "Transportation", "Home"]

def calculate_current_state():
    """
    Calculates all derived state based on the base data in 'data'.
    
    CORRECTED LOGIC:
    1. Total Expenses is calculated from all 'expense' transactions.
    2. Total Income is calculated from all 'income' transactions.
    3. Remaining Budget = Monthly Limit + Total Income - Total Expenses.
    """
    
    total_expenses = 0.00
    # **FIX: Initialize total_income**
    total_income = 0.00
    stats = {}
    
    # Initialize stats structure for accurate calculation
    for cat in stats_categories:
        stats[cat] = 0.00

    # Iterate through all transactions to calculate metrics
    for t in data["transactions"]:
        amount = t["amount"]
        
        if t["type"] == 'expense':
            total_expenses += amount # Summing up ALL expenses
            
            # Summing up expenses per category
            if t["category"] in stats:
                stats[t["category"]] += amount
        
        # **FIX: Add income to total_income**
        elif t["type"] == 'income':
            total_income += amount # Summing up ALL income

    # **CRITICAL FIX: Remaining Budget = Monthly Limit + Total Income - Total Expenses**
    remaining_budget = data["monthly_budget"] + total_income - total_expenses
    
    # Return the full state expected by the frontend
    return {
        "current_budget": remaining_budget, # This key is used by the frontend for 'Remaining Budget'
        "monthly_budget": data["monthly_budget"],
        "transactions": data["transactions"],
        "stats": stats,
        "total_expenses": total_expenses,
        # **Adding total_income for completeness, though not strictly required for the fix**
        "total_income": total_income
    }

# Route to serve the main web interface
@app.route('/')
def index():
    """Renders the main HTML page for the budget tracker."""
    return render_template('index.html')

# API for transactions (GET: retrieve data, POST: add transaction)
@app.route('/api/transactions', methods=['GET', 'POST'])
def transactions_api():
    global data
    if request.method == 'GET':
        # Return dynamically calculated state
        return jsonify(calculate_current_state()), 200
    
    elif request.method == 'POST':
        try:
            new_transaction = request.json
            amount = float(new_transaction.get('amount', 0))
            trans_type = new_transaction.get('type', 'expense')
            category = new_transaction.get('category', 'N/A')
            description = new_transaction.get('description', '')

            # Only append the new transaction record to the base data list.
            # No arithmetic operation is performed here.
            data["transactions"].append({
                "amount": amount,
                "type": trans_type,
                "category": category,
                "description": description
            })

            return jsonify({"message": "Transaction added successfully"}), 201

        except Exception as e:
            return jsonify({"error": f"Invalid transaction data: {str(e)}"}), 400

# API Route: Set the monthly budget limit
@app.route('/api/budget', methods=['POST'])
def set_monthly_budget():
    global data
    try:
        req_data = request.json
        new_budget = float(req_data.get('amount', 0.00))
        
        # Update the base monthly budget limit
        data['monthly_budget'] = new_budget
        
        # Return the new state
        return jsonify(calculate_current_state()), 200
    except Exception as e:
        return jsonify({"error": f"Invalid budget amount: {str(e)}"}), 400

# API Route: Reset all in-memory data
@app.route('/api/reset', methods=['POST'])
def reset_api():
    global data
    # Reset only base data
    data["transactions"] = []
    data["monthly_budget"] = 0.00
    
    return jsonify({"message": "All data reset successfully"}), 200

# Run the application
if __name__ == '__main__':
    # Host '0.0.0.0' is necessary for Docker container accessibility
    app.run(host='0.0.0.0', port=PORT, debug=True)