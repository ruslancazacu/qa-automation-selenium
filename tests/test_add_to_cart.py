from src.pages.login_page import LoginPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_add_to_cart(driver):
    # login
    lp = LoginPage(driver)
    lp.open()
    lp.login("standard_user", "secret_sauce")

    # inventar încărcat
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.ID, "inventory_container")))

    # adaugă primul produs în coș
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn_inventory")
    assert buttons, "Nu am găsit butoanele 'Add to cart'"
    buttons[0].click()

    # badge coș = 1
    badge = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
    assert badge.text == "1"
