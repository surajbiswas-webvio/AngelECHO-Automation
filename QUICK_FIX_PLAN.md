# QuickFix Action Plan - High Confidence Issues

**To remove dead code, run the following operations:**

---

## 1. Remove Unused Assertion Helpers (5 min)

**File:** [utils/assertions.py](utils/assertions.py)

### Remove: `assert_url_contains()` (Lines 14-28)
```python
# DELETE THIS FUNCTION - Never called by any test
def assert_url_contains(page: Page, expected_fragment: str) -> None:
    """
    Purpose:
        Verifies that the current page URL contains an expected fragment.
    ...
    """
    expect(page).to_have_url(re.compile(f".*{re.escape(expected_fragment)}.*"))
```

**Replacement:** Page objects already use `expect_url_contains()` method, tests use `expect(page).to_have_url()` directly.

---

### Remove: `assert_text_visible()` (Lines 35-54)
```python
# DELETE THIS FUNCTION - Never called by any test
def assert_text_visible(locator: Locator, expected_text: str) -> None:
    """
    Purpose:
        Confirms that a locator is visible and contains expected text.
    ...
    """
    expect(locator).to_be_visible()
    expect(locator).to_contain_text(expected_text)
```

**Replacement:** Tests call `expect().to_be_visible()` and `expect().to_contain_text()` directly.

---

### Remove: `assert_toast_contains()` (Lines 57-72)
```python
# DELETE THIS FUNCTION - Never called by any test
def assert_toast_contains(page: Page, message: str) -> None:
    """
    Purpose:
        Verifies that a user-facing toast or alert contains a message.
    ...
    """
    toast = page.get_by_role("alert").or_(page.locator(".toast, .Toastify__toast, [data-testid*='toast']").first)
    expect(toast).to_be_visible()
    expect(toast).to_contain_text(message)
```

**Replacement:** Page objects like `VendorLeadsPage` use `self.toast()` helper instead.

---

## 2. Remove Unused Base Page Methods (10 min)

**File:** [pages/base_page.py](pages/base_page.py)

### Remove: `select_option()` (Lines 164-177)
```python
# DELETE THIS METHOD - Never called
def select_option(self, selector: str, value: str) -> None:
    """
    Purpose:
        Selects an option in a visible native select field.
    ...
    """
    field = self.page.locator(selector).first
    expect(field).to_be_visible()
    field.select_option(value=value)
```

**Reason:** Can use Playwright's `locator().select_option()` directly when needed.

---

### Remove: `visible_text()` (Lines 218-233)
```python
# DELETE THIS METHOD - Never called
def visible_text(self, text: str) -> Locator:
    """
    Purpose:
        Builds a locator for visible text content.
    ...
    """
    return self.page.get_by_text(text, exact=False)
```

**Reason:** Tests use `get_by_text()` directly; no need for wrapper.

---

### Remove: `open_combobox_by_text()` (Lines 297-320)
```python
# DELETE THIS METHOD - Unused, incomplete implementation
def open_combobox_by_text(self, text: str) -> None:
    """
    Purpose:
        Opens a custom combobox or menu trigger by exact visible text.
    ...
    """
    # Method body incomplete/unused
```

**Reason:** Incomplete implementation, never used by any test.

---

## 3. Fix Unused Parameters in AI Agents Page (15 min)

**File:** [pages/ai_agents_page.py](pages/ai_agents_page.py)

### Issue 1: `configure_stt()` - Line 146
```python
# CURRENT - Parameter 'provider' is unused
def configure_stt(self, provider: str) -> None:
    """Open speech settings when available; provider is reserved for future selection."""
    button = self.page.get_by_role("button", name="Speech Settings")
    if button.count() > 0:
        button.click()
```

**Options:**
- **A) Remove parameter** if not actually needed for STT configuration
- **B) Implement provider logic** if this should select between providers (Google, Azure, etc.)

**Recommendation:** Remove parameter unless providers need to be selectable.

---

### Issue 2: `configure_tts()` - Line 153
```python
# CURRENT - Parameters 'provider' and 'voice' are unused
def configure_tts(self, provider: str, voice: str | None = None) -> None:
    """Verify text-to-speech settings remain saveable; parameters support future options."""
    expect(self.page.get_by_role("button", name=AGENT.save_button_name).or_(
        self.page.get_by_role("button", name=AGENT.update_button_name)
    ).first).to_be_visible()
```

**Options:**
- **A) Remove parameters** if not actually used for TTS configuration
- **B) Implement provider/voice selection** if tests need to configure specific providers or voices

**Recommendation:** Remove parameters unless/until test requirements demand them.

---

## 4. Remove Unused AI Agents Page Methods (5 min)

**File:** [pages/ai_agents_page.py](pages/ai_agents_page.py)

### Remove: `expect_validation_error()` - Line 174
```python
# DELETE THIS METHOD - Never called
def expect_validation_error(self, message: str | None = None) -> None:
    """Assert a validation error is visible, optionally with expected text."""
    error = self.page.locator("[role='alert'], .invalid-feedback, .text-danger, [data-testid*='error']").first
    expect(error).to_be_visible()
    if message:
        expect(error).to_contain_text(message)
```

**Reason:** Never called by any test; validation checks done inline in tests.

---

## 5. Remove Unused Module Page Method (2 min)

**File:** [pages/module_page.py](pages/module_page.py)

### Remove: `search()` - Line 115
```python
# DELETE THIS METHOD - Never called
def search(self, placeholder: str, value: str) -> None:
    """
    Purpose:
        Enters text into a module search field.
    ...
    """
    self.page.get_by_placeholder(placeholder).fill(value)
    self.page.wait_for_timeout(300)
```

**Reason:** Duplicates common pattern; tests use `fill()` + `wait_for_timeout()` directly.

---

## 6. Optional: Remove Unused MCP Method (2 min)

**File:** [mcp/tools.py](mcp/tools.py)

### Remove: `call_mcp_server_tool()` - Line 191
```python
# DELETE OR MAKE PRIVATE - Never called from tests
def call_mcp_server_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPResponse:
    """
    Purpose:
        Calls a tool exposed by an external Playwright MCP server.
    ...
    """
    if self.client is None:
        raise RuntimeError("No Playwright MCP client was provided to PlaywrightMCPTools.")
    return self.client.call_tool(tool_name, arguments)
```

**Recommendation:** **NEEDS MANUAL REVIEW** - May be used by external MCP tools. Keep for now but mark as internal.

---

## Total Cleanup Time

- Remove unused assertions: **5 minutes**
- Remove base page methods: **10 minutes**  
- Fix AI agents parameters: **15 minutes**
- Remove AI agents dead methods: **5 minutes**
- Remove module page method: **2 minutes**

**Total: 37 minutes** ≈ **40 minutes with testing**

---

## Testing After Changes

Run these commands to ensure nothing broke:

```bash
# Test smoke tests still pass
pytest tests/smoke -v

# Test regression suite
pytest tests/regression -v

# Test API layer
pytest tests/api -v

# Test vendor workflows
pytest tests/vendor -v
```

---

## Files to Backup Before Making Changes

1. `utils/assertions.py`
2. `pages/base_page.py`
3. `pages/ai_agents_page.py`
4. `pages/module_page.py`
5. `mcp/tools.py` (optional)
