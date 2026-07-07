# Deployment Verification Report

## Environment

- Date: 2026-06-16
- UI: `https://staging-app.webvio.in/`
- API: `https://staging-api.angelecho.ai/v1/`
- Workspace: `New Customer's Workspace`

## Result Summary

- Login: Passed via existing Python smoke test.
- Invalid login validation: Passed via existing Python smoke test.
- Dashboard load: Passed, widgets rendered.
- Navigation: Passed for all discovered modules.
- Agent creation: Passed. `POST /agents/create-full` returned `200`.
- Agent persistence: Passed. `Auto_Test_Agent` appeared in the list and opened in `/agent-editor`.
- Agent prompt: Passed. The requested prompt was visible in the editor.
- Agent testing surface: Partially passed. Web Call, Phone Call, and Start were visible.
- API health: Failed because `GET /live-calls/10` returned `403`.
- Console health: Failed because CORS and call-history JavaScript errors were observed.

## Recommended Gate

Use `npm run test:smoke` as a deployment confidence check while `ALLOW_KNOWN_DEFECTS=true`.

Use `npx playwright test tests-ts/deployment-validation.spec.ts` as the strict gate once the backend/CORS issues are fixed.
