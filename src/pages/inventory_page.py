from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class InventoryPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_open(self) -> bool:
        """Ești logat dacă există lista de produse (inventory_list)."""
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
            )
            return True
        except TimeoutException:
            return False
