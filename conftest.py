import os
import shutil
import tempfile
import pytest
from selenium import webdriver

def _chrome_options():
    opts = webdriver.ChromeOptions()

    # headless dacă e setat în mediu (GH Actions sau local)
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
    opts.add_argument(
        "--disable-features=Translate,AutofillServerCommunication,"
        "PasswordManagerOnboarding,SavePasswordBubble,OptInRlhOnboarding"
    )
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # profil temporar unic (șters la teardown)
    tmp_profile = tempfile.mkdtemp(prefix="scoped_dir_")
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
        try:
            drv.quit()
        finally:
            shutil.rmtree(tmp_profile, ignore_errors=True)


# ---- Screenshot + page source pe eșec ----
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # doar după execuția testului ("call") și doar dacă a eșuat
    if rep.when == "call" and rep.failed and "driver" in item.fixturenames:
        drv = item.funcargs["driver"]
        os.makedirs("artifacts", exist_ok=True)

        # nume fișier sigur (înlocuiește :: / cu _)
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")

        # încearcă să salvezi screenshot + html
        try:
            drv.save_screenshot(f"artifacts/{safe_name}.png")
        except Exception:
            pass
        try:
            with open(f"artifacts/{safe_name}.html", "w", encoding="utf-8") as f:
                f.write(drv.page_source)
        except Exception:
            pass
