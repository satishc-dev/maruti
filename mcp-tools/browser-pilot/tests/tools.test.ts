import { describe, it, expect, vi, beforeEach } from "vitest";
import type { IBrowserManager } from "../src/interfaces/index.js";
import type { Page, BrowserContext } from "playwright-core";
import { ToolRegistry } from "../src/tools/ToolRegistry.js";
import { NavigateTool } from "../src/tools/NavigateTool.js";
import { ClickTool } from "../src/tools/ClickTool.js";
import { TypeTool } from "../src/tools/TypeTool.js";
import { GetTextTool } from "../src/tools/GetTextTool.js";
import { ScrollTool } from "../src/tools/ScrollTool.js";
import { EvaluateTool } from "../src/tools/EvaluateTool.js";
import { BackTool } from "../src/tools/BackTool.js";
import { ForwardTool } from "../src/tools/ForwardTool.js";
import { TabsTool } from "../src/tools/TabsTool.js";
import { SwitchTabTool } from "../src/tools/SwitchTabTool.js";
import { CloseTool } from "../src/tools/CloseTool.js";
import { WaitForTool } from "../src/tools/WaitForTool.js";
import { SelectTool } from "../src/tools/SelectTool.js";
import { UploadTool } from "../src/tools/UploadTool.js";
import { CookiesTool } from "../src/tools/CookiesTool.js";
import { PdfTool } from "../src/tools/PdfTool.js";
import { ScreenshotTool } from "../src/tools/ScreenshotTool.js";

function createMockPage(): Page {
  return {
    goto: vi.fn().mockResolvedValue({ status: () => 200 }),
    title: vi.fn().mockResolvedValue("Test Page"),
    url: vi.fn().mockReturnValue("https://example.com"),
    click: vi.fn().mockResolvedValue(undefined),
    type: vi.fn().mockResolvedValue(undefined),
    fill: vi.fn().mockResolvedValue(undefined),
    locator: vi.fn().mockReturnValue({
      first: vi.fn().mockReturnValue({
        innerText: vi.fn().mockResolvedValue("Hello World"),
        screenshot: vi.fn().mockResolvedValue(Buffer.from("fake-png")),
        evaluate: vi.fn().mockResolvedValue(undefined),
        waitFor: vi.fn().mockResolvedValue(undefined),
      }),
    }),
    mouse: { wheel: vi.fn().mockResolvedValue(undefined) },
    evaluate: vi.fn().mockResolvedValue({ key: "value" }),
    goBack: vi.fn().mockResolvedValue(null),
    goForward: vi.fn().mockResolvedValue(null),
    selectOption: vi.fn().mockResolvedValue(["option1"]),
    setInputFiles: vi.fn().mockResolvedValue(undefined),
    pdf: vi.fn().mockResolvedValue(undefined),
    screenshot: vi.fn().mockResolvedValue(Buffer.from("full-page-png")),
    waitForLoadState: vi.fn().mockResolvedValue(undefined),
    close: vi.fn().mockResolvedValue(undefined),
  } as unknown as Page;
}

function createMockBrowserManager(mockPage?: Page): IBrowserManager {
  const page = mockPage ?? createMockPage();
  const mockContext = {
    pages: vi.fn().mockReturnValue([page]),
    cookies: vi.fn().mockResolvedValue([{ name: "session", value: "abc", domain: ".example.com" }]),
    addCookies: vi.fn().mockResolvedValue(undefined),
    clearCookies: vi.fn().mockResolvedValue(undefined),
  } as unknown as BrowserContext;

  return {
    ensureConnected: vi.fn().mockResolvedValue(undefined),
    getActivePage: vi.fn().mockResolvedValue(page),
    getPageByIndex: vi.fn().mockResolvedValue(page),
    getPages: vi.fn().mockResolvedValue([page]),
    switchToPage: vi.fn().mockResolvedValue(page),
    createNewPage: vi.fn().mockResolvedValue(page),
    closePage: vi.fn().mockResolvedValue(undefined),
    getBrowser: vi.fn().mockReturnValue(null),
    getContext: vi.fn().mockReturnValue(mockContext),
    disconnect: vi.fn().mockResolvedValue(undefined),
    isConnected: vi.fn().mockReturnValue(true),
  };
}

