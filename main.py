# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.home import HomeScreen
from screens.add_product import AddProductScreen
from screens.view_product import ViewProductScreen
from screens.record_sales import RecordSalesScreen
from screens.view_transactions import ViewTransactionsScreen
from screens.debts import DebtsScreen
from screens.view_single_transaction import ViewSingleTransactionScreen
from screens.product_history import ProductHistoryScreen
from screens.product_detail import ProductDetailScreen  # ✅ Add this

class InvoiceApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddProductScreen(name='add_product'))
        sm.add_widget(RecordSalesScreen(name='record_sales'))
        sm.add_widget(ViewProductScreen(name='view_product'))
        sm.add_widget(DebtsScreen(name='view_debts'))  # Only debts.py used
        sm.add_widget(ViewTransactionsScreen(name='view_transactions'))
        sm.add_widget(ViewSingleTransactionScreen(name='view_single_transaction'))
        sm.add_widget(ProductHistoryScreen(name='product_history'))
        sm.add_widget(ProductDetailScreen(name='product_detail'))
        return sm

if __name__ == '__main__':
    InvoiceApp().run()