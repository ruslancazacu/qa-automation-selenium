# conftest.py
import os
import shutil
import tempfile
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def driver():
    # profil Chrome TEMPORAR (gol) ca să nu moștenească setări/sync
    tmp_profile = tempfile.mkdtemp(prefix="selenium-profile-")

    opts = Options()
    if os.environ.get("HEADLESS") == "1":
        opts.add_argument("--headless=new")

    # robust pentru CI/Windows
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--incognito")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--user-data-dir=" + tmp_profile)

    # oprește complet password manager + leak detection + baloane
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "signin.allowed": False,
        "profile.default_content_setting_values.notifications": 2,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)
    # dezactivează direct feature-urile de password manager/leak
    opts.add_argument(
        "--disable-features=PasswordManagerOnboarding,PasswordManagerRedesign,"
        "PasswordLeakDetection,OptimizationHints"
    )

    drv = webdriver.Chrome(options=opts)
    try:
        yield drv
    finally:
        drv.quit()
        # curăță profilul temporar
        shutil.rmtree(tmp_profile, ignore_errors=True)
