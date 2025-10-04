# screens/product_detail.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
from file_manager import load_json, save_json
import os

GOODS_JSON = "goods.json"
PRODUCT_HISTORY_JSON = "product_history.json"

class ProductDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_product = None
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=15)
        self.add_widget(self.layout)

        # Background
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=lambda *x: setattr(self.bg_rect, 'size', self.layout.size),
                         pos=lambda *x: setattr(self.bg_rect, 'pos', self.layout.pos))

        # Carousel for images
        self.carousel = Carousel(direction='right', loop=True, size_hint_y=0.4)
        self.layout.add_widget(self.carousel)

        # Info box
        self.info_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=180, spacing=30, padding=10)
        with self.info_box.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.info_bg = RoundedRectangle(size=self.info_box.size, pos=self.info_box.pos, radius=[15])
        self.info_box.bind(size=lambda *x: setattr(self.info_bg, 'size', self.info_box.size),
                           pos=lambda *x: setattr(self.info_bg, 'pos', self.info_box.pos))
        self.layout.add_widget(self.info_box)

        self.name_value = Label(font_size=28, bold=True, color=(1,1,1,1), halign='center', valign='middle')
        self.price_value = Label(font_size=26, color=(0.8,0.8,0.8,1), halign='center', valign='middle')
        self.quantity_value = Label(font_size=26, color=(0.5,0.8,0.5,1), halign='center', valign='middle')

        def create_block(title, value_label, color):
            block = BoxLayout(orientation='vertical', size_hint_x=0.33, spacing=5)
            block.add_widget(Label(text=title, font_size=20, color=color, size_hint_y=None, height=30))
            block.add_widget(value_label)
            return block

        self.info_box.add_widget(create_block("Name", self.name_value, (1,1,1,0.8)))
        self.info_box.add_widget(create_block("Price", self.price_value, (0.8,0.8,0.8,0.8)))
        self.info_box.add_widget(create_block("Quantity", self.quantity_value, (0.5,0.8,0.5,0.8)))

        # Description
        self.desc_scroll = ScrollView(size_hint_y=0.4)
        self.description_label = Label(text='Description:', font_size=16, color=(0.9,0.9,0.9,1),
                                       halign='left', valign='top', size_hint_y=None)
        self.description_label.bind(texture_size=self.update_desc_height)
        self.desc_scroll.add_widget(self.description_label)
        self.layout.add_widget(self.desc_scroll)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=25, padding=(20,0))
        self.btn_restock = Button(text="Restock", font_size=20)
        self.btn_history = Button(text="View History", font_size=20)
        self.btn_add_photo = Button(text="Add Photo", font_size=20)
        self.btn_back = Button(text="Back", font_size=20)

        self.btn_restock.bind(on_release=self.restock)
        self.btn_history.bind(on_release=self.view_history)
        self.btn_add_photo.bind(on_release=self.add_photo)
        self.btn_back.bind(on_release=self.go_back)

        for btn in [self.btn_restock, self.btn_history, self.btn_add_photo, self.btn_back]:
            btn_layout.add_widget(btn)
        self.layout.add_widget(btn_layout)

    def update_desc_height(self, instance, value):
        instance.height = instance.texture_size[1]

    # ------------------ JSON ------------------
    def load_products(self):
        return load_json(GOODS_JSON, default={})

    def save_products(self, products):
        save_json(GOODS_JSON, products)

    def load_history(self):
        return load_json(PRODUCT_HISTORY_JSON, default={})

    def save_history(self, history):
        save_json(PRODUCT_HISTORY_JSON, history)

    # ------------------ Display Product ------------------
    def show_details(self, product_name):
        self.current_product = product_name
        products = self.load_products()
        product_data = products.get(product_name)
        if not product_data:
            self.clear_details()
            return

        self.name_value.text = product_name
        self.price_value.text = f"₦{product_data.get('price','N/A')}"
        self.quantity_value.text = str(product_data.get('quantity','N/A'))
        self.description_label.text = f"Description:\n{product_data.get('description','No description available.')}"
        self.carousel.clear_widgets()
        image_path = product_data.get('image_path','')
        if image_path and os.path.exists(image_path):
            self.carousel.add_widget(Image(source=image_path, allow_stretch=True, keep_ratio=True))
        else:
            self.carousel.add_widget(Label(text="No images available.", color=(1,1,1,0.7)))

    def clear_details(self):
        self.current_product = None
        self.name_value.text = self.price_value.text = self.quantity_value.text = ""
        self.description_label.text = "Description:"
        self.carousel.clear_widgets()
        self.carousel.add_widget(Label(text="No images available.", color=(1,1,1,0.7)))

    # ------------------ Restock Product ------------------
    def restock(self, instance):
        if not self.current_product:
            return

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        qty_input = TextInput(hint_text="Enter quantity to add", input_filter='int', multiline=False)
        price_input = TextInput(hint_text="Enter new price", input_filter='float', multiline=False)
        btn_submit = Button(text="Submit")
        btn_cancel = Button(text="Cancel")

        content.add_widget(Label(text=f"Restock {self.current_product}", size_hint_y=None, height=30))
        content.add_widget(qty_input)
        content.add_widget(price_input)

        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_box.add_widget(btn_submit)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)

        popup = Popup(title="Restock Product", content=content, size_hint=(0.8,0.6))
        btn_cancel.bind(on_release=popup.dismiss)

        def submit_restock(inst):
            try:
                qty = int(qty_input.text.strip())
                price = float(price_input.text.strip())
            except:
                return
            if qty <= 0 or price <= 0:
                return

            products = self.load_products()
            product_data = products.get(self.current_product, {})
            old_qty = product_data.get('quantity',0)
            old_price = product_data.get('price',0)
            product_data['quantity'] = old_qty + qty
            product_data['price'] = price
            products[self.current_product] = product_data
            self.save_products(products)

            self.quantity_value.text = str(product_data['quantity'])
            self.price_value.text = f"₦{price}"

            # Record structured history
            history = self.load_history()
            history.setdefault(self.current_product, []).append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "restock",
                "quantity": qty,
                "price": price,
                "note": f"{old_qty}→{old_qty+qty}, price {old_price}→{price}"
            })
            self.save_history(history)
            popup.dismiss()

        btn_submit.bind(on_release=submit_restock)
        popup.open()

    # ------------------ View History ------------------
    def view_history(self, instance):
        if not self.current_product:
            return

        # Open the ProductHistoryScreen
        from screens.product_history import ProductHistoryScreen
        self.manager.get_screen('product_history').load_history(self.current_product)
        self.manager.current = 'product_history'

    # ------------------ Add Photo ------------------
    def add_photo(self, instance):
        popup = Popup(title="Info", content=Label(text="Add Photo feature coming soon."), size_hint=(0.6,0.4))
        popup.open()

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        self.manager.current = "view_product"