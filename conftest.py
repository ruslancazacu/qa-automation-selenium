import os, shutil, tempfile
import pytest
from selenium import webdriver

def _chrome_options(tmp_profile: str):
    opts = webdriver.ChromeOptions()

    # headless în CI sau local dacă setezi HEADLESS=1
    if os.environ.get("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")

    # stabilitate CI / containere
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")

    # dezactivăm managerul de parole / autofill / onboarding
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False
    })
    opts.add_argument("--disable-features=Translate,AutofillServerCommunication,"
                      "PasswordManagerOnboarding,SavePasswordBubble,OptInRlhOnboarding")
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # profilul temporar (unic per worker/proces)
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    return opts

@pytest.fixture
def driver(request):
    # Unic per worker xdist (ex: gw0, gw1) + PID (siguranță)
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    tmp_profile = os.path.join(
        tempfile.gettempdir(),
        f"scoped_dir_{worker}_{os.getpid()}"
    )

    opts = _chrome_options(tmp_profile)
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(2)
    drv.set_page_load_timeout(30)
    drv.set_script_timeout(30)
    try:
        yield drv
    finally:
        drv.quit()
        shutil.rmtree(tmp_profile, ignore_errors=True)


# -------------------------------
# Artefacte + Allure pe eșec test
# -------------------------------
# (Allure e opțional local; în CI există via requirements)
try:
    import allure
except Exception:
    allure = None  # nu blocăm rularea dacă lipsește local

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    La eșecul unui test care folosește fixture-ul `driver`,
    salvăm screenshot + page source în folderul `artifacts/`
    și, dacă există Allure, le atașăm în raport.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed and "driver" in item.fixturenames:
        drv = item.funcargs["driver"]
        os.makedirs("artifacts", exist_ok=True)

        # nume sigur de fișier (fără separatori speciali)
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
        png_path = f"artifacts/{safe_name}.png"
        html_path = f"artifacts/{safe_name}.html"

        # scriem fișierele pe disc
        try:
            drv.save_screenshot(png_path)
        except Exception:
            png_path = None
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(drv.page_source)
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
                # nu stricăm testul dacă atașarea eșuează
                pass
