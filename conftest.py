import os
import shutil
import tempfile
import pytest
from selenium import webdriver


def _chrome_options(tmp_profile: str) -> webdriver.ChromeOptions:
    opts = webdriver.ChromeOptions()

    # Headless în CI sau local dacă setezi HEADLESS=1 (default 1 ca să nu apară ferestre)
    if os.environ.get("HEADLESS", "1") == "1":
        opts.add_argument("--headless=new")

    # Stabilitate (CI/containere/Windows)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-features=Translate,AutofillServerCommunication,"
                      "PasswordManagerOnboarding,SavePasswordBubble,OptInRlhOnboarding")
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # Elimină bannerul “Chrome is being controlled by automated test software”
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Dezactivează password manager & autofill (previn baloanele native)
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
    })

    # Profil Chrome temporar (unic per worker/proces)
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    # Page load strategy implicită (stabilă); poți folosi "eager" dacă vrei mai rapid
    opts.page_load_strategy = "normal"

    return opts


@pytest.fixture
def driver():
    """
    Instanță Chrome izolată pe test (profil dedicat); curățăm profilul la final.
    HEADLESS=1 (default) -> rulează fără UI. Setează HEADLESS=0 pentru UI local.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    tmp_profile = os.path.join(tempfile.gettempdir(), f"chrome_prof_{worker}_{os.getpid()}")

    opts = _chrome_options(tmp_profile)
    drv = webdriver.Chrome(options=opts)

    # Timeouts & așteptări implicite
    drv.implicitly_wait(2)
    drv.set_page_load_timeout(30)
    drv.set_script_timeout(30)

    try:
        yield drv
    finally:
        try:
            drv.quit()
        finally:
            shutil.rmtree(tmp_profile, ignore_errors=True)


# -------------------------------
# Artefacte + Allure pe eșec test
# -------------------------------
try:
    import allure  # type: ignore
except Exception:
    allure = None  # nu blocăm rularea local dacă lipsesc pachetele


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    La eșecul unui test care folosește fixture-ul `driver`,
    salvăm screenshot + page source în `artifacts/`
    și, dacă există Allure, le atașăm în raport.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call" or not rep.failed or "driver" not in item.fixturenames:
        return

    drv = item.funcargs["driver"]
    os.makedirs("artifacts", exist_ok=True)

    # nume sigur de fișier
    safe = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
    png_path = os.path.join("artifacts", f"{safe}.png")
    html_path = os.path.join("artifacts", f"{safe}.html")

    # scriem fișierele pe disc
    try:
        drv.save_screenshot(png_path)
    except Exception:
        png_path = None

    try:
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(drv.page_source)
    except Exception:
        html_path = None

    # atașăm în Allure, dacă e disponibil
    if allure:
        try:
            if png_path and os.path.exists(png_path):
                allure.attach.file(png_path, name="screenshot",
                                   attachment_type=allure.attachment_type.PNG)
            if html_path and os.path.exists(html_path):
                allure.attach.file(html_path, name="page-source",
                                   attachment_type=allure.attachment_type.HTML)
        except Exception:
            pass
