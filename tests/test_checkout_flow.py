# tests/test_checkout_flow.py
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
# în CI e mai lent; poate fi setat din ci.yml prin E2E_TIMEOUT
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


def _safe_click(driver, locator, attempts: int = 3, wait_seconds: int = 10):
    """Click robust: așteaptă clickability, încearcă normal, apoi JS-click ca fallback."""
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
                time.sleep(0.5)
    if last_exc:
        raise last_exc


def test_checkout_complete_flow(driver):
    w = W(driver, TIMEOUT)

    # 1) Login
    driver.get(BASE_URL)
    w.until(EC.visibility_of_element_located(LOC["user"])).send_keys("standard_user")
    driver.find_element(*LOC["pwd"]).send_keys("secret_sauce")
    driver.find_element(*LOC["login"]).click()
    w.until(EC.presence_of_element_located(LOC["inventory"]))

    # 2) Add to cart + badge=1
    _safe_click(driver, LOC["add_backpack"])
    w.until(EC.text_to_be_present_in_element(LOC["badge"], "1"))

    # 3) Cart – acceptăm oricare din semnalele că pagina e încărcată
    _safe_click(driver, LOC["cart_link"])
    w.until(EC.any_of(
        EC.url_contains("cart"),
        EC.presence_of_element_located(LOC["cart_container"]),
        EC.presence_of_element_located(LOC["checkout"])
    ))

    # 4) Checkout Step One (retry-safe pentru CI)
    _safe_click(driver, LOC["checkout"])
    for _ in range(2):
        try:
            W(driver, 5).until(EC.any_of(
                EC.url_contains("checkout-step-one"),
                EC.visibility_of_element_located(LOC["first"])
            ))
            break
        except Exception:
            _safe_click(driver, LOC["checkout"])

    # Form Step One
    w.until(EC.visibility_of_element_located(LOC["first"]))
    driver.find_element(*LOC["first"]).send_keys("QA")
    driver.find_element(*LOC["last"]).send_keys("Bot")
    driver.find_element(*LOC["zip"]).send_keys("9000")
    _safe_click(driver, LOC["cont"])

    # 5) Step Two -> Finish
    _safe_click(driver, LOC["finish"])

    # 6) Pagina de succes
    w.until(EC.visibility_of_element_located(LOC["complete_header"]))
