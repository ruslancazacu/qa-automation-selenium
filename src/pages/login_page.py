from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL = "https://www.saucedemo.com/"

    # Locators
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    SUBMIT   = (By.ID, "login-button")
    ERROR    = (By.CSS_SELECTOR, "h3[data-test='error']")
    INVENTORY_CONTAINER = (By.ID, "inventory_container")

    def __init__(self, driver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, 30)  # mărim puțin pentru stabilitate

    def open(self):
        self.driver.get(self.URL)

    def login(self, user, password):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME)).send_keys(user)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()

    def inventory_loaded(self) -> bool:
        # pagină cu produse după login reușit
        self.wait.until(EC.presence_of_element_located(self.INVENTORY_CONTAINER))
        return True

    def error_text(self) -> str:
        el = self.wait.until(EC.visibility_of_element_located(self.ERROR))
        return el.text or ""
