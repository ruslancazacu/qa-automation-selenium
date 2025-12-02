from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
import os, time

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "90"))

LOC = {
    "user": (By.CSS_SELECTOR, '[data-test="username"]'),
    "pwd": (By.CSS_SELECTOR,   '[data-test="password"]'),
    "login": (By.CSS_SELECTOR, '[data-test="login-button"]'),
    "inventory": (By.ID, "inventory_container"),

    "add_backpack": (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'),
    "cart_link": (By.CLASS_NAME, "shopping_cart_link"),
    "badge": (By.CLASS_NAME, "shopping_cart_badge"),
    "cart_container": (By.ID, "cart_contents_container"),
    "checkout": (By.CSS_SELECTOR, '[data-test="checkout"]'),

    "first": (By.CSS_SELECTOR, '[data-test="firstName"]'),
    "last":  (By.CSS_SELECTOR, '[data-test="lastName"]'),
    "zip":   (By.CSS_SELECTOR, '[data-test="postalCode"]'),
    "cont":  (By.CSS_SELECTOR, '[data-test="continue"]'),
    "finish": (By.CSS_SELECTOR, '[data-test="finish"]'),
    "done":   (By.CLASS_NAME, "complete-header"),
}

def _safe_click(drv, locator, attempts: int = 3):
    """Click cu wait + scroll + fallback JS (fiabil în headless/CI)."""
    w = W(drv, TIMEOUT)
    last = None
    for _ in range(attempts):
        el = w.until(EC.element_to_be_clickable(locator))
        try:
            drv.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass
        try:
            el.click()
            return
        except Exception as e:
            last = e
            try:
                drv.execute_script("arguments[0].click();", el)
                return
            except Exception as e2:
                last = e2
                time.sleep(0.3)
    raise last if last else RuntimeError("safe_click failed")

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

    # 3) Cart – așteptăm elementul paginii, NU URL-ul
    _safe_click(driver, LOC["cart_link"])
    w.until(EC.presence_of_element_located(LOC["cart_container"]))

    # 4) Checkout Step One – click robust, apoi firstName vizibil
    _safe_click(driver, LOC["checkout"])
    w.until(EC.visibility_of_element_located(LOC["first"]))
    driver.find_element(*LOC["first"]).send_keys("QA")
    driver.find_element(*LOC["last"]).send_keys("Bot")
    driver.find_element(*LOC["zip"]).send_keys("9000")
    _safe_click(driver, LOC["cont"])

    # 5) Finish + verificare succes
    _safe_click(driver, LOC["finish"])
    w.until(EC.visibility_of_element_located(LOC["done"]))
