# Defect Report

## DEF-001: Live Calls API returns 403

- Area: Dashboard, Live Calls, deployment smoke
- Endpoint: `GET https://staging-api.angelecho.ai/v1/live-calls/10`
- Observed: repeated `403` responses during dashboard and navigation exploration.
- Impact: live-call metrics and call testing reliability are at risk for the customer workspace.
- Automation: `tests-ts/deployment-validation.spec.ts` fails strictly until this is fixed. Other suites ignore it only when `ALLOW_KNOWN_DEFECTS=true`.

## DEF-002: Browser console CORS failures

- Area: Dashboard, analytics, permissions, phone numbers, live calls
- Observed: console errors report missing `Access-Control-Allow-Origin` for several staging API requests.
- Impact: UI may silently show empty or stale data depending on browser enforcement and token state.
- Automation: strict deployment validation captures these as console failures.

## DEF-003: Call history console error

- Area: Call History
- Observed: `ReferenceError: setDeleteLoading is not defined` while fetching call history.
- Impact: call history actions may fail or leave loading state inconsistent.
- Automation: strict deployment validation and full UI route coverage capture console errors.

## DEF-004: Shared Python artifact directories are not writable in current execution context

- Area: Existing Python framework
- Observed: writes to `logs/automation.log`, `reports/html-report.html`, and `reports/allure-results/*.json` were denied.
- Impact: pytest execution can fail before running tests.
- Mitigation added: `utils/logger.py` falls back to a temp log file when the shared repo log is unavailable.
