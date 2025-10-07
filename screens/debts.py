# screens/debts.py
import json
from datetime import datetime
from PIL import Image as PILImage, ImageDraw, ImageFont
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
from utils.paths import get_file_path, get_export_path

DEBTS_FILE = get_file_path("debts.json")

class DebtsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_debts = []
        self.filtered_debts = []

        self.layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        self.add_widget(self.layout)

        # Title
        title = Label(text="📑 Unsettled Debts", font_size=sp(24), size_hint=(1, 0.1), color=(1,1,1,1))
        self.layout.add_widget(title)

        # Search bar
        self.search_input = TextInput(
            hint_text="Search by customer name...",
            multiline=False,
            size_hint=(1,0.1),
            font_size=sp(16)
        )
        self.search_input.bind(text=self.filter_debts)
        self.layout.add_widget(self.search_input)

        # Scrollable debts grid
        self.scroll = ScrollView(size_hint=(1, 0.75))
        self.grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=(0,dp(5)))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Back button
        btn_back = Button(text="⬅ Back", size_hint=(1,0.1), font_size=sp(16))
        btn_back.bind(on_release=self.go_back)
        self.layout.add_widget(btn_back)

    # -------------------- Lifecycle --------------------
    def on_pre_enter(self):
        self.load_debts()

    # -------------------- JSON Helpers --------------------
    def load_json(self):
        try:
            with open(DEBTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Loading debts.json: {e}")
            return {"debts": []}

    def save_json(self, data):
        with open(DEBTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_debts(self):
        data = self.load_json()
        existing = data.get("debts", [])
        for debt in self.all_debts:
            for i, d in enumerate(existing):
                if (
                    d["buyer"] == debt["buyer"]
                    and d["product"] == debt["product"]
                    and d["date"] == debt["date"]
                ):
                    existing[i] = debt
                    break
            else:
                existing.append(debt)
        data["debts"] = existing
        self.save_json(data)

    # -------------------- Load & Display --------------------
    def load_debts(self):
        data = self.load_json()
        self.all_debts = [d for d in data.get("debts", []) if d.get("debt", 0) > 0]
        self.filtered_debts = self.all_debts[:]
        self.display_debts()

    def display_debts(self):
        self.grid.clear_widgets()
        if not self.filtered_debts:
            self.grid.add_widget(Label(text="No unsettled debts found.", size_hint_y=None, height=dp(40)))
            return

        for debt in self.filtered_debts:
            row = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10), padding=dp(10))
            with row.canvas.before:
                Color(0.15,0.15,0.2,1)
                rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
            row.bg_rect = rect
            row.bind(pos=self.update_rect, size=self.update_rect)

            label = Label(
                text=f"{debt.get('buyer','Unknown')} | {debt.get('product','N/A')} | ₦{debt.get('debt',0):.2f}",
                halign="left", valign="middle", font_size=sp(16), color=(1,1,1,1)
            )
            label.bind(size=label.setter("text_size"))
            row.add_widget(label)

            btn_view = Button(text="View", size_hint=(None,1), width=dp(80))
            btn_view.bind(on_release=lambda inst, d=debt: self.open_debt_popup(d))
            row.add_widget(btn_view)

            btn_update = Button(text="Update", size_hint=(None,1), width=dp(80))
            btn_update.bind(on_release=lambda inst, d=debt: self.pay_debt_popup(d))
            row.add_widget(btn_update)

            self.grid.add_widget(row)

    def update_rect(self, instance, value):
        if hasattr(instance, "bg_rect"):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

    # -------------------- Search --------------------
    def filter_debts(self, instance, text):
        text = text.strip().lower()
        self.filtered_debts = (
            self.all_debts if not text else [d for d in self.all_debts if text in d.get("buyer","").lower()]
        )
        self.display_debts()

    # -------------------- View / Export / History --------------------
    def open_debt_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        for key, value in debt.items():
            if key != "history":
                layout.add_widget(Label(text=f"{key.capitalize()}: {value}", size_hint_y=None, height=dp(30), font_size=sp(14)))

        for text, action in [
            ("Export Image", lambda inst: self.export_image(debt)),
            ("View History", lambda inst: self.show_history_popup(debt))
        ]:
            btn = Button(text=text, size_hint_y=None, height=dp(40))
            btn.bind(on_release=action)
            layout.add_widget(btn)

        btn_close = Button(text="Close", size_hint_y=None, height=dp(40))
        layout.add_widget(btn_close)
        popup = Popup(title="Debt Details", content=layout, size_hint=(0.85,0.85))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    # -------------------- Payment --------------------
    def pay_debt_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        layout.add_widget(Label(text=f"Current Debt: ₦{debt['debt']:.2f}", size_hint_y=None, height=dp(30), font_size=sp(14)))

        input_payment = TextInput(hint_text="Enter payment amount...", multiline=False, size_hint_y=None, height=dp(40))
        layout.add_widget(input_payment)

        btn_pay = Button(text="Pay", size_hint_y=None, height=dp(40))
        btn_cancel = Button(text="Cancel", size_hint_y=None, height=dp(40))
        layout.add_widget(btn_pay)
        layout.add_widget(btn_cancel)

        popup = Popup(title="Pay Debt", content=layout, size_hint=(0.75,0.55))
        btn_cancel.bind(on_release=popup.dismiss)

        def process_payment(inst):
            try:
                amount = float(input_payment.text)
                if amount <= 0:
                    return
            except:
                return

            debt["debt"] -= amount
            debt.setdefault("history", []).append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "paid": amount
            })

            if debt["debt"] <= 0 and debt in self.all_debts:
                self.all_debts.remove(debt)

            self.filtered_debts = self.all_debts[:]
            self.save_debts()
            self.display_debts()
            popup.dismiss()

        btn_pay.bind(on_release=process_payment)
        popup.open()

    # -------------------- Debt History --------------------
    def show_history_popup(self, debt):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        history = debt.get("history", [])
        if not history:
            layout.add_widget(Label(text="No history found.", size_hint_y=None, height=dp(30)))
        else:
            for record in history:
                layout.add_widget(Label(text=f"{record['date']}: Paid ₦{record['paid']:.2f}", size_hint_y=None, height=dp(30)))
        btn_close = Button(text="Close", size_hint_y=None, height=dp(40))
        layout.add_widget(btn_close)
        popup = Popup(title=f"{debt.get('buyer','Unknown')} Payment History", content=layout, size_hint=(0.85,0.85))
        btn_close.bind(on_release=popup.dismiss)
        popup.open()

    # -------------------- Export Image --------------------
    def export_image(self, debt):
        export_folder = get_export_path("debts")
        filename = f"debt_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        filepath = f"{export_folder}/{filename}"

        img = PILImage.new("RGB", (700, 400), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        y = 20
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()

        for key, value in debt.items():
            if key != "history":
                draw.text((20, y), f"{key.capitalize()}: {value}", fill="white", font=font)
                y += 30

        history = debt.get("history", [])
        if history:
            draw.text((20, y), "Payment History:", fill="white", font=font)
            y += 25
            for record in history:
                draw.text((20, y), f"{record['date']} → ₦{record['paid']:.2f}", fill="white", font=font)
                y += 25

        img.save(filepath)
        popup = Popup(title="Exported Image", content=Label(text=f"Debt exported to:\n{filepath}"), size_hint=(0.8,0.4))
        popup.open()

    # -------------------- Navigation --------------------
    def go_back(self, *args):
        if self.manager and "home" in self.manager.screen_names:
            self.manager.current = "home"