describe("ToolRegistry", () => {
  it("should register and retrieve a tool", () => {
    const registry = new ToolRegistry();
    const manager = createMockBrowserManager();
    const tool = new NavigateTool(manager);

    registry.register(tool);
    expect(registry.get("browser_navigate")).toBe(tool);
  });

  it("should throw on duplicate registration", () => {
    const registry = new ToolRegistry();
    const manager = createMockBrowserManager();
    const tool = new NavigateTool(manager);

    registry.register(tool);
    expect(() => registry.register(tool)).toThrow("already registered");
  });

  it("should return undefined for unknown tool", () => {
    const registry = new ToolRegistry();
    expect(registry.get("unknown")).toBeUndefined();
  });

  it("should return all registered tools", () => {
    const registry = new ToolRegistry();
    const manager = createMockBrowserManager();
    registry.registerAll([new NavigateTool(manager), new ClickTool(manager)]);
    expect(registry.getAll()).toHaveLength(2);
    expect(registry.size).toBe(2);
  });
});

describe("NavigateTool", () => {
  let manager: IBrowserManager;
  let tool: NavigateTool;

  beforeEach(() => {
    manager = createMockBrowserManager();
    tool = new NavigateTool(manager);
  });

  it("should have correct metadata", () => {
    expect(tool.name).toBe("browser_navigate");
    expect(tool.description).toBeTruthy();
    expect(tool.inputSchema.required).toContain("url");
  });

  it("should navigate with custom waitUntil", async () => {
    const result = await tool.execute({ url: "https://example.com", waitUntil: "networkidle" });
    expect(result.isError).toBeUndefined();
    expect(result.content[0]!.text).toContain("Navigated to");
  });

  it("should handle null response status", async () => {
    const mockPage = createMockPage();
    (mockPage.goto as ReturnType<typeof vi.fn>).mockResolvedValueOnce(null);
    const mgr = createMockBrowserManager(mockPage);
    const t = new NavigateTool(mgr);
    const result = await t.execute({ url: "about:blank" });
    expect(result.content[0]!.text).toContain("unknown");
  });

  it("should return error for missing URL", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
    expect(result.content[0]!.text).toContain("Missing required argument");
  });
});

describe("ClickTool", () => {
  let tool: ClickTool;

  beforeEach(() => {
    tool = new ClickTool(createMockBrowserManager());
  });

  it("should click an element", async () => {
    const result = await tool.execute({ selector: "#btn" });
    expect(result.content[0]!.text).toContain("Clicked element: #btn");
  });

  it("should return error for missing selector", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
  });
});

describe("TypeTool", () => {
  let tool: TypeTool;

  beforeEach(() => {
    tool = new TypeTool(createMockBrowserManager());
  });

  it("should type text into input", async () => {
    const result = await tool.execute({ selector: "#input", text: "hello" });
    expect(result.content[0]!.text).toContain('Typed "hello"');
  });

  it("should clear input before typing when clear is true", async () => {
    const mockPage = createMockPage();
    const mgr = createMockBrowserManager(mockPage);
    const t = new TypeTool(mgr);
    await t.execute({ selector: "#input", text: "hello", clear: true });
    expect(mockPage.fill).toHaveBeenCalledWith("#input", "");
  });

  it("should return error for missing args", async () => {
    const result = await tool.execute({ selector: "#input" });
    expect(result.isError).toBe(true);
  });
});

describe("ScreenshotTool", () => {
  let tool: ScreenshotTool;

  beforeEach(() => {
    tool = new ScreenshotTool(createMockBrowserManager());
  });

  it("should take full page screenshot", async () => {
    const result = await tool.execute({ fullPage: true });
    expect(result.content[0]!.type).toBe("image");
    expect(result.content[0]!.mimeType).toBe("image/png");
  });

  it("should take element screenshot", async () => {
    const result = await tool.execute({ selector: "#logo" });
    expect(result.content[0]!.type).toBe("image");
  });
});

describe("GetTextTool", () => {
  let tool: GetTextTool;

  beforeEach(() => {
    tool = new GetTextTool(createMockBrowserManager());
  });

  it("should get text from page body by default", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toBe("Hello World");
  });

  it("should get text from specific selector", async () => {
    const result = await tool.execute({ selector: "#content" });
    expect(result.content[0]!.text).toBe("Hello World");
  });
});

