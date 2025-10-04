# screens/view_single_transaction.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from file_manager import get_file_path
import os
import csv

EXPORT_FOLDER = "exports"
EXPORT_PATH = get_file_path(EXPORT_FOLDER)
os.makedirs(EXPORT_PATH, exist_ok=True)

class ViewSingleTransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction = None

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Centered label for transaction info
        center_box = AnchorLayout(size_hint=(1, 0.6))
        self.label = Label(
            text="",
            halign="center",
            valign="middle",
            size_hint=(0.9, None),
            font_size=20,
            markup=True
        )
        self.label.bind(texture_size=self.label.setter('size'))
        center_box.add_widget(self.label)
        self.layout.add_widget(center_box)

        # Buttons
        btns = BoxLayout(size_hint=(1, 0.2), spacing=10)
        btn_csv = Button(text="Export to CSV")
        btn_csv.bind(on_release=self.export_csv)
        btn_img = Button(text="Export to Image")
        btn_img.bind(on_release=self.export_image)
        btn_back = Button(text="Back")
        btn_back.bind(on_release=self.go_back)

        btns.add_widget(btn_csv)
        btns.add_widget(btn_img)
        btns.add_widget(btn_back)
        self.layout.add_widget(btns)

        self.add_widget(self.layout)

    def display_transaction(self, txn):
        """Display a single transaction"""
        self.transaction = txn
        self.label.text = (
            f"[b]Date:[/b] {txn['date']}\n\n"
            f"[b]Buyer:[/b] {txn['buyer']}\n\n"
            f"[b]Product:[/b] {txn['product']}\n\n"
            f"[b]Quantity:[/b] {txn['quantity']}\n\n"
            f"[b]Total Price:[/b] ₦{txn.get('total_price', txn['amount_paid'] + txn['debt']):.2f}\n\n"
            f"[b]Amount Paid:[/b] ₦{txn['amount_paid']:.2f}\n\n"
            f"[b]Debt:[/b] ₦{txn['debt']:.2f}"
        )

    def export_csv(self, instance):
        if not self.transaction:
            return

        filename = f"{self.transaction['buyer'].replace(' ', '_')}_{self.transaction['date'].replace(':', '-')}.csv"
        filepath = os.path.join(EXPORT_PATH, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Buyer", "Product", "Quantity", "Total Price", "Amount Paid", "Debt", "Date"])
            writer.writerow([
                self.transaction["buyer"],
                self.transaction["product"],
                self.transaction["quantity"],
                self.transaction.get("total_price", self.transaction["amount_paid"] + self.transaction["debt"]),
                self.transaction["amount_paid"],
                self.transaction["debt"],
                self.transaction["date"]
            ])

        self.show_popup("CSV Exported", f"Saved as:\n{filepath}")

    def export_image(self, instance):
        if not self.transaction:
            return

        info = (
            f"Date: {self.transaction['date']}\n"
            f"Buyer: {self.transaction['buyer']}\n"
            f"Product: {self.transaction['product']}\n"
            f"Quantity: {self.transaction['quantity']}\n"
            f"Total Price: ₦{self.transaction.get('total_price', self.transaction['amount_paid'] + self.transaction['debt']):.2f}\n"
            f"Amount Paid: ₦{self.transaction['amount_paid']:.2f}\n"
            f"Debt: ₦{self.transaction['debt']:.2f}"
        )

        # Create PIL image
        img = Image.new("RGB", (800, 300), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        draw.multiline_text((20, 20), info, fill="black", font=font, spacing=10)

        filename = f"{self.transaction['buyer'].replace(' ', '_')}_{self.transaction['date'].replace(':', '-')}.png"
        filepath = os.path.join(EXPORT_PATH, filename)
        img.save(filepath)

        # Show in-app preview
        byte_io = BytesIO()
        img.save(byte_io, format='PNG')
        byte_io.seek(0)
        kivy_img = CoreImage(byte_io, ext='png').texture

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(KivyImage(texture=kivy_img))
        close_btn = Button(text="Close", size_hint_y=None, height=40)
        popup_layout.add_widget(close_btn)
        popup = Popup(title="Exported Image", content=popup_layout, size_hint=(0.9, 0.9))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message)
        btn = Button(text="OK", size_hint_y=None, height=40)
        content.add_widget(label)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.3))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'view_transactions'