from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 20

def _js_click(driver, el):
    driver.execute_script("arguments[0].click();", el)

def test_checkout_complete_flow(driver):
    wait = W(driver, TIMEOUT)

    # 1) Login
    driver.get("https://www.saucedemo.com/")
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.url_contains("inventory.html"))

    # 2) Adaugă în coș (folosește ID-ul corect!)
    wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack"))).click()

    # Deschide coșul (JS click ca să ocolim orice overlay)
    cart_link = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link")))
    _js_click(driver, cart_link)
    wait.until(EC.url_contains("cart.html"))

    # 3) Start checkout
    checkout_btn = wait.until(EC.element_to_be_clickable((By.ID, "checkout")))
    _js_click(driver, checkout_btn)
    wait.until(EC.url_contains("checkout-step-one"))

    # 4) Completează Step One
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("QA")
    driver.find_element(By.ID, "last-name").send_keys("Bot")
    driver.find_element(By.ID, "postal-code").send_keys("9000")
    driver.find_element(By.ID, "continue").click()
    wait.until(EC.url_contains("checkout-step-two"))

    # 5) Finalizează comanda
    finish_btn = wait.until(EC.element_to_be_clickable((By.ID, "finish")))
    _js_click(driver, finish_btn)
    wait.until(EC.url_contains("checkout-complete"))

    thanks = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
    assert "THANK YOU" in thanks.text.upper()
