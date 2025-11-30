# QA Automation — Selenium + PyTest
![CI](https://github.com/ruslancazacu/qa-automation-selenium/actions/workflows/ci.yml/badge.svg)

Teste UI headless pe site-ul demo **SauceDemo** cu Page Object Model.

## Run local (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
