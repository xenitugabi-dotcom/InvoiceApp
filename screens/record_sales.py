# screens/record_sales.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
from file_manager import load_json, save_json

GOODS_JSON = "goods.json"
TRANSACTIONS_JSON = "transactions.json"
DEBTS_JSON = "debts.json"

class RecordSalesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.products = self.load_products()
        self.selected_price = 0.0

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Record Sales", font_size=22, size_hint=(1, 0.2)))

        self.buyer_input = TextInput(hint_text="Customer Name", multiline=False)
        self.product_input = TextInput(hint_text="Select Product", multiline=False, readonly=True)
        self.product_input.bind(on_touch_down=self.open_product_popup)

        self.product_price_label = Label(text="Product Price: ₦0.00")
        self.quantity_input = TextInput(hint_text="Quantity", input_filter='int', multiline=False)
        self.amount_due_label = Label(text="Amount to Pay: ₦0.00")
        self.amount_paid_input = TextInput(hint_text="Amount Paid", input_filter='float', multiline=False)
        self.message = Label(text="", size_hint=(1, 0.2))

        btn_record = Button(text="Record Sale")
        btn_view_transactions = Button(text="View Transactions")
        btn_back = Button(text="Back")

        for widget in [
            self.buyer_input, self.product_input, self.product_price_label,
            self.quantity_input, self.amount_due_label, self.amount_paid_input,
            btn_record, btn_view_transactions, btn_back, self.message
        ]:
            layout.add_widget(widget)

        self.add_widget(layout)

        self.quantity_input.bind(text=self.update_amount_due)
        btn_record.bind(on_release=self.record_sale)
        btn_view_transactions.bind(on_release=self.view_transactions)
        btn_back.bind(on_release=self.go_back)

    # ------------------ JSON Load/Save ------------------
    def load_products(self):
        goods = load_json(GOODS_JSON, default={})
        return [{"name": name, "price": data["price"], "quantity": data["quantity"]} for name, data in goods.items()]

    # ------------------ Product Selection ------------------
    def open_product_popup(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return

        self.products = self.load_products()  # Refresh products

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        search_input = TextInput(hint_text="Search product", multiline=False, size_hint_y=None, height=40)
        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)

        def populate_grid(filter_text=""):
            grid.clear_widgets()
            for product in self.products:
                if filter_text.lower() in product['name'].lower():
                    btn = Button(text=f"{product['name']} - ₦{product['price']}", size_hint_y=None, height=40)
                    btn.bind(on_release=lambda btn_inst, prod=product: select_product(prod))
                    grid.add_widget(btn)

        def select_product(product):
            self.product_input.text = product['name']
            self.selected_price = product['price']
            self.product_price_label.text = f"Product Price: ₦{self.selected_price:.2f}"
            self.update_amount_due()
            popup.dismiss()

        search_input.bind(text=lambda inst, val: populate_grid(val))
        popup_layout.add_widget(search_input)
        popup_layout.add_widget(scroll)

        btn_back_popup = Button(text="Back", size_hint_y=None, height=40)
        popup_layout.add_widget(btn_back_popup)
        popup = Popup(title="Select Product", content=popup_layout, size_hint=(0.9, 0.8))
        btn_back_popup.bind(on_release=popup.dismiss)
        populate_grid()
        popup.open()

    # ------------------ Update Amount ------------------
    def update_amount_due(self, *args):
        try:
            quantity = int(self.quantity_input.text)
            total = self.selected_price * quantity
            self.amount_due_label.text = f"Amount to Pay: ₦{total:.2f}"
        except:
            self.amount_due_label.text = "Amount to Pay: ₦0.00"

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        self.manager.current = 'home'

    def view_transactions(self, instance):
        self.manager.current = 'view_transactions'

    # ------------------ Record Sale ------------------
    def record_sale(self, instance):
        buyer = self.buyer_input.text.strip()
        product_name = self.product_input.text.strip()
        quantity_text = self.quantity_input.text.strip()
        paid_text = self.amount_paid_input.text.strip()

        if not all([buyer, product_name, quantity_text, paid_text]):
            self.message.text = "Please fill all fields."
            self.message.color = (1, 0, 0, 1)
            return

        try:
            quantity = int(quantity_text)
            paid = float(paid_text)
        except:
            self.message.text = "Invalid quantity or payment."
            self.message.color = (1, 0, 0, 1)
            return

        goods = load_json(GOODS_JSON, default={})
        product = goods.get(product_name)
        if not product or quantity > product["quantity"]:
            self.message.text = "Not enough stock."
            self.message.color = (1, 0, 0, 1)
            return

        total_price = self.selected_price * quantity
        debt_amount = max(total_price - paid, 0)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ----- Update Stock -----
        product["quantity"] -= quantity
        goods[product_name] = product
        save_json(GOODS_JSON, goods)

        # ----- Record Transaction -----
        transactions = load_json(TRANSACTIONS_JSON, default=[])
        transactions.append({
            "buyer": buyer,
            "product": product_name,
            "quantity": quantity,
            "total_price": total_price,
            "amount_paid": paid,
            "debt": debt_amount,
            "date": date_str
        })
        save_json(TRANSACTIONS_JSON, transactions)

        # ----- Record Debt if exists -----
        if debt_amount > 0:
            debts_data = load_json(DEBTS_JSON, default={"debts":[]})
            new_debt = {
                "buyer": buyer,
                "product": product_name,
                "quantity": quantity,
                "total_price": total_price,
                "amount_paid": paid,
                "debt": debt_amount,
                "date": date_str,
                "history": [{"date": date_str, "paid": paid}]
            }
            debts_data["debts"].append(new_debt)
            save_json(DEBTS_JSON, debts_data)

        # ----- Reset Fields -----
        self.message.text = "Sale recorded successfully."
        self.message.color = (0, 1, 0, 1)
        self.buyer_input.text = ""
        self.product_input.text = ""
        self.quantity_input.text = ""
        self.amount_paid_input.text = ""
        self.product_price_label.text = "Product Price: ₦0.00"
        self.amount_due_label.text = "Amount to Pay: ₦0.00"