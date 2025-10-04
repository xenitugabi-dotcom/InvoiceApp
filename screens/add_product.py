# screens/add_product.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from file_manager import load_json, save_json
from datetime import datetime
import os

GOODS_JSON = "goods.json"
PRODUCT_HISTORY_JSON = "product_history.json"

class AddProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Input fields
        self.name_input = TextInput(hint_text="Product Name", multiline=False)
        self.price_input = TextInput(hint_text="Price", multiline=False, input_filter='float')
        self.quantity_input = TextInput(hint_text="Quantity", multiline=False, input_filter='int')

        # Feedback message
        self.message = Label(text="", color=(0, 1, 0, 1), size_hint=(1, 0.2))

        # Buttons
        btn_save = Button(text="Save Product")
        btn_back = Button(text="Back")

        # Layout widgets
        layout.add_widget(Label(text="Add Product", font_size=22, size_hint=(1, 0.2)))
        layout.add_widget(self.name_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.quantity_input)
        layout.add_widget(btn_save)
        layout.add_widget(btn_back)
        layout.add_widget(self.message)

        self.add_widget(layout)

        # Bind events
        btn_save.bind(on_release=self.save_product)
        btn_back.bind(on_release=self.go_back)

    def go_back(self, instance):
        self.manager.current = 'home'

    def save_product(self, instance):
        name = self.name_input.text.strip()
        price = self.price_input.text.strip()
        quantity = self.quantity_input.text.strip()

        if not name or not price or not quantity:
            self.message.text = "Please fill all fields."
            self.message.color = (1, 0, 0, 1)
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            self.message.text = "Invalid price or quantity."
            self.message.color = (1, 0, 0, 1)
            return

        try:
            # Load goods and product history
            goods = load_json(GOODS_JSON, default={})
            history = load_json(PRODUCT_HISTORY_JSON, default={})
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if name in goods:
                # Restock existing product
                old_qty = goods[name].get("quantity", 0)
                old_price = goods[name].get("price", 0)

                goods[name]["quantity"] = old_qty + quantity
                goods[name]["price"] = price

                # Record structured history entry
                history.setdefault(name, []).append({
                    "date": now,
                    "action": "restock",
                    "quantity": quantity,
                    "price": price,
                    "note": f"{old_qty}→{old_qty + quantity}, price {old_price}→{price}"
                })
            else:
                # Add new product
                goods[name] = {
                    "price": price,
                    "quantity": quantity,
                    "description": "",
                    "image_path": ""
                }
                history.setdefault(name, []).append({
                    "date": now,
                    "action": "add",
                    "quantity": quantity,
                    "price": price,
                    "note": "Initial addition"
                })

            # Save updates
            save_json(GOODS_JSON, goods)
            save_json(PRODUCT_HISTORY_JSON, history)

            # Clear inputs and show success
            self.message.text = "Product saved!"
            self.message.color = (0, 1, 0, 1)
            self.name_input.text = ""
            self.price_input.text = ""
            self.quantity_input.text = ""

        except Exception as e:
            self.message.text = f"Error: {e}"
            self.message.color = (1, 0, 0, 1)