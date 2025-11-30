# tests/test_add_to_cart.py
from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage

def test_add_to_cart(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "secret_sauce")

    inv = InventoryPage(driver)
    assert inv.loaded() is True

    inv.add_backpack()
    assert inv.cart_count() == 1
