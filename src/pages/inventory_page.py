# src/pages/inventory_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InventoryPage:
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    # produs simplu pentru test: „Sauce Labs Backpack”
    ADD_BACKPACK_BTN   = (By.CSS_SELECTOR, '[data-test="add-to-cart-sauce-labs-backpack"]')
    CART_BADGE         = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK          = (By.CLASS_NAME, "shopping_cart_link")

    def __init__(self, driver):
        self.driver = driver
        # folosește timeout mai generos, rezolvă flakiness:
        self.wait = WebDriverWait(driver, 30)

    def loaded(self) -> bool:
        # Pagina e considerată „loaded” când containerul de produse devine vizibil
        self.wait.until(EC.visibility_of_element_located(self.INVENTORY_CONTAINER))
        return True

    def add_backpack(self):
        # click când butonul chiar e „clickable” (nu doar prezent)
        self.wait.until(EC.element_to_be_clickable(self.ADD_BACKPACK_BTN)).click()

    def cart_count(self) -> int:
        # după adăugare, insigna coșului trebuie să apară cu „1”
        try:
            badge = self.wait.until(EC.visibility_of_element_located(self.CART_BADGE))
            return int(badge.text.strip())
        except Exception:
            return 0
