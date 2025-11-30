from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InventoryPage:
    URL = "https://www.saucedemo.com/inventory.html"

    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    CART_BADGE = (By.CSS_SELECTOR, ".shopping_cart_badge")

    ADD_BACKPACK = (By.ID, "add-to-cart-sauce-labs-backpack")
    REMOVE_BACKPACK = (By.ID, "remove-sauce-labs-backpack")

    def __init__(self, driver):
        self.drv = driver

    def open(self):
        self.drv.get(self.URL)

    def loaded(self) -> bool:
        try:
            WebDriverWait(self.drv, 10).until(
                EC.presence_of_element_located(self.INVENTORY_LIST)
            )
            return True
        except Exception:
            return False

    def add_backpack(self):
        # click pe Add
        WebDriverWait(self.drv, 10).until(
            EC.element_to_be_clickable(self.ADD_BACKPACK)
        ).click()

        # așteptăm să apară butonul Remove (confirmă schimbarea stării)
        WebDriverWait(self.drv, 10).until(
            EC.presence_of_element_located(self.REMOVE_BACKPACK)
        )

        # așteptăm să se actualizeze badge-ul la 1
        WebDriverWait(self.drv, 10).until(
            EC.text_to_be_present_in_element(self.CART_BADGE, "1")
        )

    def cart_count(self) -> int:
        # citire robustă; dacă nu e badge, returnăm 0
        try:
            el = WebDriverWait(self.drv, 3).until(
                EC.presence_of_element_located(self.CART_BADGE)
            )
            txt = (el.text or "").strip()
            return int(txt) if txt.isdigit() else 0
        except Exception:
            return 0
