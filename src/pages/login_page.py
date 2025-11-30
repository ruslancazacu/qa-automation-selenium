from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LoginPage:
    URL = "https://www.saucedemo.com/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.URL)
        # login button prezent -> pagina încărcată
        self.wait.until(EC.visibility_of_element_located((By.ID, "login-button")))

    def login(self, username: str, password: str):
        user = self.wait.until(EC.element_to_be_clickable((By.ID, "user-name")))
        pwd  = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
        btn  = self.wait.until(EC.element_to_be_clickable((By.ID, "login-button")))

        user.clear(); user.send_keys(username)
        pwd.clear();  pwd.send_keys(password)
        btn.click()

    def error_text(self, timeout: int = 6) -> str:
        """Returnează textul de eroare de pe login (sau string gol dacă nu apare)."""
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-test="error"]'))
            )
            return el.text.strip()
        except TimeoutException:
            return ""
