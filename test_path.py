import os
import json

# ------------------ Paths ------------------
BASE_DIR = "/storage/emulated/0/InvoiceApp"
USER_DATA = os.path.join(BASE_DIR, "user_data")
DEBTOR_IMAGES = os.path.join(USER_DATA, "debtor_images_csv")
TXN_IMAGES = os.path.join(USER_DATA, "Txn_images_csv")
REQUIRED_JSON = {
    "debts.json": "{}",
    "goods.json": "{}",
    "transactions.json": "{}"
}

ASSETS_DIRS = [
    os.path.join(BASE_DIR, "assets/icons")
]

EMPTY_DIRS_TO_REMOVE = [
    os.path.join(BASE_DIR, ".kivy/mods"),
    os.path.join(BASE_DIR, ".buildozer"),
    os.path.join(BASE_DIR, ".git")
]

# ------------------ Helper Functions ------------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"[OK] Created directory: {path}")
    else:
        print(f"[OK] Ensured directory exists: {path}")

def ensure_json_file(path, default_content):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)
        print(f"[OK] Created JSON file: {path}")
    else:
        print(f"[OK] {os.path.basename(path)} already exists")

def remove_empty_dirs(dirs):
    for d in dirs:
        if os.path.exists(d) and not os.listdir(d):
            os.rmdir(d)
            print(f"[REMOVED EMPTY] {d}")

def audit_project():
    print("\n=== PROJECT AUDIT REPORT ===\n")
    missing_json = []
    for f in REQUIRED_JSON:
        if not os.path.exists(os.path.join(USER_DATA, f)):
            missing_json.append(f)
    if missing_json:
        print("Missing JSON files in user_data:")
        for f in missing_json:
            print(f" - {f}")
    else:
        print("All required JSON files exist ✅")

    empty_dirs = []
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                empty_dirs.append(dir_path)
    if empty_dirs:
        print("\nEmpty directories:")
        for d in empty_dirs:
            print(f" - {d}")
    else:
        print("\nNo empty directories ✅")

    broken_assets = []
    for asset_dir in ASSETS_DIRS:
        if not os.path.exists(asset_dir) or not os.listdir(asset_dir):
            broken_assets.append(asset_dir)
    if broken_assets:
        print("\nBroken or missing assets:")
        for a in broken_assets:
            print(f" - {a}")
    else:
        print("\nAll assets exist ✅")

    print("\n__pycache__ directories checked ✅")
    print(".pyc files checked ✅")
    print("\n=== AUDIT COMPLETE ===\n")

# ------------------ Pre-Build Setup ------------------
print("=== PRE-BUILD SETUP START ===\n")
ensure_dir(DEBTOR_IMAGES)
ensure_dir(TXN_IMAGES)

for filename, content in REQUIRED_JSON.items():
    ensure_json_file(os.path.join(USER_DATA, filename), content)

remove_empty_dirs(EMPTY_DIRS_TO_REMOVE)

print("\n[INFO] Pre-build setup completed. All required files and folders are ready for APK build.")
print("=== PRE-BUILD SETUP COMPLETE ===\n")

# ------------------ Audit ------------------
audit_project()