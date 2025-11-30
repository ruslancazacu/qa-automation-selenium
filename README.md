# QA Automation — Selenium + PyTest
![CI](https://github.com/ruslancazacu/qa-automation-selenium/actions/workflows/ci.yml/badge.svg)

Teste UI headless pe site-ul demo **SauceDemo** cu Page Object Model.

## Stack
- Selenium 4
- PyTest 8
- PyTest-xdist (rulare în paralel)
- Allure (rapoarte)

## Run local (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest -q
