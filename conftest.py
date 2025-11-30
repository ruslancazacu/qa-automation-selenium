import os, shutil, tempfile
import pytest
from selenium import webdriver

def _chrome_options():
    opts = webdriver.ChromeOptions()

    # headless dacă e setat în mediu (GH Actions) sau local dacă vrei
    if os.environ.get("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")

    # stabilitate CI / containere
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")

    # dezactivăm tot ce scoate pop-up de parole/autofill
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False
    })
    opts.add_argument("--disable-features=Translate,AutofillServerCommunication," +
                      "PasswordManagerOnboarding,SavePasswordBubble,OptInRlhOnboarding")
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # profil temporar unic (ștergem la teardown)
    tmp_profile = os.path.join(tempfile.gettempdir(), "scoped_dir")
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    return opts, tmp_profile

@pytest.fixture
def driver():
    opts, tmp_profile = _chrome_options()
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(2)          # mic implicit
    drv.set_page_load_timeout(30)
    drv.set_script_timeout(30)
    try:
        yield drv
    finally:
        drv.quit()
        shutil.rmtree(tmp_profile, ignore_errors=True)
