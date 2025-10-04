# screens/view_transactions.py
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from file_manager import load_json

TRANSACTIONS_JSON = "transactions.json"

class ViewTransactionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text="Transaction History", font_size=22, size_hint=(1, 0.1))
        self.layout.add_widget(title)

        # Search area
        search_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.product_input = TextInput(hint_text="Search by product")
        self.date_input = TextInput(hint_text="Search by date (YYYY-MM-DD)")
        btn_search = Button(text="Search")
        btn_search.bind(on_release=self.search_transactions)

        search_layout.add_widget(self.product_input)
        search_layout.add_widget(self.date_input)
        search_layout.add_widget(btn_search)
        self.layout.add_widget(search_layout)

        # Scroll area
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Back button
        btn_back = Button(text="Back", size_hint=(1, 0.1))
        btn_back.bind(on_release=self.go_back)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    # ------------------ Lifecycle ------------------
    def on_pre_enter(self):
        self.product_input.text = ""
        self.date_input.text = ""
        self.display_transactions()

    # ------------------ JSON Load ------------------
    def load_transactions(self):
        return load_json(TRANSACTIONS_JSON, default=[])

    # ------------------ Display ------------------
    def display_transactions(self, product_query="", date_query=""):
        self.grid.clear_widgets()
        transactions = self.load_transactions()
        if not transactions:
            self.grid.add_widget(Label(text="No transactions yet."))
            return

        filtered = [
            t for t in transactions
            if (product_query.lower() in t["product"].lower() if product_query else True)
            and (date_query in t["date"] if date_query else True)
        ]

        if not filtered:
            self.grid.add_widget(Label(text="No matching results."))
            return

        for txn in reversed(filtered):  # Latest first
            # Card container
            row_box = BoxLayout(size_hint_y=None, height=90, spacing=10, padding=10, orientation="horizontal")

            # Card background
            row_box.canvas.before.clear()
            with row_box.canvas.before:
                Color(0.15, 0.15, 0.15, 1)
                rect = RoundedRectangle(pos=row_box.pos, size=row_box.size, radius=[10])
            row_box.bg_rect = rect
            row_box.bind(pos=self.update_rect, size=self.update_rect)

            # Debt text and color
            debt_text = f" | Debt: ₦{txn['debt']:.2f}" if txn['debt'] > 0 else ""
            debt_color = (1, 0, 0, 1) if txn['debt'] > 0 else (1, 1, 1, 1)

            # Transaction info
            info = (
                f"{txn['date']}\n"
                f"{txn['buyer']} bought {txn['quantity']} x {txn['product']}\n"
                f"Paid: ₦{txn['amount_paid']:.2f}{debt_text}"
            )
            label = Label(text=info, halign="left", valign="middle", color=debt_color)
            label.bind(size=label.setter('text_size'))
            row_box.add_widget(label)

            # View button
            btn_view = Button(text="View", size_hint=(None, 1), width=100)
            btn_view.bind(on_release=lambda inst, t=txn: self.open_single_transaction(t))
            row_box.add_widget(btn_view)

            self.grid.add_widget(row_box)

    def update_rect(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    # ------------------ Search ------------------
    def search_transactions(self, instance):
        product_query = self.product_input.text.strip()
        date_query = self.date_input.text.strip()
        self.display_transactions(product_query, date_query)

    # ------------------ Single Transaction ------------------
    def open_single_transaction(self, txn):
        screen = self.manager.get_screen('view_single_transaction')
        screen.display_transaction(txn)
        self.manager.current = 'view_single_transaction'

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        self.manager.current = 'record_sales'