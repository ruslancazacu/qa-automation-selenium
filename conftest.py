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

    # Dezactivează onboarding/autofill/manager parolă + leak warning (fără pop-up-uri)
    opts.add_argument(
        "--disable-features=" +
        ",".join([
            "Translate",
            "AutofillServerCommunication",
            "PasswordManagerOnboarding",
            "SavePasswordBubble",
            "OptInRlhOnboarding",
            "PasswordLeakDetection",
        ])
    )
    opts.add_argument("--disable-save-password-bubble")
    opts.add_argument("--password-store=basic")
    opts.add_argument("--use-mock-keychain")

    # Alte blocări de UI care uneori apar în Chromium
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-infobars")

    # Elimină bannerul “Chrome is being controlled by automated test software”
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Dezactivează autofill & password manager din prefs (dublu asigurat)
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
        # oprește cererile de notificări site
        "profile.default_content_setting_values.notifications": 2,
    })

    # Profil Chrome temporar (unic per worker/proces)
    opts.add_argument(f"--user-data-dir={tmp_profile}")

    # Page load strategy implicită (stabilă)
    opts.page_load_strategy = "normal"

    # Activăm logurile de consolă din browser (utile la debug)
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    return opts


@pytest.fixture
def driver():
    """
    Instanță Chrome izolată pe test (profil dedicat); curățăm profilul la final.
    HEADLESS=1 (default) -> rulează fără UI. Setează HEADLESS=0 pentru UI local.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    tmp_profile = os.path.join(
        tempfile.gettempdir(),
        f"chrome_prof_{worker}_{os.getpid()}"
    )

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
    salvăm screenshot + page source + console logs în `artifacts/`
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
    url_path = os.path.join("artifacts", f"{safe}.current-url.txt")
    log_path = os.path.join("artifacts", f"{safe}.browser-console.log")

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

    # URL curent
    try:
        with open(url_path, "w", encoding="utf-8") as fh:
            fh.write(drv.current_url or "")
    except Exception:
        url_path = None

    # Loguri de consolă din browser
    try:
        logs = []
        for entry in drv.get_log("browser"):
            # fiecare entry are level, message, timestamp
            logs.append(f"[{entry.get('level')}] {entry.get('message')}")
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(logs))
    except Exception:
        log_path = None

    # atașăm în Allure, dacă e disponibil
    if allure:
        try:
            if png_path and os.path.exists(png_path):
                allure.attach.file(
                    png_path, name="screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
            if html_path and os.path.exists(html_path):
                allure.attach.file(
                    html_path, name="page-source",
                    attachment_type=allure.attachment_type.HTML
                )
            if url_path and os.path.exists(url_path):
                allure.attach.file(
                    url_path, name="current-url",
                    attachment_type=allure.attachment_type.TEXT
                )
            if log_path and os.path.exists(log_path):
                allure.attach.file(
                    log_path, name="browser-console",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception:
            pass