describe("ScrollTool", () => {
  let tool: ScrollTool;
  let mockPage: Page;

  beforeEach(() => {
    mockPage = createMockPage();
    tool = new ScrollTool(createMockBrowserManager(mockPage));
  });

  it("should scroll down by default", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toContain("Scrolled down by 500px");
    expect(mockPage.mouse.wheel).toHaveBeenCalledWith(0, 500);
  });

  it("should scroll up", async () => {
    const result = await tool.execute({ direction: "up", amount: 300 });
    expect(result.content[0]!.text).toContain("Scrolled up by 300px");
  });

  it("should scroll element when selector provided", async () => {
    await tool.execute({ direction: "down", selector: "#container" });
    expect(mockPage.locator).toHaveBeenCalledWith("#container");
  });

  it("should scroll left", async () => {
    const result = await tool.execute({ direction: "left", amount: 200 });
    expect(result.content[0]!.text).toContain("Scrolled left by 200px");
    expect(mockPage.mouse.wheel).toHaveBeenCalledWith(-200, 0);
  });

  it("should scroll right", async () => {
    const result = await tool.execute({ direction: "right", amount: 100 });
    expect(result.content[0]!.text).toContain("Scrolled right by 100px");
    expect(mockPage.mouse.wheel).toHaveBeenCalledWith(100, 0);
  });
});

describe("WaitForTool", () => {
  let tool: WaitForTool;

  beforeEach(() => {
    tool = new WaitForTool(createMockBrowserManager());
  });

  it("should wait for selector", async () => {
    const result = await tool.execute({ selector: "#loading" });
    expect(result.content[0]!.text).toContain("is now visible");
  });

  it("should wait for load event", async () => {
    const result = await tool.execute({ event: "networkidle" });
    expect(result.content[0]!.text).toContain("networkidle");
  });

  it("should error if neither selector nor event provided", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
    expect(result.content[0]!.text).toContain("Either 'selector' or 'event'");
  });
});

describe("EvaluateTool", () => {
  let tool: EvaluateTool;

  beforeEach(() => {
    tool = new EvaluateTool(createMockBrowserManager());
  });

  it("should evaluate JavaScript", async () => {
    const result = await tool.execute({ script: "document.title" });
    expect(result.content[0]!.text).toContain("key");
  });

  it("should return error for missing script", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
  });

  it("should handle undefined result", async () => {
    const mockPage = createMockPage();
    (mockPage.evaluate as ReturnType<typeof vi.fn>).mockResolvedValueOnce(undefined);
    const mgr = createMockBrowserManager(mockPage);
    const t = new EvaluateTool(mgr);
    const result = await t.execute({ script: "void 0" });
    expect(result.content[0]!.text).toBe("undefined");
  });
});

describe("SelectTool", () => {
  let tool: SelectTool;

  beforeEach(() => {
    tool = new SelectTool(createMockBrowserManager());
  });

  it("should select by value", async () => {
    const result = await tool.execute({ selector: "#dropdown", value: "opt1" });
    expect(result.content[0]!.text).toContain("Selected option(s)");
  });

  it("should select by label", async () => {
    const result = await tool.execute({ selector: "#dropdown", label: "Option 1" });
    expect(result.content[0]!.text).toContain("Selected option(s)");
  });

  it("should error if neither value nor label", async () => {
    const result = await tool.execute({ selector: "#dropdown" });
    expect(result.isError).toBe(true);
    expect(result.content[0]!.text).toContain("Either 'value' or 'label'");
  });
});

describe("UploadTool", () => {
  let tool: UploadTool;

  beforeEach(() => {
    tool = new UploadTool(createMockBrowserManager());
  });

  it("should upload files", async () => {
    const result = await tool.execute({ selector: "#file", filePaths: ["/tmp/test.pdf"] });
    expect(result.content[0]!.text).toContain("Uploaded 1 file(s)");
  });

  it("should error for missing args", async () => {
    const result = await tool.execute({ selector: "#file" });
    expect(result.isError).toBe(true);
  });
});

