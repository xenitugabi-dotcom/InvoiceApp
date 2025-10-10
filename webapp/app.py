from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Allow frontend access (e.g., React, HTML, etc.)

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")


# --- HELPER FUNCTIONS ---
def load_json(filename):
    """Safely load data from JSON file."""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_json(filename, data):
    """Safely save dictionary or list data to JSON file."""
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
    goods = load_json("goods.json")
    return jsonify({"status": "success", "data": goods})


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
            return jsonify({"status": "error", "message": f"Product '{name}' not found"})

        # Update quantity and price
        goods[name]["quantity"] += qty
        goods[name]["price"] = new_price
        save_json("goods.json", goods)

        return jsonify({"status": "success", "message": f"Restocked {qty} units of {name}"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


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
            return jsonify({"status": "error", "message": f"Product '{product}' not found"})

        if goods[product]["quantity"] < qty:
            return jsonify({"status": "error", "message": f"Not enough stock for '{product}'"})

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
        if isinstance(transactions, list):
            transactions.append(sale)
        else:
            transactions = [sale]

        # Record debts if needed
        if amount_paid < total_price:
            debt_entry = {
                "customer": customer,
                "product": product,
                "amount_owed": total_price - amount_paid
            }
            if isinstance(debts, list):
                debts.append(debt_entry)
            else:
                debts = [debt_entry]

        # Save updated data
        save_json("transactions.json", transactions)
        save_json("debts.json", debts)
        save_json("goods.json", goods)

        return jsonify({"status": "success", "message": f"Sale recorded for {customer}"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# --- DEBT ROUTES ---
@app.route("/api/debts", methods=["GET"])
def api_get_debts():
    """Fetch all debts."""
    debts = load_json("debts.json")
    return jsonify({"status": "success", "data": debts})


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
            return jsonify({"status": "error", "message": "Debt record not found"})

        save_json("debts.json", debts)
        return jsonify({"status": "success", "message": f"Debt updated for {customer}"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# --- SERVER START ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
