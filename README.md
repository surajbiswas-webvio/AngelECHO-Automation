# Angel ECHP Automation Framework

Enterprise Playwright Python automation framework for the Echo Customer AI Voice Agent portal.

## Architecture

```text
api_helpers/            API clients for auth, agents, and backend setup
config/                 Environment configuration and runtime settings
data/                   JSON/YAML test data
fixtures/               Reserved for domain-specific reusable fixtures
pages/                  Page Object Model classes and centralized locators
tests/api/              API checks
tests/e2e/              End-to-end workflows
tests/regression/       Broader regression scenarios
tests/smoke/            Deployment confidence suite
utils/                  Logging, assertions, screenshots, data loading
reports/                HTML, Allure, trace, and video outputs
screenshots/            Failure screenshots
logs/                   Rotating automation logs
storage_states/         Reusable Playwright authenticated sessions
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install
Copy-Item .env.example .env
```

Update `.env` for the target environment. Keep real credentials in local `.env` or CI secrets.

## Run Tests

```powershell
pytest
pytest -m smoke
pytest -m regression
pytest -m e2e
pytest -m api
pytest --headed-mode
pytest --env qa
```

Run in parallel:

```powershell
pytest -n auto
pytest -m smoke -n 4
```

Generate reports:

```powershell
pytest --html=reports/html-report.html --self-contained-html
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## Framework Capabilities

- Playwright sync API with Pytest.
- Page Object Model with shared `BasePage`.
- Centralized selectors in `pages/locators.py`.
- Environment configuration through `.env` and `config/environments.yaml`.
- Data-driven JSON/YAML fixtures under `data/`.
- Session reuse via Playwright `storage_state` per xdist worker.
- Failure screenshots, Playwright traces, rotating logs, HTML reports, and Allure results.
- Retry support through `pytest-rerunfailures`.
- Parallel execution through `pytest-xdist`.
- API helper layer ready for backend setup and validation.
- GitHub Actions and Jenkins examples included.

## Maintenance Practices

- Prefer stable `data-testid` attributes for all selectors. Add them in the product when possible.
- Keep page objects workflow-oriented and tests assertion-oriented.
- Use API helpers to create and clean test data whenever UI setup becomes slow.
- Mark suites intentionally: `smoke`, `regression`, `e2e`, `api`, `negative`, `permissions`, `session`, `ui`.
- Avoid fixed sleeps. Use Playwright locators, assertions, and load states.
- Keep one assertion theme per test so failures are diagnostic.
- Store secrets only in `.env`, GitHub secrets, Jenkins credentials, or a vault.
- Review reports, traces, screenshots, and logs together for failure triage.

## Scaling Recommendations

- Add product-level `data-testid` hooks for login, dashboard cards, AI agent forms, STT/TTS controls, voice selectors, prompts, search, delete dialogs, and toast notifications.
- Build API cleanup routines for agents created during tests.
- Split long E2E tests into API setup plus focused UI validations where possible.
- Add contract tests for auth, agents, permissions, and settings APIs.
- Run smoke on every deployment, regression nightly, and full cross-browser suites before major releases.
- Introduce visual checks only for stable pages and keep them separate from functional regression.
