# screens/view_single_transaction.py
import os
import csv
from io import BytesIO
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, RoundedRectangle
from PIL import Image, ImageDraw, ImageFont
from utils.paths import get_export_path

EXPORT_PATH = get_export_path()  # Ensure this returns a valid folder path

class ViewSingleTransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction = None

        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        self.add_widget(self.layout)

        # Background
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos, radius=[15])
        self.layout.bind(size=lambda *x: setattr(self.bg_rect, 'size', self.layout.size))
        self.layout.bind(pos=lambda *x: setattr(self.bg_rect, 'pos', self.layout.pos))

        # Scrollable transaction info
        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.info_label = Label(
            text="", font_size=18, markup=True,
            color=(1,1,1,1), halign="left", valign="top",
            size_hint_y=None, text_size=(self.width-40, None)
        )
        self.info_label.bind(texture_size=self.update_label_height)
        self.scroll.add_widget(self.info_label)
        self.layout.add_widget(self.scroll)

        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.btn_csv = Button(text="Export to CSV")
        self.btn_img = Button(text="Export to Image")
        self.btn_back = Button(text="Back")

        self.btn_csv.bind(on_release=self.export_csv)
        self.btn_img.bind(on_release=self.export_image)
        self.btn_back.bind(on_release=self.go_back)

        for btn in [self.btn_csv, self.btn_img, self.btn_back]:
            btn_layout.add_widget(btn)
        self.layout.add_widget(btn_layout)

    # ------------------ Helpers ------------------
    def update_label_height(self, instance, value):
        instance.height = instance.texture_size[1]

    def display_transaction(self, txn):
        """Display a single transaction with debt/payment history if present"""
        self.transaction = txn
        total_price = txn.get("total_price", txn["amount_paid"] + txn["debt"])
        info_text = (
            f"[b]Date:[/b] {txn['date']}\n\n"
            f"[b]Buyer:[/b] {txn['buyer']}\n\n"
            f"[b]Product:[/b] {txn['product']}\n\n"
            f"[b]Quantity:[/b] {txn['quantity']}\n\n"
            f"[b]Total Price:[/b] ₦{total_price:.2f}\n\n"
            f"[b]Amount Paid:[/b] ₦{txn['amount_paid']:.2f}\n\n"
            f"[b]Debt:[/b] ₦{txn['debt']:.2f}"
        )

        # Include debt/payment history if exists
        history = txn.get("history", [])
        if history:
            info_text += "\n\n[b]Payment History:[/b]"
            for entry in history:
                info_text += f"\n{entry['date']} → Paid: ₦{entry['paid']:.2f}"

        self.info_label.text = info_text

    # ------------------ Export Functions ------------------
    def export_csv(self, instance):
        if not self.transaction:
            return
        os.makedirs(EXPORT_PATH, exist_ok=True)
        safe_buyer = self.transaction['buyer'].replace(' ', '_')
        safe_date = self.transaction['date'].replace(':','-').replace(' ','_')
        filepath = os.path.join(EXPORT_PATH, f"{safe_buyer}_{safe_date}.csv")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Buyer", "Product", "Quantity", "Total Price",
                "Amount Paid", "Debt", "Date", "Payment History"
            ])
            history_text = "; ".join([f"{h['date']} → ₦{h['paid']:.2f}" for h in self.transaction.get("history", [])])
            writer.writerow([
                self.transaction["buyer"],
                self.transaction["product"],
                self.transaction["quantity"],
                self.transaction.get("total_price", self.transaction["amount_paid"] + self.transaction["debt"]),
                self.transaction["amount_paid"],
                self.transaction["debt"],
                self.transaction["date"],
                history_text
            ])
        self.show_popup("CSV Exported", f"Transaction saved as:\n{filepath}")

    def export_image(self, instance):
        if not self.transaction:
            return
        os.makedirs(EXPORT_PATH, exist_ok=True)
        total_price = self.transaction.get("total_price", self.transaction["amount_paid"] + self.transaction["debt"])
        info = (
            f"Date: {self.transaction['date']}\n"
            f"Buyer: {self.transaction['buyer']}\n"
            f"Product: {self.transaction['product']}\n"
            f"Quantity: {self.transaction['quantity']}\n"
            f"Total Price: ₦{total_price:.2f}\n"
            f"Amount Paid: ₦{self.transaction['amount_paid']:.2f}\n"
            f"Debt: ₦{self.transaction['debt']:.2f}"
        )

        history = self.transaction.get("history", [])
        if history:
            info += "\nPayment History:\n"
            for h in history:
                info += f"{h['date']} → ₦{h['paid']:.2f}\n"

        # Create PIL image
        img_height = 250 + 30*len(history)
        img = Image.new("RGB", (800, img_height), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 22)
        except:
            font = ImageFont.load_default()
        draw.multiline_text((20, 20), info, fill="black", font=font, spacing=10)

        safe_buyer = self.transaction['buyer'].replace(' ', '_')
        safe_date = self.transaction['date'].replace(':','-').replace(' ','_')
        filepath = os.path.join(EXPORT_PATH, f"{safe_buyer}_{safe_date}.png")
        img.save(filepath)

        # Preview in-app
        byte_io = BytesIO()
        img.save(byte_io, format='PNG')
        byte_io.seek(0)
        kivy_img = CoreImage(byte_io, ext='png').texture

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        scroll = ScrollView()
        image_widget = KivyImage(texture=kivy_img, allow_stretch=True, keep_ratio=True)
        scroll.add_widget(image_widget)
        popup_layout.add_widget(scroll)
        close_btn = Button(text="Close", size_hint_y=None, height=40)
        popup_layout.add_widget(close_btn)

        popup = Popup(title="Exported Image", content=popup_layout, size_hint=(0.9,0.9))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    # ------------------ Popup Helper ------------------
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        lbl = Label(text=message, halign="center", valign="middle")
        lbl.bind(size=lbl.setter('text_size'))
        btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(lbl)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8,0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        if 'view_transactions' in self.manager.screen_names:
            self.manager.get_screen('view_transactions').display_transactions()
        self.manager.current = 'view_transactions'