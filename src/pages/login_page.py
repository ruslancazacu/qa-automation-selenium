# src/pages/login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL = "https://www.saucedemo.com/"

    # locatori
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    SUBMIT   = (By.ID, "login-button")
    ERROR    = (By.CSS_SELECTOR, "[data-test='error']")  # mesajul roșu
    INVENTORY = (By.CSS_SELECTOR, ".inventory_list")     # după login reușit

    def __init__(self, driver):
        self.driver = driver
        # crește timpul de așteptare ca să fim stabili local
        self.wait = WebDriverWait(driver, 20)

    def open(self):
        self.driver.get(self.URL)
        # câmpul user este vizibil = pagina e gata
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))

    def login(self, username, password):
        self.driver.find_element(*self.USERNAME).clear()
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()

    # helperi pentru aserții
    def inventory_loaded(self):
        """True când lista de produse e prezentă după login valid."""
        try:
            self.wait.until(EC.presence_of_element_located(self.INVENTORY))
            return True
        except Exception:
            return False

    def error_text(self):
        """Textul complet al mesajului de eroare după login greșit."""
        el = self.wait.until(EC.visibility_of_element_located(self.ERROR))
        return el.text
