# screens/product_details.py
import os
import json
from datetime import datetime
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
from utils.paths import GOODS_JSON_PATH  # Centralized path

class ProductDetailsScreen(Screen):
    """Displays full product details, restock history, and actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_product_name = None

        # ===== MAIN LAYOUT =====
        self.layout = BoxLayout(orientation='vertical', spacing=15, padding=15)
        self.add_widget(self.layout)

        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=lambda *_: setattr(self.bg, "size", self.layout.size))
        self.layout.bind(pos=lambda *_: setattr(self.bg, "pos", self.layout.pos))

        # ===== IMAGE CAROUSEL =====
        self.carousel = Carousel(direction='right', loop=True, size_hint_y=0.4)
        self.layout.add_widget(self.carousel)

        # ===== INFO BOX =====
        self.info_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=180, spacing=25, padding=10)
        with self.info_box.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.info_bg = RoundedRectangle(size=self.info_box.size, pos=self.info_box.pos, radius=[15])
        self.info_box.bind(size=lambda *_: setattr(self.info_bg, "size", self.info_box.size))
        self.info_box.bind(pos=lambda *_: setattr(self.info_bg, "pos", self.info_box.pos))
        self.layout.add_widget(self.info_box)

        self.name_value = Label(font_size=26, bold=True, color=(1,1,1,1))
        self.price_value = Label(font_size=24, color=(0.8,0.8,0.8,1))
        self.quantity_value = Label(font_size=24, color=(0.5,0.9,0.5,1))

        def info_block(title, label, color):
            box = BoxLayout(orientation='vertical', spacing=3)
            box.add_widget(Label(text=title, font_size=18, color=color, size_hint_y=None, height=25))
            box.add_widget(label)
            return box

        self.info_box.add_widget(info_block("Name", self.name_value, (1,1,1,0.8)))
        self.info_box.add_widget(info_block("Price", self.price_value, (0.8,0.8,0.8,0.8)))
        self.info_box.add_widget(info_block("Quantity", self.quantity_value, (0.5,0.9,0.5,0.8)))

        # ===== DESCRIPTION =====
        self.desc_scroll = ScrollView(size_hint_y=0.4)
        self.description_label = Label(
            text="Description:", font_size=16, color=(0.9,0.9,0.9,1),
            halign="left", valign="top", size_hint_y=None
        )
        self.description_label.bind(texture_size=self._update_desc_height)
        self.desc_scroll.add_widget(self.description_label)
        self.layout.add_widget(self.desc_scroll)

        # ===== BUTTONS =====
        btn_box = BoxLayout(size_hint_y=None, height=70, spacing=15)
        self.btn_restock = Button(text="Restock / History", font_size=20)
        self.btn_add_photo = Button(text="Add Photo", font_size=20)
        self.btn_back = Button(text="Back", font_size=20)
        for b in [self.btn_restock, self.btn_add_photo, self.btn_back]:
            btn_box.add_widget(b)
        self.layout.add_widget(btn_box)

        self.btn_restock.bind(on_release=self._open_restock_popup)
        self.btn_add_photo.bind(on_release=self._add_photo)
        self.btn_back.bind(on_release=self._go_back)

    # ================= JSON HELPERS =================
    def _load_goods(self):
        if os.path.exists(GOODS_JSON_PATH):
            with open(GOODS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_goods(self, data):
        os.makedirs(os.path.dirname(GOODS_JSON_PATH), exist_ok=True)
        with open(GOODS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _update_desc_height(self, instance, value):
        instance.height = instance.texture_size[1]

    # ================= LOAD PRODUCT =================
    def load_product(self, product_name):
        self.current_product_name = product_name
        goods = self._load_goods()
        product = goods.get(product_name)

        if not product:
            self._clear_details()
            return

        self.name_value.text = product_name
        self.price_value.text = f"₦{product.get('price', 0)}"
        self.quantity_value.text = str(product.get('quantity', 0))
        self.description_label.text = f"Description:\n{product.get('description','No description available.')}"

        self.carousel.clear_widgets()
        img_path = product.get("image_path", "")
        if img_path and os.path.exists(img_path):
            self.carousel.add_widget(Image(source=img_path, allow_stretch=True))
        else:
            self.carousel.add_widget(Label(text="No image available.", color=(1,1,1,0.6)))

    def _clear_details(self):
        self.name_value.text = ""
        self.price_value.text = ""
        self.quantity_value.text = ""
        self.description_label.text = "Description:"
        self.carousel.clear_widgets()
        self.carousel.add_widget(Label(text="No image available.", color=(1,1,1,0.6)))

    # ================= RESTOCK / HISTORY =================
    def _open_restock_popup(self, instance):
        if not self.current_product_name:
            return

        goods = self._load_goods()
        product = goods.get(self.current_product_name, {})

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        qty_input = TextInput(hint_text="Enter quantity to add", input_filter="int", multiline=False)
        price_input = TextInput(hint_text="Enter new price", input_filter="float", multiline=False)
        btn_submit = Button(text="Submit")
        btn_history = Button(text="View History")
        btn_cancel = Button(text="Cancel")

        layout.add_widget(Label(text=f"Restock: {self.current_product_name}", size_hint_y=None, height=30))
        layout.add_widget(qty_input)
        layout.add_widget(price_input)
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        for b in [btn_submit, btn_history, btn_cancel]:
            btn_box.add_widget(b)
        layout.add_widget(btn_box)

        popup = Popup(title="Restock / Product History", content=layout, size_hint=(0.85,0.75))
        btn_cancel.bind(on_release=popup.dismiss)

        def submit(_):
            try:
                qty = int(qty_input.text.strip())
                price = float(price_input.text.strip())
            except:
                return
            if qty <= 0 or price <= 0:
                return
            old_qty = product.get("quantity",0)
            old_price = product.get("price",0)
            product["quantity"] = old_qty + qty
            product["price"] = price
            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": "restock",
                "quantity": qty,
                "price": price,
                "note": f"{old_qty}→{old_qty+qty}, ₦{old_price}→₦{price}"
            }
            product.setdefault("history", []).append(entry)
            goods[self.current_product_name] = product
            self._save_goods(goods)
            self.load_product(self.current_product_name)
            popup.dismiss()

        def view_history(_):
            history = product.get("history", [])
            msg = "No history available." if not history else "\n".join(
                f"{h['date']}: {h['action']} {h['quantity']} pcs @ ₦{h['price']} ({h.get('note','')})"
                for h in history
            )
            hist_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
            scroll = ScrollView()
            label = Label(text=msg, color=(1,1,1,1), size_hint_y=None)
            label.bind(texture_size=lambda inst, val: setattr(inst,"height",val[1]))
            scroll.add_widget(label)
            hist_layout.add_widget(scroll)
            back_btn = Button(text="Back", size_hint_y=None, height=40)
            hist_layout.add_widget(back_btn)
            hist_popup = Popup(title=f"{self.current_product_name} History", content=hist_layout, size_hint=(0.9,0.85))
            back_btn.bind(on_release=hist_popup.dismiss)
            hist_popup.open()

        btn_submit.bind(on_release=submit)
        btn_history.bind(on_release=view_history)
        popup.open()

    # ================= EXTRA BUTTONS =================
    def _add_photo(self, instance):
        # Placeholder for future image picker
        pass

    def _go_back(self, instance):
        if "view_product" in self.manager.screen_names:
            self.manager.get_screen("view_product").load_products()
        self.manager.current = "view_product"