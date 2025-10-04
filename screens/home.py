import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp

# ✅ Base project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "icons")

def get_icon(filename):
    return os.path.join(ASSETS_DIR, filename)

# ✅ Custom button with responsive icon & text
class IconButton(ButtonBehavior, BoxLayout):
    def __init__(self, icon_path, text, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), padding=dp(8), **kwargs)
        self.icon_path = icon_path
        self.text = text
        self.size_hint = (1, 1)
        self.radius = [dp(12)]
        self.bg_color = (0.2, 0.5, 0.8, 1)  # blue
        self.pressed_color = (0.1, 0.4, 0.7, 1)
        self.current_color = self.bg_color

        # Background
        with self.canvas.before:
            Color(rgba=self.current_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # Icon
        self.image = Image(
            source=self.icon_path,
            size_hint=(1, 0.65),  # relative height
            allow_stretch=True,
            keep_ratio=True
        )

        # Label
        self.label = Label(
            text=self.text,
            size_hint=(1, 0.35),
            font_size=sp(14),
            halign='center',
            valign='middle'
        )
        self.label.bind(size=self.label.setter('text_size'))

        self.add_widget(self.image)
        self.add_widget(self.label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        self.current_color = self.pressed_color
        self.update_canvas()

    def on_release(self):
        self.current_color = self.bg_color
        self.update_canvas()

    def update_canvas(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.current_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=self.radius)

# ✅ Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Title
        title = Label(
            text='📋 Welcome to Somto Invoice',
            font_size=sp(22),
            size_hint=(1, 0.2),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)

        # Buttons Grid
        button_grid = GridLayout(cols=2, spacing=dp(12), size_hint=(1, 0.8))

        self.btn_add_product = IconButton(get_icon("add.png"), "Add Product")
        self.btn_record_sale = IconButton(get_icon("sales.png"), "Record Sales")
        self.btn_view_debts = IconButton(get_icon("debt.png"), "View Debt")
        self.btn_view_products = IconButton(get_icon("product.png"), "View Product")

        button_grid.add_widget(self.btn_add_product)
        button_grid.add_widget(self.btn_record_sale)
        button_grid.add_widget(self.btn_view_debts)
        button_grid.add_widget(self.btn_view_products)

        main_layout.add_widget(button_grid)
        self.add_widget(main_layout)

        # 🔗 Navigation
        self.btn_add_product.bind(on_release=lambda x: self.goto_screen('add_product'))
        self.btn_record_sale.bind(on_release=lambda x: self.goto_screen('record_sales'))
        self.btn_view_debts.bind(on_release=lambda x: self.goto_screen('view_debts'))
        self.btn_view_products.bind(on_release=lambda x: self.goto_screen('view_product'))

    def goto_screen(self, screen_name):
        self.manager.current = screen_name