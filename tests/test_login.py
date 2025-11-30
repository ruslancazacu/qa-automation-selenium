from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage

# https://www.saucedemo.com/
# user: standard_user | pass: secret_sauce

def test_successful_login(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "secret_sauce")
    inv = InventoryPage(driver)
    assert inv.is_loaded()

def test_login_wrong_password(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "BAD_password")
    assert "Epic sadface" in driver.page_source
