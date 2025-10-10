from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Allow access from web frontends

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- HELPER FUNCTION ---
def load_json(filename):
    """Load data from a JSON file safely."""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    """Save dictionary data to JSON file."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# --- HOME ROUTE ---
@app.route("/")
def home():
    return render_template("index.html")

# --- GOODS ROUTES ---
@app.route("/api/goods", methods=["GET"])
def api_get_goods():
    """Fetch all goods."""
    return jsonify({"status": "success", "data": load_json("goods.json")})

@app.route("/api/restock", methods=["POST"])
def api_restock():
    """Add new quantity and price to an existing product."""
    try:
        data = request.json
        goods = load_json("goods.json")
        name = data.get("name")
        qty = int(data.get("quantity", 0))
        new_price = float(data.get("price", 0))

        if name not in goods:
            return jsonify({"status": "error", "message": "Product not found"}), 404

        # Update quantity and price
        goods[name]["quantity"] += qty
        goods[name]["price"] = new_price
        save_json("goods.json", goods)

        return jsonify({"status": "success", "message": f"{name} restocked successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SALES ROUTES ---
@app.route("/api/sale", methods=["POST"])
def api_record_sale():
    """Record a sale transaction and update stock."""
    try:
        data = request.json
        goods = load_json("goods.json")
        transactions = load_json("transactions.json")
        debts = load_json("debts.json")

        customer = data.get("customer")
        product = data.get("product")
        qty = int(data.get("quantity", 0))
        amount_paid = float(data.get("amount_paid", 0))

        if product not in goods:
            return jsonify({"status": "error", "message": "Product not found"}), 404

        total_price = goods[product]["price"] * qty
        goods[product]["quantity"] -= qty

        # Record transaction
        sale = {
            "customer": customer,
            "product": product,
            "quantity": qty,
            "total_price": total_price,
            "amount_paid": amount_paid,
            "debt": total_price - amount_paid
        }
        transactions.append(sale)

        # Track debts
        if amount_paid < total_price:
            debts.append({
                "customer": customer,
                "product": product,
                "amount_owed": total_price - amount_paid
            })

        save_json("transactions.json", transactions)
        save_json("debts.json", debts)
        save_json("goods.json", goods)

        return jsonify({"status": "success", "message": "Sale recorded successfully", "data": sale})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- DEBT ROUTES ---
@app.route("/api/debts", methods=["GET"])
def api_get_debts():
    """Fetch all debts."""
    return jsonify({"status": "success", "data": load_json("debts.json")})

@app.route("/api/update_debt", methods=["POST"])
def api_update_debt():
    """Update a customer's debt payment."""
    try:
        data = request.json
        customer = data.get("customer")
        product = data.get("product")
        payment = float(data.get("payment", 0))

        debts = load_json("debts.json")
        updated = False

        for debt in debts:
            if debt["customer"] == customer and debt["product"] == product:
                debt["amount_owed"] -= payment
                if debt["amount_owed"] <= 0:
                    debt["amount_owed"] = 0
                updated = True

        if not updated:
            return jsonify({"status": "error", "message": "Debt record not found"}), 404

        save_json("debts.json", debts)
        return jsonify({"status": "success", "message": "Debt updated successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- SERVER START ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)