# AngelECHO Automation - Code Quality Analysis Report

**Analysis Date:** 2026-07-20  
**Scope:** tests/, pages/, utils/, config/, api_helpers/, mcp/ directories

---

## Executive Summary

This analysis identified **12 unused page object methods**, **3 unused utility functions**, **3 unused function parameters**, and **0 commented-out code blocks**. The codebase is generally well-maintained with minimal code quality issues.

---

## Detailed Findings

### 1. UNUSED PAGE OBJECT METHODS (Never Called by Tests)

#### Base Page Object - `pages/base_page.py`

| Line | Method | Reason for Removal | Confidence |
|------|--------|-------------------|-----------|
| 177 | `select_option(selector, value)` | Defined but never used by any test. No usages found in entire codebase. Native select elements could be handled via Playwright's existing methods. | **HIGH** |
| 218 | `visible_text(text)` | Returns a Locator for visible text but never called. Page objects use `get_by_text()` directly instead. | **HIGH** |
| 297 | `open_combobox_by_text(text)` | Method skeleton is defined but has incomplete implementation and zero usages across all tests. | **HIGH** |

#### AI Agents Page - `pages/ai_agents_page.py`

| Line | Method | Reason for Removal | Confidence |
|------|--------|-------------------|-----------|
| 174 | `expect_validation_error(message)` | Never called by any test. Alternative validation is done inline in tests. | **HIGH** |
| 146 | `configure_stt(provider)` | **Unused Parameters:** The `provider` parameter is accepted but never used in the method body. Method checks if button exists but doesn't configure provider. Only 1 usage found (definition). Marked as "reserved for future selection" in docstring. | **HIGH** |
| 153 | `configure_tts(provider, voice)` | **Unused Parameters:** Both `provider` and `voice` parameters are declared but never referenced in implementation. Method only verifies button visibility. Docstring notes "parameters support future options" but they're not used. Only 1 usage found (definition). | **HIGH** |

#### Module Page - `pages/module_page.py`

| Line | Method | Reason for Removal | Confidence |
|------|--------|-------------------|-----------|
| 115 | `search(placeholder, value)` | Defined but never called by any test. Tests use `fill()` and `get_by_placeholder()` directly instead. | **HIGH** |

#### Utilities/Assertions - `utils/assertions.py`

| Line | Function | Reason for Removal | Confidence |
|------|----------|-------------------|-----------|
| 14 | `assert_url_contains(page, expected_fragment)` | Never called by any test. Page objects use `expect_url_contains()` method instead, or call `expect(page).to_have_url()` directly. | **HIGH** |
| 57 | `assert_toast_contains(page, message)` | Never imported or called anywhere in the codebase. Page objects implement toast assertions inline instead. | **HIGH** |
| 35 | `assert_text_visible(locator, expected_text)` | Never called by any test. Duplicates the functionality of `expect(locator).to_be_visible()` and `expect(locator).to_contain_text()` which tests use directly. | **HIGH** |

---

### 2. UNUSED MCP/PLAYWRIGHT HELPER METHODS

#### MCP Tools - `mcp/tools.py`

| Line | Method | Reason for Removal | Confidence |
|------|--------|-------------------|-----------|
| 191 | `call_mcp_server_tool(tool_name, arguments)` | Never called by any test. Only definition found, zero usages. Duplicates functionality of `mcp_client.call_tool()` which is called via fixture instead. | **NEEDS REVIEW** |

#### MCP Playwright Client - `mcp/playwright_client.py`

| Line | Method/Property | Reason for Removal | Confidence |
|------|---------|-------------------|-----------|
| 87 | `is_connected` property | Used only internally (2 internal references in same file). Could be private (`_is_connected`). | **MEDIUM** |

---

### 3. UNUSED FUNCTION PARAMETERS

#### File: `pages/ai_agents_page.py`

| Line | Method | Parameter | Current Usage | Recommendation |
|------|--------|-----------|---------------|-----------------|
| 146 | `configure_stt()` | `provider: str` | Never referenced in method body | Remove parameter or implement provider-specific logic |
| 153 | `configure_tts()` | `provider: str` | Never referenced in method body | Remove parameter or implement provider-specific logic |
| 153 | `configure_tts()` | `voice: str \| None` | Never referenced in method body | Remove parameter or implement voice-specific logic |

**Root Cause:** Methods were created as placeholders for future implementation but parameters were added before use cases were clear.

---

### 4. POTENTIALLY UNUSED PAGE OBJECT METHODS (Needs Manual Review)

These methods are called by at least one test but usage pattern suggests they may be dead code:

| File | Method | Usage | Notes |
|------|--------|-------|-------|
| `pages/billing_page.py` | `switch_to_plans()` | 1 call in test_module_workflows.py | Could be inline button click instead |
| `pages/billing_page.py` | `switch_to_payments()` | 1 call in test_module_workflows.py | Could be inline button click instead |
| `pages/pricing_page.py` | `open_detailed_pricing()` | 1 call in test_module_workflows.py | Could be inline button click instead |
| `pages/phone_numbers_page.py` | `search_numbers()` | 1 call in test_module_workflows.py | Duplicates `fill()` + `wait_for_timeout()` pattern |
| `pages/outbound_page.py` | `search_campaigns()` | 1 call in test_module_workflows.py | Duplicates `fill()` + `wait_for_timeout()` pattern |
| `pages/support_page.py` | `search_tickets()` | 1 call in test_module_workflows.py | Duplicates `fill()` + `wait_for_timeout()` pattern |
| `pages/members_page.py` | `search_members()` | 1 call in test_module_workflows.py | Duplicates `fill()` + `wait_for_timeout()` pattern |

