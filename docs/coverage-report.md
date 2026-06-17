# Coverage Report

## Covered

- Login with valid customer credentials.
- Invalid login rejection in existing Python smoke suite.
- Dashboard widgets, metric cards, tables, date filter, links, and API capture.
- Primary navigation across all discovered modules.
- Agent list table headers, search, filter dropdowns, and details navigation.
- Voice agent creation for `Auto_Test_Agent`.
- Prompt persistence using the requested prompt text.
- Agent editor sections and test module visibility.
- Prompt generator modal.
- Route-level UI inventory attached per page.
- Screenshots, videos, traces, HTML reports, JSON result report.

## Partially Covered

- Sorting: current UI exposes filter/menu buttons but no clear accessible sort controls beyond table headers.
- Pagination: row-size controls are validated; page navigation controls depend on data volume.
- Deployment: no separate deploy button was visible in the discovered agent editor. The suite validates update/persistence and test module availability.
- Test call: the `Start` control is validated as present. A real call start can consume telephony/voice resources, so the strict test stops before initiating an external side effect.

## Not Yet Covered

- Real phone call completion and voice response assertions.
- File upload flows for Knowledge Base and Compliance.
- Payment method mutation flows.
- Member invitation submission to real email addresses.
- Destructive delete flows beyond existing Python agent cleanup tests.
