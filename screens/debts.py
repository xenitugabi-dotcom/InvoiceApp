# screens/debts.py
import os
import json
import csv
from datetime import datetime
from PIL import Image as PILImage, ImageDraw

from kivy.metrics import dp, sp
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle

# ✅ Unified JSON path
MAIN_JSON_FOLDER = "/storage/emulated/0/InvoiceApp/user_data"
os.makedirs(MAIN_JSON_FOLDER, exist_ok=True)
DEBT_FILE = os.path.join(MAIN_JSON_FOLDER, "debts.json")


class DebtsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_debts = []
        self.filtered_debts = []

        # Main layout
        self.layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))

        # Title
        self.title = Label(
            text="📑 Unsettled Debts",
            font_size=sp(22),
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1),
        )
        self.layout.add_widget(self.title)

        # Search bar
        self.search_input = TextInput(
            hint_text="Search by customer name...",
            multiline=False,
            size_hint=(1, 0.1),
            font_size=sp(16),
        )
        self.search_input.bind(text=self.filter_debts)
        self.layout.add_widget(self.search_input)

        # Scrollable debts list
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.debt_grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=(0, dp(5)))
        self.debt_grid.bind(minimum_height=self.debt_grid.setter("height"))
        self.scroll.add_widget(self.debt_grid)
        self.layout.add_widget(self.scroll)

        # Back button
        btn_back = Button(text="⬅ Back", size_hint=(1, 0.1), font_size=sp(16))
        btn_back.bind(on_release=lambda inst: setattr(self.manager, "current", "home"))
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.load_debts()

    # ✅ Load debts
    def load_debts(self):
        if os.path.exists(DEBT_FILE):
            try:
                with open(DEBT_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "debts" in data:
                        debts = data["debts"]
                    elif isinstance(data, list):
                        debts = data
                    else:
                        debts = []
                    self.all_debts = [d for d in debts if d.get("debt", 0) > 0]
            except Exception as e:
                print("Error loading debts:", e)
                self.all_debts = []
        else:
            self.all_debts = []

        self.filtered_debts = self.all_debts[:]
        self.display_debts()

    # ✅ Save debts
    def save_debts(self):
        data = {"debts": self.all_debts}
        with open(DEBT_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # ✅ Filter debts
    def filter_debts(self, instance, text):
        text = text.strip().lower()
        if not text:
            self.filtered_debts = self.all_debts[:]
        else:
            self.filtered_debts = [
                debt for debt in self.all_debts
                if text in debt.get("buyer", "").lower()
            ]
        self.display_debts()

    # ✅ Display debts
    def display_debts(self):
        self.debt_grid.clear_widgets()

        if not self.filtered_debts:
            self.debt_grid.add_widget(
                Label(text="No unsettled debts found.", size_hint_y=None, height=dp(40))
            )
            return

        for debt in self.filtered_debts:
            buyer = debt.get("buyer", "Unknown")
            product = debt.get("product", "N/A")
            amount = debt.get("debt", 0.0)

            # Debt card container
            row_box = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10), padding=dp(10), orientation="horizontal")

            # Background
            row_box.canvas.before.clear()
            with row_box.canvas.before:
                Color(0.15, 0.15, 0.2, 1)
                rect = RoundedRectangle(pos=row_box.pos, size=row_box.size, radius=[10])
            row_box.bg_rect = rect
            row_box.bind(pos=self.update_rect, size=self.update_rect)

            # Debt info
            label = Label(
                text=f"{buyer} | {product} | ₦{amount:.2f}",
                halign="left",
                valign="middle",
                font_size=sp(16),
                color=(1, 1, 1, 1),
            )
            label.bind(size=label.setter("text_size"))
            row_box.add_widget(label)

            # View button
            btn_view = Button(text="View", size_hint=(None, 1), width=dp(80), font_size=sp(14))
            btn_view.bind(on_release=lambda inst, d=debt: self.open_debt_popup(d))
            row_box.add_widget(btn_view)

            # Update button
            btn_update = Button(text="Update", size_hint=(None, 1), width=dp(80), font_size=sp(14))
            btn_update.bind(on_release=lambda inst, d=debt: self.pay_debt_popup(d))
            row_box.add_widget(btn_update)

            self.debt_grid.add_widget(row_box)

    def update_rect(self, instance, value):
        if hasattr(instance, "bg_rect"):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    # --- Debt Popup ---
    def open_debt_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        for key, value in debt.items():
            if key != "history":
                layout.add_widget(Label(text=f"{key.capitalize()}: {value}", size_hint_y=None, height=dp(30), font_size=sp(14)))

        # Buttons
        for text, action in [
            ("Export Image", lambda inst: self.export_image(debt)),
            ("Export CSV", lambda inst: self.export_csv(debt)),
            ("View History", lambda inst: self.show_history_popup(debt)),
        ]:
            btn = Button(text=text, size_hint_y=None, height=dp(40), font_size=sp(14))
            btn.bind(on_release=action)
            layout.add_widget(btn)

        btn_close = Button(text="Close", size_hint_y=None, height=dp(40), font_size=sp(14))
        layout.add_widget(btn_close)

        popup = Popup(title="Debt Details", content=layout, size_hint=(0.85, 0.85))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    # --- Export Functions ---
    def export_image(self, debt):
        filename = os.path.join(MAIN_JSON_FOLDER, f"debt_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        img = PILImage.new("RGB", (500, 300), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        y = 20
        for key, value in debt.items():
            if key != "history":
                draw.text((20, y), f"{key.capitalize()}: {value}", fill="white")
                y += 30
        img.save(filename)
        print("Image exported:", filename)

    def export_csv(self, debt):
        filename = os.path.join(MAIN_JSON_FOLDER, f"debt_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for key, value in debt.items():
                if key != "history":
                    writer.writerow([key, value])
        print("CSV exported:", filename)

    # --- Payment Update ---
    def pay_debt_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"Current Debt: ₦{debt['debt']:.2f}", size_hint_y=None, height=dp(30), font_size=sp(14)))

        input_payment = TextInput(hint_text="Enter payment amount...", multiline=False, size_hint_y=None, height=dp(40), font_size=sp(14))
        layout.add_widget(input_payment)

        btn_pay = Button(text="Pay", size_hint_y=None, height=dp(40), font_size=sp(14))
        layout.add_widget(btn_pay)

        btn_cancel = Button(text="Cancel", size_hint_y=None, height=dp(40), font_size=sp(14))
        layout.add_widget(btn_cancel)

        popup = Popup(title="Pay Debt", content=layout, size_hint=(0.75, 0.55))
        btn_cancel.bind(on_release=popup.dismiss)

        def process_payment(inst):
            try:
                amount_paid = float(input_payment.text)
                if amount_paid <= 0:
                    return
            except:
                return

            debt["debt"] -= amount_paid
            # Update history
            if "history" not in debt:
                debt["history"] = []
            debt["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "paid": amount_paid
            })

            # Fully repaid
            if debt["debt"] <= 0:
                self.all_debts.remove(debt)

            self.filtered_debts = self.all_debts[:]
            self.save_debts()
            self.display_debts()
            popup.dismiss()

        btn_pay.bind(on_release=process_payment)
        popup.open()

    # --- History Popup ---
    def show_history_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        history = debt.get("history", [])
        if not history:
            layout.add_widget(Label(text="No history found.", size_hint_y=None, height=dp(30), font_size=sp(14)))
        else:
            for record in history:
                layout.add_widget(Label(text=f"{record['date']}: Paid ₦{record['paid']:.2f}", size_hint_y=None, height=dp(30), font_size=sp(14)))

        btn_close = Button(text="Close", size_hint_y=None, height=dp(40), font_size=sp(14))
        layout.add_widget(btn_close)

        popup = Popup(title=f"{debt.get('buyer', 'Unknown')} Payment History", content=layout, size_hint=(0.85, 0.85))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()