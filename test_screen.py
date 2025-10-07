# test_prebuild_headless.py
import os
import sys
import json
import traceback

# Force flush
print = lambda *a, **k: __import__('builtins').print(*a, **k, flush=True)

print("=== HEADLESS PRE-BUILD TEST ===")

# Try importing only JSON helpers and paths
try:
    from utils.paths import GOODS_JSON_PATH
    print("✅ Path import OK")
except Exception:
    print("❌ Path import failed\n", traceback.format_exc())
    sys.exit(1)

# Test JSON read/write
try:
    os.makedirs(os.path.dirname(GOODS_JSON_PATH), exist_ok=True)
    with open(GOODS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)
    with open(GOODS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["__TEST__"] = {"price": 123, "quantity": 1, "description": "test", "image_path": ""}
    with open(GOODS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ JSON read/write OK at {GOODS_JSON_PATH}")
except Exception:
    print("❌ JSON read/write failed\n", traceback.format_exc())
    sys.exit(1)

print("🎉 HEADLESS PRE-BUILD TEST PASSED — JSON safe for APK build")