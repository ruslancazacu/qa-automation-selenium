from src.pages.login_page import LoginPage
from src.pages.inventory_page import InventoryPage

def test_successful_login(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "secret_sauce")
    inv = InventoryPage(driver)
    assert inv.is_open()

def test_login_wrong_password(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "BAD_password")
    # așteaptă explicit mesajul de eroare, apoi verifică textul
    assert "epic sadface" in lp.error_text().lower()
