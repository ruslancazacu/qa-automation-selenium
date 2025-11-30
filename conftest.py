import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")

    chrome_path = os.getenv("CHROME_PATH")
    if chrome_path:
        opts.binary_location = chrome_path

    driver = webdriver.Chrome(options=opts)
    yield driver
    driver.quit()
