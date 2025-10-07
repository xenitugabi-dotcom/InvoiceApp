import os
import json

# -------------------- Base Paths --------------------
USERDATA_PATH = "/storage/emulated/0/InvoiceApp/user_data"

# -------------------- Default JSON Content --------------------
JSON_FILES = {
    "goods.json": "{}",
    "transactions.json": "{}",
    "debts.json": "{}",
}

# -------------------- Export Folders --------------------
EXPORT_DEBTS_PATH = os.path.join(USERDATA_PATH, "debtor_images")
EXPORT_TXNS_PATH = os.path.join(USERDATA_PATH, "transaction_images")


# -------------------- Helper Functions --------------------
def ensure_dir(path):
    """Ensure a directory exists."""
    os.makedirs(path, exist_ok=True)
    return path


def ensure_file(path, default_content="{}"):
    """Ensure a JSON file exists. Create if missing."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)
    return path


def ensure_all_files():
    """Ensure all default JSON files exist."""
    ensure_dir(USERDATA_PATH)
    for filename, default_content in JSON_FILES.items():
        ensure_file(os.path.join(USERDATA_PATH, filename), default_content)
    ensure_dir(EXPORT_DEBTS_PATH)
    ensure_dir(EXPORT_TXNS_PATH)


# -------------------- Get File Path --------------------
def get_file_path(filename=None):
    """
    Return the full path for a JSON file in user_data.
    Auto-creates the file if missing.
    """
    ensure_all_files()
    if filename is None or filename == "":
        return USERDATA_PATH
    if filename not in JSON_FILES:
        raise ValueError(f"Unknown JSON file requested: {filename}")
    return os.path.join(USERDATA_PATH, filename)


# -------------------- Direct Constants --------------------
GOODS_JSON_PATH = get_file_path("goods.json")
TRANSACTIONS_JSON_PATH = get_file_path("transactions.json")
DEBTS_JSON_PATH = get_file_path("debts.json")


# -------------------- Export Path --------------------
def get_export_path(export_type="transactions"):
    """
    Returns the path for exported images.
    export_type: 'transactions' or 'debts'
    """
    if export_type == "debts":
        return ensure_dir(EXPORT_DEBTS_PATH)
    else:
        return ensure_dir(EXPORT_TXNS_PATH)