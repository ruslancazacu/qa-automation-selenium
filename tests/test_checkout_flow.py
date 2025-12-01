from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as EC
import os

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = int(os.getenv("E2E_TIMEOUT", "40"))

def test_checkout_complete_flow(driver):
    wait = W(driver, TIMEOUT)

    # 1) Login
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys("standard_user")
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.ID, "inventory_container")))

    # 2) Adaugă în coș și mergi la coș
    wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack"))).click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.visibility_of_element_located((By.ID, "cart_contents_container")))
    wait.until(EC.element_to_be_clickable((By.ID, "checkout"))).click()

    # 3) Step One
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("QA")
    driver.find_element(By.ID, "last-name").send_keys("Bot")
    driver.find_element(By.ID, "postal-code").send_keys("9000")
    driver.find_element(By.ID, "continue").click()

    # 4) Step Two -> Finish
    wait.until(EC.element_to_be_clickable((By.ID, "finish"))).click()

    # 5) Pagina de succes
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
