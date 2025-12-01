from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = 25  # puțin mai mare pentru CI

def test_checkout_complete_flow(driver):
    wait = W(driver, TIMEOUT)

    # 1) Login
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()

    # Inventar încărcat
    wait.until(EC.visibility_of_element_located((By.ID, "inventory_container")))

    # 2) Adaugă în coș + mergi la coș
    wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack"))).click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()

    # Pagina de coș este vizibilă (nu ne bazăm pe URL, ci pe element)
    wait.until(EC.visibility_of_element_located((By.ID, "cart_contents_container")))
    wait.until(EC.element_to_be_clickable((By.ID, "checkout"))).click()

    # 3) Checkout Step One – așteptăm formularul (elemente specifice)
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("QA")
    driver.find_element(By.ID, "last-name").send_keys("Bot")
    driver.find_element(By.ID, "postal-code").send_keys("9000")
    driver.find_element(By.ID, "continue").click()

    # 4) Checkout Step Two – așteptăm butonul Finish (semnal clar că suntem pe step two)
    wait.until(EC.visibility_of_element_located((By.ID, "finish")))
