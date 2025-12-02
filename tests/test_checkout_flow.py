import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "60"))

LOC = {
    "user": (By.CSS_SELECTOR, '[data-test="username"]'),
    "pwd": (By.CSS_SELECTOR, '[data-test="password"]'),
    "login": (By.CSS_SELECTOR, '[data-test="login-button"]'),
    "inventory": (By.ID, "inventory_container"),

    "add_backpack": (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'),
    "badge": (By.CLASS_NAME, "shopping_cart_badge"),

    "cart_link": (By.CLASS_NAME, "shopping_cart_link"),
    "cart_container": (By.ID, "cart_contents_container"),
    "checkout": (By.CSS_SELECTOR, '[data-test="checkout"]'),

    "first": (By.CSS_SELECTOR, '[data-test="firstName"]'),
    "last": (By.CSS_SELECTOR,  '[data-test="lastName"]'),
    "zip": (By.CSS_SELECTOR,   '[data-test="postalCode"]'),
    "continue": (By.CSS_SELECTOR, '[data-test="continue"]'),
    "finish": (By.CSS_SELECTOR,   '[data-test="finish"]'),
    "complete_header": (By.CLASS_NAME, "complete-header"),
}

def _wait_dom_ready(driver, t=10):
    W(driver, t).until(lambda d: d.execute_script("return document.readyState") == "complete")

def _visible_or_present(driver, locator, t=TIMEOUT):
    try:
        return W(driver, t).until(EC.visibility_of_element_located(locator))
    except TimeoutException:
        return W(driver, t).until(EC.presence_of_element_located(locator))

def _safe_click(driver, locator, t=TIMEOUT):
    el = W(driver, t).until(EC.element_to_be_clickable(locator))
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)

def _goto_cart(driver, base=BASE_URL):
    """Click pe icon + fallback: navigare directă la /cart.html."""
    try:
        _safe_click(driver, LOC["cart_link"], t=10)
        _wait_dom_ready(driver, 10)
        W(driver, 10).until(EC.any_of(
            EC.url_contains("cart"),
            EC.presence_of_element_located(LOC["cart_container"]),
            EC.presence_of_element_located(LOC["checkout"]),
        ))
    except Exception:
        driver.get(base + "cart.html")
        _wait_dom_ready(driver, 10)
        W(driver, 10).until(EC.presence_of_element_located(LOC["cart_container"]))

def _open_checkout_step_one(driver, base=BASE_URL):
    """Click pe Checkout + fallback: navigare directă la /checkout-step-one.html."""
    try:
        _safe_click(driver, LOC["checkout"], t=10)
        W(driver, 8).until(EC.any_of(
            EC.url_contains("checkout-step-one"),
            EC.visibility_of_element_located(LOC["first"]),
        ))
    except Exception:
        driver.get(base + "checkout-step-one.html")
        _wait_dom_ready(driver, 10)
        W(driver, 10).until(EC.visibility_of_element_located(LOC["first"]))

def test_checkout_complete_flow(driver):
    w = W(driver, TIMEOUT)

    # 1) Login
    driver.get(BASE_URL)
    _wait_dom_ready(driver, 15)
    _visible_or_present(driver, LOC["user"], 15).send_keys("standard_user")
    driver.find_element(*LOC["pwd"]).send_keys("secret_sauce")
    _safe_click(driver, LOC["login"])
    w.until(EC.presence_of_element_located(LOC["inventory"]))

    # 2) Add to cart + badge=1
    _safe_click(driver, LOC["add_backpack"])
    w.until(EC.text_to_be_present_in_element(LOC["badge"], "1"))

    # 3) Cart (rezilient)
    _goto_cart(driver)

    # 4) Checkout Step One (rezilient)
    _open_checkout_step_one(driver)

    # 5) Completează formularul + finalizează
    driver.find_element(*LOC["first"]).send_keys("QA")
    driver.find_element(*LOC["last"]).send_keys("Auto")
    driver.find_element(*LOC["zip"]).send_keys("12345")
    _safe_click(driver, LOC["continue"])
    _safe_click(driver, LOC["finish"])

    # 6) Verifică succesul
    w.until(EC.url_contains("checkout-complete"))
    assert "Thank you for your order!" in driver.find_element(*LOC["complete_header"]).text
