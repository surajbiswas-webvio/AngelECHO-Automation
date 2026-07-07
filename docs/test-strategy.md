# AngelECHO Test Strategy

## Scope

The TypeScript Playwright suite validates the customer portal across authentication, dashboard, agent management, agent configuration, route health, API responses, console errors, and deployment smoke workflows.

## Live Discovery Inventory

Primary navigation discovered on staging:

- Dashboard `/`
- All Agents `/list`
- Knowledge Base `/knowledge-base`
- Phone Numbers `/phone-numbers`
- Campaign Calling `/outbound`
- Live Calls `/live-calls`
- Call History `/call-history`
- Campaign History `/campaign-history`
- Chat History `/chat-history`
- Analytics `/analytics`
- Compliance `/compliance`
- Billing `/billing`
- Pricing `/pricing`
- Members `/members`
- Roles & Permissions `/roles-permissions`
- Setup Guides `/setup-guides`
- Support `/support`

Dashboard widgets discovered:

- Live Calls
- Total Calls
- Avg Duration
- Active Agents
- Phone Numbers
- Daily Calls
- Agent Performance
- Cost Breakdown

Agent editor sections discovered:

- Functions
- Agent Settings
- Multi-Language
- Knowledge Base
- Speech Settings
- Call Settings
- Post-Call Analysis
- Security & Fallback Settings
- Safety Restrictions
- Webhook Settings
- Agent Metadata
- Test module tabs: Web Call, Phone Call, Start

## Execution Layers

- Smoke: login, dashboard, navigation, agent listing, members/settings route.
- Dashboard: widgets, cards, links, date filter, tables, API health.
- Agents: listing, search, filters, create `Auto_Test_Agent`, persist prompt, editor sections, prompt generator, test module.
- Full UI: every discovered route opens, headings render, core buttons are enabled, and network failures are captured.
- Deployment validation: strict run that fails on any API failure or console error, including currently known staging defects.

## Artifacts

Playwright is configured for screenshots on failure, videos on failure, traces retained on failure, HTML report, and JSON report.
