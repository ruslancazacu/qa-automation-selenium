from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL = "https://www.saucedemo.com/"
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    SUBMIT   = (By.ID, "login-button")
    ERROR    = (By.CSS_SELECTOR, "h3[data-test='error']")
    INVENTORY_TITLE = (By.CSS_SELECTOR, ".title")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)  # 30s pentru stabilitate

    def open(self):
        self.driver.get(self.URL)

    def login(self, user, pwd):
        self.wait.until(EC.element_to_be_clickable(self.USERNAME)).send_keys(user)
        self.driver.find_element(*self.PASSWORD).send_keys(pwd)
        self.driver.find_element(*self.SUBMIT).click()

    @property
    def inventory_loaded(self):
        try:
            self.wait.until(EC.visibility_of_element_located(self.INVENTORY_TITLE))
            return True
        except:
            return False

    def error_text(self):
        el = self.wait.until(EC.visibility_of_element_located(self.ERROR))
        return el.text