**Recommendation:** These are on the boundary - they exist and are used once, but are simple wrapper methods that might not justify their existence.

---

### 5. DUPLICATE HELPER PATTERNS (Code Duplication)

#### Pattern 1: Search + Wait Implementation

**Found in 5 locations** - These methods have identical implementation patterns:

1. [pages/module_page.py](pages/module_page.py#L118) - `search()` method
2. [pages/phone_numbers_page.py](pages/phone_numbers_page.py#L27) - `search_numbers()` 
3. [pages/outbound_page.py](pages/outbound_page.py#L18) - `search_campaigns()`
4. [pages/support_page.py](pages/support_page.py#L17) - `search_tickets()`
5. [pages/members_page.py](pages/members_page.py#L28) - `search_members()`

**Pattern:**
```python
def search_*(self, value: str) -> None:
    self.page.get_by_placeholder("Search...").fill(value)
    self.page.wait_for_timeout(300)
```

**Recommendation:** Extract to `BasePage.search_by_placeholder()` utility method with configurable placeholder and timeout.

#### Pattern 2: Tab Switching

**Found in 2 locations:**

1. [pages/billing_page.py](pages/billing_page.py#L11) - `switch_to_plans()`, `switch_to_payments()`
2. [pages/vendor_team_page.py](pages/vendor_team_page.py#L20) - `open_tab()`

**Recommendation:** Create generic `BasePage.click_tab(name: str)` method to replace both implementations.

---

### 6. COMMENTED-OUT CODE

**Result:** No commented-out code blocks found in any Python files.

---

### 7. UNUSED TEST FILES / TEST FUNCTIONS

**Status:** All test functions are properly marked with pytest markers (`@pytest.mark.smoke`, `@pytest.mark.regression`, etc.). All test files are actively used.

---

### 8. UNUSED IMPORTS

#### Verified as USED:
- `pathlib.Path` in all page object files where it appears (e.g., `vendor_support_page.py`, `mcp/browser_manager.py`)
- `datetime` in all e2e and vendor test files - used for timestamp generation in test data
- `re` in all files - used for regex patterns in URL/text matching
- `yaml` - used for parsing environment configuration
- All Playwright imports - actively used throughout

#### Status: No unused imports found.

---

### 9. UNUSED API HELPER METHODS

**Status:** All methods in `api_helpers/` are either:
- Called by at least one test (`AuthApi.login()`, `AgentsApi.list_agents()`, etc.)
- Internal helper methods used by other methods in the same class (`_get_default_workspace_id()`)

**No unused API methods found.**

---

## Summary Table

| Issue Type | Count | Confidence | Severity |
|-----------|-------|-----------|----------|
| Unused page object methods | 7 | HIGH | **Medium** |
| Unused utility functions | 3 | HIGH | **Low** |
| Unused/unused parameters | 3 | HIGH | **Medium** |
| Boundary methods (used once) | 7 | MEDIUM | **Low** |
| Code duplication patterns | 7 | HIGH | **Low** |
| Commented-out code | 0 | N/A | N/A |
| Unused test files/functions | 0 | N/A | N/A |
| Unused imports | 0 | N/A | N/A |

---

## Recommendations (Priority Order)

### HIGH PRIORITY
1. **Remove unused assertion helpers** (`utils/assertions.py` lines 14, 35, 57)
   - Time to fix: 5 minutes
   - Impact: Removes unused code without affecting tests

2. **Remove unused page object methods** (`base_page.py` lines 177, 218, 297)
   - Time to fix: 10 minutes  
   - Impact: Reduces cognitive load when reading BasePage

3. **Fix unused parameters in AI Agents page** (`pages/ai_agents_page.py` lines 146, 153)
   - Time to fix: 15 minutes
   - Options: Remove parameters or implement provider/voice selection logic
   - Impact: Makes method signatures more honest

### MEDIUM PRIORITY
4. **Create unified search helper** in `BasePage`
   - Time to fix: 30 minutes
   - Consolidates 5 duplicate search implementations
   - Reduces code duplication by ~10 lines

5. **Remove unused page object methods** from `ai_agents_page.py` and `module_page.py`
   - Time to fix: 5 minutes
   - Impact: Reduces API surface of page objects

### LOW PRIORITY
6. **Mark `is_connected` as private** in `mcp/playwright_client.py`
   - Time to fix: 2 minutes
   - Only used internally

7. **Review boundary methods** (used only once)
   - Assess if wrapper methods add enough value to justify existence
   - May keep as they improve test readability

---

## Files Without Issues

✅ `config/settings.py` - All code actively used  
✅ `config/env.py` - Clean compatibility wrapper  
✅ `api_helpers/base_client.py` - All methods active  
✅ `api_helpers/auth_api.py` - All methods active  
✅ `api_helpers/agents_api.py` - All methods active  
✅ `mcp/browser_manager.py` - All methods active  
✅ `utils/logger.py` - All code active  
✅ `utils/screenshot.py` - All code active  
✅ `utils/config_manager.py` - All code active  
✅ `utils/data_loader.py` - All code active  

---

## Notes

- The codebase follows good practices with comprehensive docstrings explaining purpose and usage
- Framework is well-architected with clear separation between base classes, page objects, and tests
- No security issues or major anti-patterns detected
- Most unused code appears to be intentional placeholders for future functionality
