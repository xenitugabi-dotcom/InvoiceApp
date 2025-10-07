import os
import json
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.behaviors import ButtonBehavior
from screens.product_details import ProductDetailsScreen  # ✅ Correct import
from utils.paths import GOODS_JSON_PATH


# ------------------------ Clickable Card ------------------------
class ClickableCard(ButtonBehavior, BoxLayout):
    """Clickable product card."""
    pass


# ------------------------ View Product Screen ------------------------
class ViewProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)

        # Background
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=lambda *_: setattr(self.bg_rect, 'size', self.layout.size))
        self.layout.bind(pos=lambda *_: setattr(self.bg_rect, 'pos', self.layout.pos))

        # 🔍 Search bar
        self.search_input = TextInput(
            hint_text="🔍 Search product by name...",
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.search_input.bind(text=self.on_search_text)
        self.layout.add_widget(self.search_input)

        # Scrollable grid for product cards
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=(0, 5))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Bottom buttons
        btn_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        btn_reload = Button(text="↻ Refresh", background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        btn_back = Button(text="⬅ Back", background_color=(0.15, 0.15, 0.15, 1), color=(1, 1, 1, 1))
        btn_reload.bind(on_release=lambda _: self.load_products())
        btn_back.bind(on_release=self.go_back)
        btn_box.add_widget(btn_reload)
        btn_box.add_widget(btn_back)
        self.layout.add_widget(btn_box)

        # Storage for products
        self.all_goods = {}

    # ------------------ JSON Helpers ------------------
    def load_goods(self):
        if os.path.exists(GOODS_JSON_PATH):
            with open(GOODS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_goods(self, data):
        os.makedirs(os.path.dirname(GOODS_JSON_PATH), exist_ok=True)
        with open(GOODS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ------------------ Lifecycle ------------------
    def on_enter(self):
        self.load_products()

    # ------------------ Product Display ------------------
    def on_search_text(self, instance, value):
        self.display_products(filter_text=value.strip().lower())

    def load_products(self):
        self.all_goods = self.load_goods()
        self.display_products()

    def display_products(self, filter_text=""):
        self.grid.clear_widgets()
        if not self.all_goods:
            self.grid.add_widget(Label(text="No products found.", color=(1, 1, 1, 1)))
            return

        count = 0
        for name, data in self.all_goods.items():
            if filter_text and filter_text not in name.lower():
                continue

            price = data.get("price", 0)
            quantity = data.get("quantity", 0)
            description = data.get("description", "")
            image_path = data.get("image_path", "")

            # Clickable Product Card
            card = ClickableCard(orientation="horizontal", size_hint_y=None, height=200, spacing=15, padding=10)
            with card.canvas.before:
                Color(0.08, 0.08, 0.08, 1)
                bg_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[15])
            card.bind(size=lambda inst, val, rect=bg_rect: setattr(rect, "size", val))
            card.bind(pos=lambda inst, val, rect=bg_rect: setattr(rect, "pos", val))

            # Product Image
            img_box = BoxLayout(size_hint=(None, 1), width=180)
            if image_path and os.path.exists(image_path):
                img = Image(source=image_path, size_hint=(None, None), size=(160, 160))
            else:
                img = Image(size_hint=(None, None), size=(160, 160))
                with img.canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    RoundedRectangle(size=img.size, pos=img.pos, radius=[10])
            img_box.add_widget(img)

            # Product Info
            info = BoxLayout(orientation="vertical", spacing=5)
            info.add_widget(Label(text=f"[b]{name}[/b]", markup=True, font_size=22, color=(1, 1, 1, 1)))
            info.add_widget(Label(text=f"₦{price}", font_size=20, color=(0.8, 0.8, 0.8, 1)))
            info.add_widget(Label(text=f"{quantity} in stock", font_size=18, color=(0.6, 0.9, 0.6, 1)))
            if description:
                info.add_widget(Label(text=description, font_size=16, color=(0.7, 0.7, 0.7, 1)))

            card.add_widget(img_box)
            card.add_widget(info)

            # Capture correct product in lambda using default arg
            card.bind(on_release=lambda inst, product_name=name: self.open_product_details(product_name))

            self.grid.add_widget(card)
            count += 1

        if count == 0:
            self.grid.add_widget(Label(text="No matching products found.", color=(1, 1, 1, 1)))

    # ------------------ Navigation ------------------
    def open_product_details(self, product_name):
        """Open the Product Details screen for the selected product."""
        if "product_details" not in self.manager.screen_names:
            self.manager.add_widget(ProductDetailsScreen(name="product_details"))

        detail_screen = self.manager.get_screen("product_details")
        detail_screen.load_product(product_name)
        self.manager.current = "product_details"

    def go_back(self, instance):
        self.manager.current = "home"