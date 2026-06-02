# Angel ECHO Automation Framework

Enterprise Playwright Python automation framework for the Angel ECHO Admin, Vendor, and Customer portals.

## Architecture

```text
portals/
  admin/
    pages/          Admin Portal page objects
    tests/          Admin Portal test suites
    fixtures/       Admin-only fixtures
    data/           Admin-only test data
  vendor/
    pages/          Vendor Portal page objects
    tests/          Vendor Portal test suites
    fixtures/       Vendor-only fixtures
    data/           Vendor-only test data
  customer/
    pages/          Customer Portal page objects
    tests/          Customer Portal test suites
    fixtures/       Customer-only fixtures
    data/           Customer-only test data

common/
  api/              Shared API clients
  auth/             Shared login page plus admin/vendor/customer auth flows
  base_pages/       Shared Playwright Page Object base classes
  components/       Shared locators and reusable UI component objects
  helpers/          Cross-portal helper modules
  utils/            Logging, assertions, screenshots, data loading, config helpers

config/             Runtime settings and environment defaults
reports/            HTML, Allure, trace, and video outputs
screenshots/        Failure screenshots
logs/               Rotating automation logs
storage_states/     Reusable Playwright authenticated sessions by env, portal, worker, and user
```

## Where Code Belongs

Add portal-specific test files under `portals/<portal>/tests`. Add portal-specific page objects under `portals/<portal>/pages`.

Put code in `common` only when at least two portals can reuse it, or when it is framework infrastructure such as auth, config, logging, API clients, base pages, reporting helpers, screenshots, or shared UI components.

Keep shared workflows thin and explicit. For example, `common/auth/vendor_auth.py`, `common/auth/customer_auth.py`, and `common/auth/admin_auth.py` each own their portal login flow while reusing `common/auth/login_page.py`.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install
Copy-Item .env.example .env
```

Update `.env` for the target environment. Keep real credentials in local `.env` or CI secrets.

## Environment Configuration

Runtime configuration is centralized in:

```text
config/settings.py              Settings dataclass used by tests, fixtures, pages, and API clients
common/utils/config_manager.py  .env loading, URL normalization, and runtime validation
config/environments.yaml        Committed non-secret environment defaults
.env.example                    Local override template
.env.staging.example            Staging template
.env.prod.example               Production template with URLs intentionally blank
```

Supported portal URLs:

```text
ADMIN_BASE_URL
VENDOR_BASE_URL
CUSTOMER_BASE_URL
```

Select a portal with `PORTAL` or `--portal`:

```powershell
$env:PORTAL="customer"; pytest portals/customer/tests
pytest --portal vendor portals/vendor/tests
pytest --portal admin portals/admin/tests
```

A pytest session targets one portal because authentication storage state and browser context are session-scoped. Run Customer, Vendor, and Admin suites as separate pytest commands in CI.

## Run Tests

```powershell
pytest portals/customer/tests
pytest portals/customer/tests -m smoke
pytest portals/customer/tests -m regression
pytest portals/customer/tests -m e2e
pytest portals/customer/tests -m api
pytest --headed-mode --portal customer portals/customer/tests
```

Run the Vendor Portal suite:

```powershell
$env:PORTAL="vendor"
$env:VENDOR_EMAIL="<vendor email>"
$env:VENDOR_PASSWORD="<vendor password>"
pytest portals/vendor/tests
pytest portals/vendor/tests -m smoke
pytest portals/vendor/tests -m crud
pytest portals/vendor/tests -n 2
```

Run in parallel:

```powershell
pytest --portal customer portals/customer/tests -n auto
pytest --portal vendor portals/vendor/tests -m smoke -n 4
```

Generate reports:

```powershell
pytest --html=reports/html-report.html --self-contained-html
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## Framework Capabilities

- Playwright sync API with Pytest.
- Portal-wise Page Object Model under `portals/<portal>/pages`.
- Shared `BasePage` in `common/base_pages/base_page.py`.
- Shared selectors in `common/components/locators.py`.
- Environment configuration through `.env` and `config/environments.yaml`.
- Portal-scoped JSON/YAML fixtures under `portals/<portal>/data`.
- Session reuse via Playwright `storage_state` per environment, portal, xdist worker, and user.
- Failure screenshots, Playwright traces, rotating logs, HTML reports, and Allure results.
- Retry support through `pytest-rerunfailures`.
- Parallel execution through `pytest-xdist`.
- Shared API helper layer under `common/api`.
- GitHub Actions workflow included.

## Portal Coverage

Customer automation lives under `portals/customer` and covers login, dashboard navigation, accessible modules, AI agent workflows, settings validation, session/permission checks, and agents API checks.

Vendor automation lives under `portals/vendor` and covers dashboard navigation, leads CRUD, demo agents, earnings, pricing, team management, performance, support, profile, session checks, reporting artifacts, and xdist-compatible worker state.

Admin automation should be added under `portals/admin` using the existing folder structure. Put Admin-only pages/tests/data there, and promote reusable logic into `common` only when another portal benefits from it.

## Maintenance Practices

- Prefer stable `data-testid` attributes for selectors. Add them in the product when possible.
- Keep page objects workflow-oriented and tests assertion-oriented.
- Use API helpers to create and clean test data whenever UI setup becomes slow.
- Mark suites intentionally: `admin`, `vendor`, `customer`, `smoke`, `regression`, `e2e`, `api`, `negative`, `permissions`, `session`, `ui`.
- Avoid fixed sleeps. Use Playwright locators, assertions, and load states.
- Keep one assertion theme per test so failures are diagnostic.
- Store secrets only in `.env`, GitHub secrets, or a vault.
- Review reports, traces, screenshots, and logs together for failure triage.
