# Browser Pilot Skill - Test Scenarios

Use these scenarios to validate that the browser-pilot skill activates correctly
and guides the agent through proper tool sequencing. Test in both Claude Code and
GitHub Copilot CLI.

---

## 1. Activation tests (should trigger the skill)

### 1.1 Direct URL request
**Prompt:** "Open https://news.ycombinator.com and show me the top 5 stories"
**Expected behavior:**
- Skill activates
- Agent calls `browser_navigate` with the URL
- Agent calls `browser_wait_for` (networkidle or selector)
- Agent calls `browser_get_text` or `browser_evaluate` to extract stories
- Agent summarizes the 5 stories

### 1.2 Vague browsing request
**Prompt:** "Check my GitHub notifications"
**Expected behavior:**
- Skill activates
- Agent navigates to `https://github.com/notifications`
- Uses existing Chrome profile (user should be logged in)
- Takes screenshot or extracts text to report back

### 1.3 Form filling
**Prompt:** "Go to https://httpbin.org/forms/post and fill out the form with test data, then submit it"
**Expected behavior:**
- Agent navigates to the URL
- Waits for the form to load
- Uses `browser_type` for text fields
- Uses `browser_select` for dropdowns (if any)
- Uses `browser_click` on submit button
- Waits for response and reports the result

### 1.4 Screenshot capture
**Prompt:** "Take a screenshot of https://example.com"
**Expected behavior:**
- Agent navigates to URL
- Waits for page load
- Calls `browser_screenshot`
- Returns the image to the user

### 1.5 Multi-tab workflow
**Prompt:** "Open google.com and bing.com in separate tabs, then compare their homepages"
**Expected behavior:**
- Agent navigates to first URL
- Opens second URL (via evaluate window.open or navigate after tabs)
- Uses `browser_tabs` to list tabs
- Switches between tabs with `browser_switch_tab`
- Captures text/screenshots from each
- Compares and summarizes

### 1.6 JavaScript execution
**Prompt:** "Go to https://jsonplaceholder.typicode.com/todos and extract all the JSON data"
**Expected behavior:**
- Agent navigates to URL
- Uses `browser_evaluate` or `browser_get_text` to extract the JSON
- Parses and presents the data

### 1.7 Cookie inspection
**Prompt:** "Navigate to github.com and show me what cookies are set"
**Expected behavior:**
- Agent navigates to URL
- Calls `browser_cookies` with action "get"
- Lists the cookies with their names/values/domains

---

## 2. Non-activation tests (should NOT trigger the skill)

### 2.1 API call
**Prompt:** "Make a GET request to https://api.github.com/users/octocat"
**Expected:** Agent uses curl/fetch, NOT browser-pilot tools.

### 2.2 Local file reading
**Prompt:** "Read the contents of README.md"
**Expected:** Agent uses file system tools, NOT browser-pilot.

### 2.3 Code generation
**Prompt:** "Write a Python script that scrapes a website using requests and BeautifulSoup"
**Expected:** Agent writes code, does NOT launch a browser.

### 2.4 General question
**Prompt:** "What is the capital of France?"
**Expected:** Agent answers directly, no browser involved.

---

## 3. Best-practice adherence tests

### 3.1 Wait after navigation
**Prompt:** "Go to https://news.ycombinator.com and click the first link"
**Verify:** Agent calls `browser_wait_for` between `browser_navigate` and `browser_click`.

### 3.2 Screenshot for confirmation
**Prompt:** "Log into my bank at https://example-bank.com"
**Verify:** Agent takes a screenshot after login attempt to confirm success/failure.

### 3.3 Error recovery
**Prompt:** "Click the button with id #nonexistent-button on https://example.com"
**Verify:** When click fails, agent takes a screenshot to diagnose, tries alternative selectors or reports the issue clearly.

### 3.4 Cookie banner handling
**Prompt:** "Go to a European news site and read the headline"
**Verify:** Agent acknowledges cookie banners may appear and attempts to dismiss them before extracting content.

---

## 4. Edge case scenarios

### 4.1 Chrome already running
**Prompt:** (With Chrome already open) "Navigate to google.com"
**Verify:** Agent successfully connects to existing Chrome instance without error.

### 4.2 Long page load
**Prompt:** "Go to a slow-loading dashboard and wait until it's fully rendered"
**Verify:** Agent uses appropriate `waitUntil` option (networkidle) and reasonable timeout.

### 4.3 PDF generation
**Prompt:** "Save https://example.com as a PDF"
**Verify:** Agent navigates to URL, waits for load, calls `browser_pdf`.

### 4.4 Page with dynamic content
**Prompt:** "Go to https://infinite-scroll-demo.com and scroll down 3 times, then show me what loaded"
**Verify:** Agent uses `browser_scroll` multiple times with waits between scrolls, then extracts text.

### 4.5 Tab cleanup
**Prompt:** "Open 3 different news sites, grab their headlines, then close them all"
**Verify:** Agent opens tabs, extracts content, then calls `browser_close` for each.

---

## 5. Integration validation

### 5.1 MCP server connectivity
**Steps:**
1. Start the browser-pilot MCP server: `npx --prefix mcp-tools/browser-pilot browser-pilot`
2. Verify it responds to MCP handshake (ListTools request)
3. Confirm all 17 tools are listed

### 5.2 End-to-end with skill
**Steps:**
1. Install the skill plugin in Claude Code or Copilot CLI
2. Ensure browser-pilot MCP server is configured
3. Say "open example.com and tell me what's on the page"
4. Verify: skill activates, tools are called in correct order, result is returned

### 5.3 Skill does not conflict with other tools
**Steps:**
1. Have both browser-pilot skill and other MCP tools (e.g., filesystem) active
2. Say "read the file at ./README.md" -- should NOT trigger browser-pilot
3. Say "open localhost:3000 in the browser" -- SHOULD trigger browser-pilot

---

## Scoring rubric

For each scenario, evaluate:

| Criterion | Pass | Fail |
|-----------|------|------|
| Skill activation | Activates when expected, stays silent when not | False positive or false negative |
| Tool ordering | Follows navigate -> wait -> interact pattern | Interacts before page is ready |
| Error handling | Recovers gracefully, reports clearly | Crashes or gives cryptic errors |
| Efficiency | Minimal tool calls to achieve goal | Redundant or unnecessary calls |
| User communication | Explains what it's doing, shows results | Silent or confusing output |
