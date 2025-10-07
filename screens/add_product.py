# screens/add_product.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.app import App

GOODS_JSON = "goods.json"

class AddProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Title
        layout.add_widget(Label(text="Add Product", font_size=22, size_hint=(1, 0.15)))

        # Input fields
        self.name_input = TextInput(hint_text="Product Name", multiline=False)
        self.price_input = TextInput(hint_text="Price", input_filter='float', multiline=False)
        self.quantity_input = TextInput(hint_text="Quantity", input_filter='int', multiline=False)
        self.description_input = TextInput(hint_text="Description", multiline=True, size_hint=(1, 0.2))

        layout.add_widget(self.name_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.quantity_input)
        layout.add_widget(self.description_input)

        # Buttons
        btn_save = Button(text="💾 Save Product", size_hint=(1, 0.15))
        btn_back = Button(text="↩ Back", size_hint=(1, 0.15))
        layout.add_widget(btn_save)
        layout.add_widget(btn_back)

        # Feedback label
        self.message = Label(text="", color=(0, 1, 0, 1), size_hint=(1, 0.15))
        layout.add_widget(self.message)

        self.add_widget(layout)

        # Bind buttons
        btn_save.bind(on_release=self.save_product)
        btn_back.bind(on_release=self.go_back)

    # ------------------ JSON Helpers ------------------
    def load_goods(self):
        """Load goods safely using App helper"""
        app = App.get_running_app()
        return app.load_json(GOODS_JSON, default={})

    def save_goods(self, goods):
        """Save goods safely using App helper"""
        app = App.get_running_app()
        app.save_json(GOODS_JSON, goods)

    # ------------------ Navigation ------------------
    def go_back(self, instance):
        """Return to HomeScreen and refresh products if needed"""
        if 'view_product' in self.manager.screen_names:
            try:
                self.manager.get_screen('view_product').load_products()
            except Exception as e:
                print(f"[Warning] Failed to refresh ViewProductScreen: {e}")
        self.manager.current = 'home'

    # ------------------ Save Product ------------------
    def save_product(self, instance):
        """Validate and save product"""
        name = self.name_input.text.strip()
        price_text = self.price_input.text.strip()
        quantity_text = self.quantity_input.text.strip()
        description = self.description_input.text.strip()

        if not name or not price_text or not quantity_text:
            self._show_message("⚠️ Please fill all required fields.", error=True)
            return

        try:
            price = float(price_text)
            quantity = int(quantity_text)
        except ValueError:
            self._show_message("⚠️ Invalid price or quantity.", error=True)
            return

        try:
            goods = self.load_goods()

            # Case-insensitive key lookup
            existing_key = next((k for k in goods if k.lower() == name.lower()), None)

            if existing_key:
                product = goods[existing_key]
                product['quantity'] = product.get('quantity', 0) + quantity
                product['price'] = price
                if description:
                    product['description'] = description
            else:
                goods[name] = {
                    'price': price,
                    'quantity': quantity,
                    'description': description,
                    'image_path': ""
                }

            self.save_goods(goods)
            self._clear_inputs()
            self._show_message(f"✅ Product '{name}' saved successfully!")

            # Refresh product list if screen exists
            if 'view_product' in self.manager.screen_names:
                self.manager.get_screen('view_product').load_products()

        except Exception as e:
            self._show_message(f"❌ Error: {e}", error=True)
            print(f"[Error] Failed to save product: {e}")

    # ------------------ Helper Methods ------------------
    def _clear_inputs(self):
        self.name_input.text = ""
        self.price_input.text = ""
        self.quantity_input.text = ""
        self.description_input.text = ""

    def _show_message(self, text, error=False):
        self.message.text = text
        self.message.color = (1, 0, 0, 1) if error else (0, 1, 0, 1)