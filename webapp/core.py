import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- GOODS ----------------
def get_goods():
    return load_json("goods.json")

def restock_product(name, qty, new_price):
    goods = load_json("goods.json")
    if name not in goods:
        return {"error": "Product not found"}

    goods[name]["quantity"] += qty
    goods[name]["price"] = new_price

    # record restock in product history
    history = goods[name].setdefault("history", [])
    history.append({
        "action": "restock",
        "quantity": qty,
        "new_price": new_price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json("goods.json", goods)
    return {"message": f"{name} restocked successfully."}

# ---------------- SALES ----------------
def record_sale(customer, product, qty, amount_paid):
    goods = load_json("goods.json")
    transactions = load_json("transactions.json")
    debts = load_json("debts.json")

    if product not in goods:
        return {"error": "Product not found"}

    item = goods[product]
    if item["quantity"] < qty:
        return {"error": "Insufficient stock"}

    total_price = item["price"] * qty
    debt = total_price - amount_paid

    # reduce stock
    item["quantity"] -= qty

    # record transaction
    transaction = {
        "customer": customer,
        "product": product,
        "quantity": qty,
        "price": item["price"],
        "total": total_price,
        "paid": amount_paid,
        "debt": debt,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    transactions.setdefault("sales", []).append(transaction)

    # record debt if any
    if debt > 0:
        debts.setdefault(customer, []).append(transaction)

    save_json("goods.json", goods)
    save_json("transactions.json", transactions)
    save_json("debts.json", debts)
    return {"message": "Sale recorded successfully"}

# ---------------- DEBTS ----------------
def get_debts():
    return load_json("debts.json")

def update_debt(customer, product, new_payment):
    debts = load_json("debts.json")
    if customer not in debts:
        return {"error": "Customer not found"}

    records = debts[customer]
    for r in records:
        if r["product"].lower() == product.lower() and r["debt"] > 0:
            r["paid"] += new_payment
            r["debt"] = max(r["total"] - r["paid"], 0)
            r["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    save_json("debts.json", debts)
    return {"message": f"Debt updated for {customer} - {product}"}