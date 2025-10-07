import os
import sys
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

# -------------------- Helpers --------------------
from utils.paths import get_file_path, get_export_path

# -------------------- Screens --------------------
from screens.home import HomeScreen
from screens.add_product import AddProductScreen
from screens.view_product import ViewProductScreen
from screens.record_sales import RecordSalesScreen
from screens.view_transactions import ViewTransactionsScreen
from screens.debts import DebtsScreen
from screens.view_single_transaction import ViewSingleTransactionScreen
from screens.product_details import ProductDetailsScreen  # ✅ product details screen

# -------------------- Required JSON --------------------
REQUIRED_JSON = ["debts.json", "goods.json", "transactions.json"]


class InvoiceApp(App):
    def build(self):
        # ✅ Fixed window size for desktop preview
        if not self._is_android():
            Window.size = (400, 700)

        # ✅ Initialize app data folder
        self._data_dir = os.path.dirname(get_file_path("debts.json"))
        os.makedirs(self._data_dir, exist_ok=True)
        print(f"[INFO] Data directory initialized at: {self._data_dir}")

        # ✅ Create export folders
        self.debtor_images_dir = get_export_path("debts")
        self.txn_images_dir = get_export_path("transactions")

        # ✅ Ensure essential JSON files exist
        for filename in REQUIRED_JSON:
            path = get_file_path(filename)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)

        # ✅ Assign helper methods
        self.load_json = self._load_json
        self.save_json = self._save_json

        # ✅ Screen Manager setup
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddProductScreen(name="add_product"))
        sm.add_widget(ViewProductScreen(name="view_product"))
        sm.add_widget(RecordSalesScreen(name="record_sales"))
        sm.add_widget(DebtsScreen(name="view_debts"))
        sm.add_widget(ViewTransactionsScreen(name="view_transactions"))
        sm.add_widget(ViewSingleTransactionScreen(name="view_single_transaction"))
        sm.add_widget(ProductDetailsScreen(name="product_details"))  # ✅ added details screen

        return sm

    # -------------------- JSON Utilities --------------------
    def _load_json(self, filename, default=None):
        """Safely load JSON data."""
        path = get_file_path(filename)
        if not os.path.exists(path):
            data = default or {}
            self._save_json(filename, data)
            return data
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Corrupted JSON at {path}: {e}. Resetting...")
            data = default or {}
            self._save_json(filename, data)
            return data

    def _save_json(self, filename, data):
        """Safely write JSON data."""
        path = get_file_path(filename)
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to save {filename}: {e}")

    # -------------------- Platform Check --------------------
    def _is_android(self):
        """Check if running on Android (Termux/Pydroid)."""
        return (
            "ANDROID_ARGUMENT" in os.environ
            or "ANDROID_APP_PATH" in os.environ
            or sys.platform == "android"
        )


if __name__ == "__main__":
    InvoiceApp().run()