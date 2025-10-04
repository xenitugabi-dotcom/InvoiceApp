# screens/view_product.py

import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle

from file_manager import load_json, save_json

# Centralized JSON files
GOODS_FILE = "goods.json"
GOODS_BACKUP_FILE = "goods_backup.json"
PRODUCT_HISTORY_FILE = "product_history.json"


class ViewProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Dark gray background
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=lambda *x: setattr(self.bg_rect, 'size', self.layout.size),
                         pos=lambda *x: setattr(self.bg_rect, 'pos', self.layout.pos))

        # Search bar
        search_bar = BoxLayout(size_hint_y=None, height=45, spacing=10)
        self.search_input = TextInput(
            hint_text="Search product...",
            multiline=False,
            foreground_color=(1, 1, 1, 1),
            background_normal='',
            background_active='',
            background_color=(0.15, 0.15, 0.15, 1),
            padding=(10, 10),
            halign="left"
        )
        btn_search = Button(
            text="🔍",
            size_hint_x=None,
            width=60,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        btn_search.bind(on_release=self.search_product)
        search_bar.add_widget(self.search_input)
        search_bar.add_widget(btn_search)
        self.layout.add_widget(search_bar)

        # Scroll and grid
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=(0, 5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        # Backup/Restore buttons
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_backup = Button(text="Backup", background_normal='', background_color=(0.15, 0.15, 0.15, 1), color=(1, 1, 1, 1))
        btn_restore = Button(text="Restore", background_normal='', background_color=(0.15, 0.15, 0.15, 1), color=(1, 1, 1, 1))
        btn_backup.bind(on_release=self.backup_goods)
        btn_restore.bind(on_release=self.restore_goods)
        btn_box.add_widget(btn_backup)
        btn_box.add_widget(btn_restore)
        self.layout.add_widget(btn_box)

        # Back button
        self.btn_back = Button(text="Back", size_hint_y=None, height=50, background_normal='', background_color=(0.12, 0.12, 0.12, 1), color=(1, 1, 1, 1))
        self.btn_back.bind(on_release=self.go_back)
        self.layout.add_widget(self.btn_back)

        self.add_widget(self.layout)

    def on_enter(self):
        self.load_products()

    def open_detail_screen(self, product_name):
        detail_screen = self.manager.get_screen('product_detail')
        detail_screen.show_details(product_name)
        self.manager.current = 'product_detail'

    def load_products(self, filter_name=""):
        self.grid.clear_widgets()
        products = load_json(GOODS_FILE, default={})

        if not products:
            self.grid.add_widget(Label(text="No products found.", color=(1, 1, 1, 1)))
            return

        filter_name = filter_name.lower() if filter_name else ""

        for product_name, details in products.items():
            if filter_name and filter_name not in product_name.lower():
                continue

            outer_container = BoxLayout(size_hint_y=None, height=220, padding=(10, 0), orientation='horizontal')
            card = BoxLayout(size_hint_y=None, height=220, spacing=20, padding=(10, 10, 10, 10))

            with card.canvas.before:
                Color(0.05, 0.05, 0.05, 1)
                rect_bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[15])

            card.bind(size=lambda inst, val, rect=rect_bg: setattr(rect, 'size', val))
            card.bind(pos=lambda inst, val, rect=rect_bg: setattr(rect, 'pos', val))

            img_container = BoxLayout(size_hint=(None, 1), width=220)
            image_path = details.get("image_path", "")
            if image_path and os.path.exists(image_path):
                product_image = Image(source=image_path, size_hint=(None, None), size=(200, 200), allow_stretch=True, keep_ratio=True)
            else:
                product_image = Image(size_hint=(None, None), size=(200, 200), allow_stretch=True, keep_ratio=True)
                with product_image.canvas.before:
                    Color(0.2, 0.2, 0.2, 1)
                    RoundedRectangle(size=product_image.size, pos=product_image.pos, radius=[10])
            img_container.add_widget(product_image)

            info = BoxLayout(orientation='vertical', spacing=4, size_hint_x=0.6)
            info.add_widget(Label(text=f"[b]{product_name}[/b]", markup=True, size_hint_y=None, height=48, font_size=26, color=(1,1,1,1)))
            info.add_widget(Label(text=f"₦{details.get('price', 0)}", size_hint_y=None, height=36, font_size=22, color=(0.8,0.8,0.8,1)))
            info.add_widget(Label(text=f"{details.get('quantity',0)} in stock", size_hint_y=None, height=36, font_size=20, color=(0.5,0.8,0.5,1)))

            img_info_box = BoxLayout(spacing=15)
            img_info_box.add_widget(img_container)
            img_info_box.add_widget(info)

            btn_box = BoxLayout(size_hint_x=0.2, orientation='vertical', padding=(0,0,10,0))
            btn_box.add_widget(Label(size_hint_y=1))
            btn = Button(text="View", size_hint=(None,None), size=(80,40), background_normal='', background_color=(0.25,0.25,0.25,1), color=(1,1,1,1))
            btn.bind(on_release=lambda inst, name=product_name: self.open_detail_screen(name))
            btn_box.add_widget(btn)
            btn_box.add_widget(Label(size_hint_y=1))

            card.add_widget(img_info_box)
            card.add_widget(btn_box)
            outer_container.add_widget(card)
            self.grid.add_widget(outer_container)

        self.grid.do_layout()

    def search_product(self, instance):
        keyword = self.search_input.text.strip().lower()
        self.load_products(filter_name=keyword)

    def backup_goods(self, instance):
        products = load_json(GOODS_FILE, default={})
        if products:
            save_json(GOODS_BACKUP_FILE, products)
            self.grid.add_widget(Label(text="[Backup successful]", size_hint_y=None, height=30, color=(0,1,0,1)))

    def restore_goods(self, instance):
        backup_products = load_json(GOODS_BACKUP_FILE, default={})
        if backup_products:
            save_json(GOODS_FILE, backup_products)
            self.grid.add_widget(Label(text="[Restore successful — reloading...]", size_hint_y=None, height=30, color=(0,1,0,1)))
            self.load_products()

    def go_back(self, instance):
        self.manager.current = 'home'