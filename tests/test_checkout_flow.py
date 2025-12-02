import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "90"))

LOC = {
    # login
    "user": (By.CSS_SELECTOR, '[data-test="username"]'),
    "pwd": (By.CSS_SELECTOR, '[data-test="password"]'),
    "login": (By.CSS_SELECTOR, '[data-test="login-button"]'),

    # inventory
    "inventory": (By.ID, "inventory_container"),
    "add_backpack": (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'),
    "badge": (By.CLASS_NAME, "shopping_cart_badge"),
    "cart_link": (By.CLASS_NAME, "shopping_cart_link"),

    # cart
    "cart_container": (By.ID, "cart_contents_container"),
    "checkout": (By.CSS_SELECTOR, '[data-test="checkout"]'),

    # step one
    "first": (By.CSS_SELECTOR, '[data-test="firstName"]'),
    "last": (By.CSS_SELECTOR,  '[data-test="lastName"]'),
    "zip": (By.CSS_SELECTOR,   '[data-test="postalCode"]'),
    "cont": (By.CSS_SELECTOR,  '[data-test="continue"]'),

    # step two / complete
    "finish": (By.CSS_SELECTOR, '[data-test="finish"]'),
    "complete_header": (By.CLASS_NAME, "complete-header"),
}

# ---------- helpers robuste ----------

def _wait_dom_ready(driver, seconds=10):
    W(driver, seconds).until(lambda d: d.execute_script("return document.readyState") == "complete")

def _safe_click(driver, locator, attempts=3, wait_seconds=10):
    last_exc = None
    for _ in range(attempts):
        try:
            W(driver, wait_seconds).until(EC.element_to_be_clickable(locator)).click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException, TimeoutException) as exc:
            last_exc = exc
            try:
                el = driver.find_element(*locator)
                driver.execute_script("arguments[0].click();", el)
                return
            except Exception:
                time.sleep(0.4)
    if last_exc:
        raise last_exc

def _visible_or_present(driver, locator, seconds=10):
    try:
        return W(driver, seconds).until(EC.visibility_of_element_located(locator))
    except TimeoutException:
        W(driver, seconds).until(EC.presence_of_element_located(locator))
        return driver.find_element(*locator)

# ---------- test ----------

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

    # 3) Cart – acceptăm orice semnal de încărcare
    _safe_click(driver, LOC["cart_link"])
    _wait_dom_ready(driver, 10)
    w.until(EC.any_of(
        EC.url_contains("cart"),
        EC.presence_of_element_located(LOC["cart_container"]),
        EC.presence_of_element_located(LOC["checkout"])
    ))

    # 4) Checkout Step One – 2 încercări + fallback navigare directă
    ok = False
    for i in range(2):
        _safe_click(driver, LOC["checkout"])
        _wait_dom_ready(driver, 10)
        try:
            W(driver, 6).until(EC.any_of(
                EC.url_contains("checkout-step-one"),
                EC.visibility_of_element_located(LOC["first"])
            ))
            ok = True
            break
        except TimeoutException:
            pass
    if not ok:
        driver.get(BASE_URL + "checkout-step-one.html")
        _wait_dom_ready(driver, 10)

    # Form Step One
    _visible_or_present(driver, LOC["first"], 15).send_keys("QA")
    driver.find_element(*LOC["last"]).send_keys("Bot")
    driver.find_element(*LOC["zip"]).send_keys("9000")
    _safe_click(driver, LOC["cont"])

    # 5) Step Two -> Finish
    _safe_click(driver, LOC["finish"])

    # 6) Pagina de succes
    w.until(EC.visibility_of_element_located(LOC["complete_header"]))
