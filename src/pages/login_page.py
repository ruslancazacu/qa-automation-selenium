from selenium.webdriver.common.by import By

class LoginPage:
    URL = "https://www.saucedemo.com/"
    USER = (By.ID, "user-name")
    PASS = (By.ID, "password")
    BTN  = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver):
        self.d = driver

    def open(self):
        self.d.get(self.URL)

    def login(self, username: str, password: str):
        self.d.find_element(*self.USER).clear()
        self.d.find_element(*self.USER).send_keys(username)
        self.d.find_element(*self.PASS).clear()
        self.d.find_element(*self.PASS).send_keys(password)
        self.d.find_element(*self.BTN).click()
