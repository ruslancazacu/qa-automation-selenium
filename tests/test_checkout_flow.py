import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _safe_click(driver, locator, timeout=15):
    wait = WebDriverWait(driver, timeout)
    el = wait.until(EC.presence_of_element_located(locator))
    # adu în vizor
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        wait.until(EC.element_to_be_clickable(locator)).click()
    except Exception:
        # fallback JS click
        driver.execute_script("arguments[0].click();", el)

@pytest.mark.order(30)  # poți elimina linia dacă nu ai pytest-order instalat
def test_checkout_complete_flow(driver):
    wait = WebDriverWait(driver, 20)

    # Login
    driver.get("https://www.saucedemo.com/")
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.url_contains("inventory.html"))

    # Add to cart
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'))

    # Cart
    _safe_click(driver, (By.ID, "shopping_cart_container"))
    wait.until(EC.url_contains("cart.html"))

    # Checkout
    _safe_click(driver, (By.ID, "checkout"))
    wait.until(EC.url_contains("checkout-step-one.html"))

    # Form
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("Ruslan")
    driver.find_element(By.ID, "last-name").send_keys("Cazacu")
    driver.find_element(By.ID, "postal-code").send_keys("9000")
    _safe_click(driver, (By.ID, "continue"))
    wait.until(EC.url_contains("checkout-step-two.html"))

    # Finish (cu scroll + JS fallback)
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="finish"]'))

    # Confirmare
    wait.until(EC.url_contains("checkout-complete"))
    thanks = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
    assert thanks.text.strip() == "Thank you for your order!"
