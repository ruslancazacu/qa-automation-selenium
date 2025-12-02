from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
import os, time

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "90"))

def _safe_click(driver, locator, attempts: int = 3):
    """Click cu wait + fallback JS (robust în headless/CI)."""
    wait = W(driver, TIMEOUT)
    last_err = None
    for _ in range(attempts):
        el = wait.until(EC.element_to_be_clickable(locator))
        try:
            el.click()
            return
        except Exception as e:
            last_err = e
            # fallback JS click
            driver.execute_script("arguments[0].click();", el)
            time.sleep(0.2)
            return
    raise last_err if last_err else RuntimeError("safe_click failed")

def test_checkout_complete_flow(driver):
    wait = W(driver, TIMEOUT)

    # 1) Login (data-test selectors = mai stabile)
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="username"]'))).send_keys("standard_user")
    driver.find_element(By.CSS_SELECTOR, '[data-test="password"]').send_keys("secret_sauce")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-button"]').click()

    # inventar încărcat
    wait.until(EC.presence_of_element_located((By.ID, "inventory_container")))

    # 2) Adaugă în coș și verifică badge=1
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'))
    wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "shopping_cart_badge"), "1"))

    # 3) Mergi la coș (click robust) — așteptăm elementul specific paginii, NU URL-ul
    _safe_click(driver, (By.CLASS_NAME, "shopping_cart_link"))
    wait.until(EC.presence_of_element_located((By.ID, "cart_contents_container")))

    # 4) Checkout: Step One
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="checkout"]'))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="firstName"]'))).send_keys("QA")
    driver.find_element(By.CSS_SELECTOR, '[data-test="lastName"]').send_keys("Bot")
    driver.find_element(By.CSS_SELECTOR, '[data-test="postalCode"]').send_keys("9000")
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="continue"]'))

    # 5) Step Two -> Finish
    _safe_click(driver, (By.CSS_SELECTOR, '[data-test="finish"]'))

    # 6) Pagina de succes
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
