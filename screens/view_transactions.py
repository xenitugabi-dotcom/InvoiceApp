# screens/view_transactions.py
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from utils.paths import get_file_path  # ✅ Use same helper

class ViewTransactionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.add_widget(self.layout)

        # Title
        title = Label(
            text="📄 Transaction History",
            font_size=24,
            size_hint=(1, 0.1),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        self.layout.add_widget(title)

        # Search area
        search_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.product_input = TextInput(hint_text="Search by product", multiline=False)
        self.date_input = TextInput(hint_text="Search by date (YYYY-MM-DD)", multiline=False)
        btn_search = Button(text="Search", size_hint_x=None, width=100)
        btn_search.bind(on_release=self.search_transactions)
        search_layout.add_widget(self.product_input)
        search_layout.add_widget(self.date_input)
        search_layout.add_widget(btn_search)
        self.layout.add_widget(search_layout)

        # Scrollable transactions area
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=(0, 5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Back button
        btn_back = Button(text="⬅ Back", size_hint=(1, 0.05))
        btn_back.bind(on_release=self.go_back)
        self.layout.add_widget(btn_back)

    # ------------------ JSON Helpers ------------------
    def load_json(self, filename, default=None):
        path = get_file_path(filename)
        default = default or {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else default
        except Exception as e:
            print(f"[ERROR] Failed to load {filename}: {e}")
            return default

    # ------------------ Lifecycle ------------------
    def on_pre_enter(self):
        self.product_input.text = ""
        self.date_input.text = ""
        self.display_transactions()

    # ------------------ Display Transactions ------------------
    def display_transactions(self, product_query="", date_query=""):
        self.grid.clear_widgets()
        data = self.load_json("transactions.json", default={"sales": []})
        transactions = data.get("sales", [])

        if not transactions:
            self.grid.add_widget(Label(text="No transactions yet.", size_hint_y=None, height=40))
            return

        filtered = [
            t for t in transactions
            if (product_query.lower() in t.get("product", "").lower() if product_query else True)
            and (date_query in t.get("date", "") if date_query else True)
        ]

        if not filtered:
            self.grid.add_widget(Label(text="No matching results.", size_hint_y=None, height=40))
            return

        for txn in reversed(filtered):  # Show latest first
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=100,
                spacing=10,
                padding=10
            )
            # Background
            with card.canvas.before:
                Color(0.12, 0.12, 0.12, 1)
                card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
            card.bind(pos=lambda inst, val, rect=card.bg_rect: setattr(rect, 'pos', val))
            card.bind(size=lambda inst, val, rect=card.bg_rect: setattr(rect, 'size', val))

            # Info text
            debt = txn.get("debt", 0.0)
            debt_text = f" | Debt: ₦{debt:.2f}" if debt > 0 else ""
            debt_color = (1, 0, 0, 1) if debt > 0 else (1, 1, 1, 1)

            info_text = (
                f"{txn.get('date', '')}\n"
                f"{txn.get('buyer', '')} bought {txn.get('quantity', 0)} x {txn.get('product', '')}\n"
                f"Paid: ₦{txn.get('amount_paid', 0.0):.2f}{debt_text}"
            )
            info_label = Label(text=info_text, halign='left', valign='middle', color=debt_color)
            info_label.bind(size=info_label.setter('text_size'))
            card.add_widget(info_label)

            # View button
            btn_view = Button(text="View", size_hint=(None, 1), width=100)
            btn_view.bind(on_release=lambda inst, t=txn: self.open_single_transaction(t))
            card.add_widget(btn_view)

            self.grid.add_widget(card)

    # ------------------ Search ------------------
    def search_transactions(self, instance):
        product_query = self.product_input.text.strip()
        date_query = self.date_input.text.strip()
        self.display_transactions(product_query, date_query)

    # ------------------ Open Single Transaction ------------------
    def open_single_transaction(self, txn):
        if 'view_single_transaction' in self.manager.screen_names:
            screen = self.manager.get_screen('view_single_transaction')
            screen.display_transaction(txn)
            self.manager.current = 'view_single_transaction'

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        if 'record_sales' in self.manager.screen_names:
            self.manager.current = 'record_sales'