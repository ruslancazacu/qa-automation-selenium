# tests/test_login.py
from src.pages.login_page import LoginPage

def test_successful_login(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "secret_sauce")
    assert lp.inventory_loaded() is True

def test_login_wrong_password(driver):
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "BAD_password")
    assert "epic sadface" in lp.error_text().lower()
