import os
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

MAIN_JSON_FOLDER = "/storage/emulated/0/InvoiceApp/user_data"
PRODUCT_HISTORY_JSON = os.path.join(MAIN_JSON_FOLDER, "product_history.json")

class ProductHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.title = Label(text="", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=(5, 5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        btn_back = Button(text="Back", size_hint_y=None, height=50)
        btn_back.bind(on_release=self.go_back)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def load_history(self, product_name):
        """Load history entries from product_history.json."""
        self.grid.clear_widgets()
        self.title.text = f"History for {product_name}"

        if not os.path.exists(PRODUCT_HISTORY_JSON):
            self.grid.add_widget(Label(text="No history file found.", size_hint_y=None, height=40))
            return

        try:
            with open(PRODUCT_HISTORY_JSON, "r") as f:
                content = f.read().strip()
                data = json.loads(content) if content else {}
        except json.JSONDecodeError:
            self.grid.add_widget(Label(text="History file corrupted.", size_hint_y=None, height=40))
            return

        history = data.get(product_name, [])
        if not history:
            self.grid.add_widget(Label(text="No history found.", size_hint_y=None, height=40))
            return

        # Show latest first
        for entry in reversed(history):
            date = entry.get("date", "Unknown date")
            action = entry.get("action", "Update").capitalize()
            qty = entry.get("quantity", "-")
            price = entry.get("price", "-")
            note = entry.get("note", "")

            display_text = f"[b]{date}[/b] | Action: {action} | Qty: {qty} | ₦{price}"
            if note:
                display_text += f" | {note}"

            self.grid.add_widget(
                Label(
                    text=display_text,
                    markup=True,
                    size_hint_y=None,
                    height=40,
                    halign="left",
                    valign="middle",
                )
            )

    def go_back(self, instance):
        self.manager.current = 'view_product'