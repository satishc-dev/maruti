---
name: browser-pilot
description: Use when the user wants to interact with a web page, browse a website, fill a form, take a screenshot of a URL, scrape content, test a web UI, or automate Chrome. Activates on mentions of browsing, Chrome, web pages, URLs to visit, "open X site", "check my dashboard", or any browser automation task. Do NOT use for general HTTP API calls (use curl/fetch instead).
---

# Browser Pilot

You have access to the `browser-pilot` MCP server which controls a real Chromium-based browser via Playwright CDP. The server auto-detects the best available browser (Chrome > Edge > Brave > Chromium) and launches it automatically on first use (headed, with the user's existing profile so they stay logged in).

## Available tools

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to a URL (params: `url`, optional `waitUntil`: load/domcontentloaded/networkidle/commit) |
| `browser_click` | Click an element (params: `selector`, optional `text` for text-based matching) |
| `browser_type` | Type into an input (params: `selector`, `text`, optional `delay` ms between keys) |
| `browser_screenshot` | Capture screenshot (params: optional `selector` for element, `fullPage` boolean) |
| `browser_get_text` | Extract text content (params: optional `selector`; omit for full page) |
| `browser_scroll` | Scroll the page (params: `direction`: up/down/left/right, optional `amount` px) |
| `browser_wait_for` | Wait for condition (params: `selector` for element, or `event`: load/domcontentloaded/networkidle; optional `timeout` ms, `state`: visible/hidden/attached/detached for selectors) |
| `browser_evaluate` | Run JavaScript in page (params: `script` string) |
| `browser_select` | Select dropdown option (params: `selector`, `value` or `label`) |
| `browser_upload` | Upload file (params: `selector`, `filePath`) |
| `browser_cookies` | Manage cookies (params: `action`: get/set/delete, plus cookie fields) |
| `browser_pdf` | Save page as PDF (params: optional `path`) |
| `browser_back` | Navigate back in history |
| `browser_forward` | Navigate forward in history |
| `browser_close` | Close current page/tab |
| `browser_tabs` | List all open tabs |
| `browser_switch_tab` | Switch to tab by index (params: `index`) |

## Workflow patterns

### Browse and capture

```
browser_navigate(url) -> browser_wait_for(event: "networkidle") -> browser_screenshot()
```

Always wait after navigation before taking a screenshot or interacting.

### Form filling

```
browser_navigate(url)
browser_wait_for(selector: "form")
browser_click(selector: "#email-field")
browser_type(selector: "#email-field", text: "user@example.com")
browser_type(selector: "#password-field", text: "***")
browser_click(selector: "button[type=submit]")
browser_wait_for(event: "networkidle")
browser_screenshot()  // confirm result
```

### Data extraction

```
browser_navigate(url)
browser_wait_for(selector: ".content")
browser_get_text(selector: ".data-table")
// or for structured data:
browser_evaluate(script: "JSON.stringify([...document.querySelectorAll('tr')].map(r => r.textContent))")
```

### Multi-tab workflow

```
browser_tabs()  // see what's open
browser_navigate(url: "https://site-a.com")  // opens in current tab
browser_evaluate(script: "window.open('https://site-b.com')")  // new tab
browser_tabs()  // list tabs to get indices
browser_switch_tab(index: 1)  // switch to second tab
browser_get_text()
```

## Best practices

1. **Always wait after navigation.** Pages need time to load. Use `browser_wait_for` with `event: "networkidle"` or a `selector` for a key element before interacting.

2. **Take screenshots to confirm state.** After important actions (form submit, page load, click), capture a screenshot so you and the user can verify what happened.

3. **Prefer CSS selectors.** Use standard CSS selectors (`#id`, `.class`, `[attribute=value]`, `button[type=submit]`). They are fast and reliable.

4. **Handle popups first.** Cookie banners, login modals, and notification prompts can block interaction. Dismiss them before proceeding with the main task.

5. **Use evaluate for complex queries.** When you need structured data or multiple elements, `browser_evaluate` with JavaScript is more reliable than multiple `get_text` calls.

6. **One action at a time.** Don't try to batch multiple interactions. Execute each step, verify it succeeded (via screenshot or get_text), then proceed.

7. **Close tabs when done.** Don't leave dozens of tabs open. Use `browser_close` when finished with a page.

## Error recovery

- **Element not found**: Verify the page loaded correctly (screenshot), try a broader selector, or wait longer.
- **Timeout**: Increase the timeout parameter or wait for a less specific condition (e.g., `load` instead of `networkidle`).
- **Page changed unexpectedly**: Take a screenshot to see current state, then adapt.
- **Browser not responding**: The MCP server handles browser lifecycle automatically. If tools fail, try `browser_navigate` to a fresh URL -- it will reconnect or relaunch the browser.

## When NOT to use browser-pilot

- Making API calls (use curl, fetch, or HTTP tools instead)
- Reading local files (use filesystem tools)
- Running headless automated tests in CI (this is for interactive headed browsing)
