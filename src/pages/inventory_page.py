from selenium.webdriver.common.by import By

class InventoryPage:
    TITLE = (By.CSS_SELECTOR, ".app_logo")
    INVENTORY_GRID = (By.ID, "inventory_container")

    def __init__(self, driver):
        self.d = driver

    def is_loaded(self):
        return (self.d.find_element(*self.TITLE).is_displayed()
                and self.d.find_element(*self.INVENTORY_GRID).is_displayed())
