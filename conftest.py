import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# (opțional, doar dacă vrei să forțezi un Service manual)
# from selenium.webdriver.chrome.service import Service

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # rulează fără UI în CI / local
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")

    # Dacă runnerul setează CHROME_PATH (de ex. cu setup-chrome), respectă-l
    chrome_path = os.getenv("CHROME_PATH")
    if chrome_path:
        opts.binary_location = chrome_path

    # Selenium Manager descarcă și potrivește driverul automat.
    # IMPORTANT: nu trimite NIMIC pozițional înainte de 'options='.
    driver = webdriver.Chrome(options=opts)

    yield driver
    driver.quit()
