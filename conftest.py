import os, shutil, tempfile
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def driver():
    opts = Options()

    # Headless doar în CI (sau dacă setezi manual HEADLESS=1)
    if os.getenv("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

    # mic tuning pentru stabilitate
    drv = webdriver.Chrome(options=opts)
    drv.set_window_size(1280, 900)
    drv.implicitly_wait(2)
    try:
        yield drv
    finally:
        drv.quit()
        # curăță profilul temporar eventual creat de Chrome
        tmp_profile = os.path.join(tempfile.gettempdir(), "scoped_dir")
        shutil.rmtree(tmp_profile, ignore_errors=True)
