import json
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from utils.paths import get_file_path  # ✅ Use paths helper


class RecordSalesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_product = None

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Record Sales", font_size=22, size_hint=(1, 0.15)))

        # Inputs
        self.buyer_input = TextInput(hint_text="Customer Name", multiline=False)
        self.product_input = TextInput(hint_text="Select Product", multiline=False, readonly=True)
        self.product_input.bind(on_touch_down=self._on_product_input_touch)
        self.product_price_label = Label(text="Product Price: ₦0.00")
        self.quantity_input = TextInput(hint_text="Quantity", input_filter='int', multiline=False)
        self.quantity_input.bind(text=self.update_amount_due)
        self.amount_due_label = Label(text="Amount to Pay: ₦0.00")
        self.amount_paid_input = TextInput(hint_text="Amount Paid", input_filter='float', multiline=False)
        self.message = Label(text="", size_hint=(1, 0.15))

        # Buttons
        btn_record = Button(text="Record Sale")
        btn_view_transactions = Button(text="View Transactions")
        btn_back = Button(text="Back")

        for w in [
            self.buyer_input, self.product_input, self.product_price_label,
            self.quantity_input, self.amount_due_label, self.amount_paid_input,
            btn_record, btn_view_transactions, btn_back, self.message
        ]:
            layout.add_widget(w)

        self.add_widget(layout)

        # Bindings
        btn_record.bind(on_release=self.record_sale)
        btn_view_transactions.bind(on_release=lambda x: self.goto_screen('view_transactions'))
        btn_back.bind(on_release=lambda x: self.goto_screen('home'))

    # ------------------ JSON Helpers ------------------
    def load_json(self, path, default=None):
        default = default or {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else default
        except Exception:
            return default

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ------------------ Products ------------------
    def load_products(self):
        goods_path = get_file_path("goods.json")
        goods = self.load_json(goods_path, default={})
        self.products = [
            {"key": k, "name": k, "price": v.get("price", 0), "quantity": v.get("quantity", 0)}
            for k, v in goods.items()
        ]
        return self.products

    def _on_product_input_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.open_product_popup()
            return True
        return False

    def open_product_popup(self):
        self.load_products()
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        search_input = TextInput(hint_text="Search product", multiline=False, size_hint_y=None, height=40)
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)

        popup_layout.add_widget(search_input)
        popup_layout.add_widget(scroll)

        popup = Popup(title="Select Product", content=popup_layout, size_hint=(0.9, 0.8))

        def populate_grid(filter_text=""):
            grid.clear_widgets()
            for product in self.products:
                if filter_text.lower() in product['name'].lower():
                    btn = Button(
                        text=f"{product['name']} - ₦{product['price']}",
                        size_hint_y=None, height=40
                    )
                    btn.bind(on_release=lambda inst, p=product: select_product(p))
                    grid.add_widget(btn)

        def select_product(product):
            self.selected_product = product
            self.product_input.text = product['name']
            self.product_price_label.text = f"Product Price: ₦{product['price']:.2f}"
            self.update_amount_due()
            popup.dismiss()

        search_input.bind(text=lambda inst, val: populate_grid(val))

        btn_back_popup = Button(text="Back", size_hint_y=None, height=40)
        btn_back_popup.bind(on_release=lambda x: popup.dismiss())
        popup_layout.add_widget(btn_back_popup)

        populate_grid()
        popup.open()

    # ------------------ Amount Calculation ------------------
    def update_amount_due(self, *args):
        try:
            quantity = int(self.quantity_input.text)
            price = self.selected_product['price'] if self.selected_product else 0
            self.amount_due_label.text = f"Amount to Pay: ₦{price * quantity:.2f}"
        except:
            self.amount_due_label.text = "Amount to Pay: ₦0.00"

    # ------------------ Record Sale ------------------
    def record_sale(self, instance):
        buyer = self.buyer_input.text.strip()
        quantity_text = self.quantity_input.text.strip()
        paid_text = self.amount_paid_input.text.strip()

        if not all([buyer, self.selected_product, quantity_text, paid_text]):
            self.message.text = "⚠️ Please fill all fields."
            self.message.color = (1, 0, 0, 1)
            return

        try:
            quantity = int(quantity_text)
            paid = float(paid_text)
        except:
            self.message.text = "⚠️ Invalid quantity or payment."
            self.message.color = (1, 0, 0, 1)
            return

        goods_path = get_file_path("goods.json")
        goods = self.load_json(goods_path, default={})
        product_key = next(
            (k for k in goods if k.strip().lower() == self.selected_product['name'].strip().lower()), None
        )
        if not product_key:
            self.message.text = "⚠️ Product not found."
            self.message.color = (1, 0, 0, 1)
            return

        product = goods[product_key]
        if quantity > product.get('quantity', 0):
            self.message.text = "⚠️ Not enough stock."
            self.message.color = (1, 0, 0, 1)
            return

        total_price = self.selected_product['price'] * quantity
        debt_amount = max(total_price - paid, 0)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ Update stock
        product['quantity'] -= quantity
        goods[product_key] = product
        self.save_json(goods_path, goods)

        # ✅ Record transaction
        tx_path = get_file_path("transactions.json")
        transactions = self.load_json(tx_path, default={})
        if not isinstance(transactions, dict):
            transactions = {}
        transactions.setdefault("sales", [])
        transactions["sales"].append({
            "buyer": buyer,
            "product": self.selected_product['name'],
            "quantity": quantity,
            "total_price": total_price,
            "amount_paid": paid,
            "debt": debt_amount,
            "date": date_str
        })
        self.save_json(tx_path, transactions)

        # ✅ Record debt if any
        if debt_amount > 0:
            debts_path = get_file_path("debts.json")
            debts = self.load_json(debts_path, default={})
            if not isinstance(debts, dict):
                debts = {}
            debts.setdefault("debts", [])
            debts["debts"].append({
                "buyer": buyer,
                "product": self.selected_product['name'],
                "quantity": quantity,
                "total_price": total_price,
                "amount_paid": paid,
                "debt": debt_amount,
                "date": date_str,
                "history": [{"date": date_str, "paid": paid}]
            })
            self.save_json(debts_path, debts)

        # ✅ Reset
        self.message.text = "✅ Sale recorded successfully!"
        self.message.color = (0, 1, 0, 1)
        self.buyer_input.text = ""
        self.product_input.text = ""
        self.quantity_input.text = ""
        self.amount_paid_input.text = ""
        self.product_price_label.text = "Product Price: ₦0.00"
        self.amount_due_label.text = "Amount to Pay: ₦0.00"
        self.selected_product = None

    # ------------------ Navigation ------------------
    def goto_screen(self, screen_name):
        if screen_name in self.manager.screen_names:
            self.manager.current = screen_name
        else:
            print(f"[Warning] Screen '{screen_name}' not found in manager.")