# conftest.py
import os, shutil, tempfile
import pytest
from selenium import webdriver

def _chrome_options():
    opts = webdriver.ChromeOptions()

    # headless când rulăm în CI sau dacă îl setezi local
    if os.environ.get("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")

    # stabilitate CI / containere
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--remote-debugging-port=0")  # permite mai multe instanțe

    # dezactivează parole/autofill/popups
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,
    })
    opts.add_argument("--disable-features=Translate,AutofillServerCommunication,"
                      "PasswordManagerOnboarding,SavePasswordBubble,OptInRlhOnboarding")
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # PROFIL UNIC / WORKER: evită ciocniri în xdist
    worker = os.getenv("PYTEST_XDIST_WORKER", "gw0")   # ex: gw0, gw1, ...
    tmp_profile = tempfile.mkdtemp(prefix=f"scoped_{worker}_")
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    return opts, tmp_profile

@pytest.fixture
def driver():
    opts, tmp_profile = _chrome_options()
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(3)
    drv.set_page_load_timeout(45)
    drv.set_script_timeout(45)
    try:
        yield drv
    finally:
        try:
            drv.quit()
        finally:
            shutil.rmtree(tmp_profile, ignore_errors=True)
