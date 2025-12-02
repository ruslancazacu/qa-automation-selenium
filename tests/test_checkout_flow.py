import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "90"))

def test_checkout_complete_flow(driver):
    wait = W(driver, TIMEOUT)

    # 1) Login
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="username"]'))).send_keys("standard_user")
    driver.find_element(By.CSS_SELECTOR, '[data-test="password"]').send_keys("secret_sauce")
    driver.find_element(By.CSS_SELECTOR, '[data-test="login-button"]').click()

    # confimăm încărcarea inventarului prin URL + container
    wait.until(EC.url_contains("/inventory"))
    wait.until(EC.presence_of_element_located((By.ID, "inventory_container")))

    # 2) Adaugă în coș rucsacul (data-test selector) și verifică badge=1
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]'))
    ).click()
    wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "shopping_cart_badge"), "1"))

    # mergi la coș
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("/cart"))
    wait.until(EC.visibility_of_element_located((By.ID, "cart_contents_container")))
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="checkout"]'))).click()

    # 3) Step One (form)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="firstName"]'))).send_keys("QA")
    driver.find_element(By.CSS_SELECTOR, '[data-test="lastName"]').send_keys("Bot")
    driver.find_element(By.CSS_SELECTOR, '[data-test="postalCode"]').send_keys("9000")
    driver.find_element(By.CSS_SELECTOR, '[data-test="continue"]').click()

    # 4) Step Two -> Finish
    wait.until(EC.url_contains("/checkout-step-two"))
    wait.until(EC.visibility_of_element_located((By.ID, "checkout_summary_container")))
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test="finish"]'))).click()

    # 5) Pagina de succes
    wait.until(EC.url_contains("/checkout-complete"))
    header = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
    assert "THANK YOU" in header.text.upper()