describe("CookiesTool", () => {
  let tool: CookiesTool;

  beforeEach(() => {
    tool = new CookiesTool(createMockBrowserManager());
  });

  it("should get cookies", async () => {
    const result = await tool.execute({ action: "get" });
    expect(result.content[0]!.text).toContain("session");
  });

  it("should get cookies by URL", async () => {
    const result = await tool.execute({ action: "get", url: "https://example.com" });
    expect(result.isError).toBeUndefined();
  });

  it("should set a cookie", async () => {
    const result = await tool.execute({ action: "set", name: "test", value: "123", domain: ".example.com" });
    expect(result.content[0]!.text).toContain("Cookie 'test' set");
  });

  it("should error on set without required fields", async () => {
    const result = await tool.execute({ action: "set", name: "test" });
    expect(result.isError).toBe(true);
  });

  it("should delete a cookie", async () => {
    const result = await tool.execute({ action: "delete", name: "session" });
    expect(result.content[0]!.text).toContain("Cookie 'session' deleted");
  });

  it("should error on delete without name", async () => {
    const result = await tool.execute({ action: "delete" });
    expect(result.isError).toBe(true);
  });

  it("should clear all cookies", async () => {
    const result = await tool.execute({ action: "clear" });
    expect(result.content[0]!.text).toContain("All cookies cleared");
  });

  it("should error on unknown action", async () => {
    const result = await tool.execute({ action: "invalid" });
    expect(result.isError).toBe(true);
    expect(result.content[0]!.text).toContain("Unknown cookie action");
  });

  it("should error on missing action", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
  });

  it("should error when no browser context available", async () => {
    const noContextManager: IBrowserManager = {
      ...createMockBrowserManager(),
      getContext: vi.fn().mockReturnValue(null),
    };
    const t = new CookiesTool(noContextManager);
    const result = await t.execute({ action: "get" });
    expect(result.isError).toBe(true);
    expect(result.content[0]!.text).toContain("No browser context");
  });
});

describe("PdfTool", () => {
  let tool: PdfTool;

  beforeEach(() => {
    tool = new PdfTool(createMockBrowserManager());
  });

  it("should save PDF", async () => {
    const result = await tool.execute({ path: "/tmp/output.pdf" });
    expect(result.content[0]!.text).toContain("PDF saved to: /tmp/output.pdf");
  });

  it("should error for missing path", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
  });
});

describe("BackTool", () => {
  let tool: BackTool;

  beforeEach(() => {
    tool = new BackTool(createMockBrowserManager());
  });

  it("should navigate back", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toContain("Navigated back to");
  });
});

describe("ForwardTool", () => {
  let tool: ForwardTool;

  beforeEach(() => {
    tool = new ForwardTool(createMockBrowserManager());
  });

  it("should navigate forward", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toContain("Navigated forward to");
  });
});

describe("CloseTool", () => {
  let tool: CloseTool;
  let manager: IBrowserManager;

  beforeEach(() => {
    manager = createMockBrowserManager();
    tool = new CloseTool(manager);
  });

  it("should close active tab", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toContain("Tab active closed");
  });

  it("should close specific tab by index", async () => {
    const result = await tool.execute({ tabIndex: 0 });
    expect(result.content[0]!.text).toContain("Tab 0 closed");
  });

  it("should disconnect all when all is true", async () => {
    const result = await tool.execute({ all: true });
    expect(result.content[0]!.text).toContain("Browser disconnected");
    expect(manager.disconnect).toHaveBeenCalled();
  });
});

describe("TabsTool", () => {
  let tool: TabsTool;

  beforeEach(() => {
    tool = new TabsTool(createMockBrowserManager());
  });

  it("should list all tabs", async () => {
    const result = await tool.execute({});
    expect(result.content[0]!.text).toContain("[0]");
    expect(result.content[0]!.text).toContain("Test Page");
  });

  it("should show (untitled) for pages with empty title", async () => {
    const mockPage = createMockPage();
    (mockPage.title as ReturnType<typeof vi.fn>).mockResolvedValue("");
    const mgr: IBrowserManager = {
      ...createMockBrowserManager(mockPage),
      getPages: vi.fn().mockResolvedValue([mockPage]),
    };
    const t = new TabsTool(mgr);
    const result = await t.execute({});
    expect(result.content[0]!.text).toContain("(untitled)");
  });
});

describe("SwitchTabTool", () => {
  let tool: SwitchTabTool;

  beforeEach(() => {
    tool = new SwitchTabTool(createMockBrowserManager());
  });

  it("should switch to specified tab", async () => {
    const result = await tool.execute({ index: 0 });
    expect(result.content[0]!.text).toContain("Switched to tab [0]");
  });

  it("should show (untitled) when page has no title", async () => {
    const mockPage = createMockPage();
    (mockPage.title as ReturnType<typeof vi.fn>).mockResolvedValue("");
    const mgr: IBrowserManager = {
      ...createMockBrowserManager(mockPage),
      switchToPage: vi.fn().mockResolvedValue(mockPage),
    };
    const t = new SwitchTabTool(mgr);
    const result = await t.execute({ index: 0 });
    expect(result.content[0]!.text).toContain("(untitled)");
  });

  it("should error for missing index", async () => {
    const result = await tool.execute({});
    expect(result.isError).toBe(true);
  });
});
