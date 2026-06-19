import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserPilotServer } from "../src/server/BrowserPilotServer.js";
import type { IChromeLauncher, IBrowserManager } from "../src/interfaces/index.js";
import type { ChildProcess } from "node:child_process";
import type { Browser, BrowserContext, Page } from "playwright-core";

const mockSetRequestHandler = vi.fn();
vi.mock("@modelcontextprotocol/sdk/server/index.js", () => ({
  Server: class MockServer {
    setRequestHandler = mockSetRequestHandler;
    connect = vi.fn().mockResolvedValue(undefined);
    close = vi.fn().mockResolvedValue(undefined);
  },
}));

vi.mock("@modelcontextprotocol/sdk/server/stdio.js", () => ({
  StdioServerTransport: class MockTransport {},
}));

vi.mock("@modelcontextprotocol/sdk/types.js", () => ({
  CallToolRequestSchema: "CallToolRequestSchema",
  ListToolsRequestSchema: "ListToolsRequestSchema",
}));

function createMockLauncher(): IChromeLauncher {
  return {
    launch: vi.fn().mockResolvedValue(undefined),
    shutdown: vi.fn().mockResolvedValue(undefined),
    getDebuggerUrl: vi.fn().mockResolvedValue("ws://127.0.0.1:9222"),
    getPort: vi.fn().mockReturnValue(9222),
    isRunning: vi.fn().mockReturnValue(true),
    getProcess: vi.fn().mockReturnValue(null),
  };
}

function createMockBrowserManager(): IBrowserManager {
  const mockPage = {
    title: vi.fn().mockResolvedValue("Test"),
    url: vi.fn().mockReturnValue("about:blank"),
  } as unknown as Page;

  return {
    ensureConnected: vi.fn().mockResolvedValue(undefined),
    getActivePage: vi.fn().mockResolvedValue(mockPage),
    getPageByIndex: vi.fn().mockResolvedValue(mockPage),
    getPages: vi.fn().mockResolvedValue([mockPage]),
    switchToPage: vi.fn().mockResolvedValue(mockPage),
    createNewPage: vi.fn().mockResolvedValue(mockPage),
    closePage: vi.fn().mockResolvedValue(undefined),
    getBrowser: vi.fn().mockReturnValue(null),
    getContext: vi.fn().mockReturnValue(null),
    disconnect: vi.fn().mockResolvedValue(undefined),
    isConnected: vi.fn().mockReturnValue(true),
  };
}

describe("BrowserPilotServer", () => {
  let server: BrowserPilotServer;
  let mockLauncher: IChromeLauncher;
  let mockManager: IBrowserManager;

  beforeEach(() => {
    mockSetRequestHandler.mockReset();
    mockLauncher = createMockLauncher();
    mockManager = createMockBrowserManager();
    server = new BrowserPilotServer(mockLauncher, mockManager);
  });

  it("should register all 17 tools", () => {
    const registry = server.getToolRegistry();
    expect(registry.size).toBe(17);
  });

  it("should register tools with expected names", () => {
    const registry = server.getToolRegistry();
    const expectedNames = [
      "browser_navigate", "browser_click", "browser_type",
      "browser_screenshot", "browser_get_text", "browser_scroll",
      "browser_wait_for", "browser_evaluate", "browser_select",
      "browser_upload", "browser_cookies", "browser_pdf",
      "browser_back", "browser_forward", "browser_close",
      "browser_tabs", "browser_switch_tab",
    ];
    for (const name of expectedNames) {
      expect(registry.get(name)).toBeDefined();
    }
  });

  it("should start without throwing", async () => {
    await expect(server.start()).resolves.toBeUndefined();
  });

  it("should shutdown cleanly", async () => {
    await server.shutdown();
    expect(mockManager.disconnect).toHaveBeenCalled();
    expect(mockLauncher.shutdown).toHaveBeenCalled();
  });

  describe("request handlers", () => {
    it("ListTools handler should return all tools", async () => {
      // Find the ListTools handler
      const listToolsCall = mockSetRequestHandler.mock.calls.find(
        (call) => call[0] === "ListToolsRequestSchema"
      );
      expect(listToolsCall).toBeDefined();

      const handler = listToolsCall![1];
      const result = await handler({});
      expect(result.tools).toHaveLength(17);
      expect(result.tools[0]).toHaveProperty("name");
      expect(result.tools[0]).toHaveProperty("description");
      expect(result.tools[0]).toHaveProperty("inputSchema");
    });

    it("CallTool handler should execute a known tool", async () => {
      const callToolCall = mockSetRequestHandler.mock.calls.find(
        (call) => call[0] === "CallToolRequestSchema"
      );
      expect(callToolCall).toBeDefined();

      const handler = callToolCall![1];
      const result = await handler({
        params: { name: "browser_tabs", arguments: {} },
      });
      expect(result.content).toBeDefined();
      expect(result.isError).toBeUndefined();
    });

    it("CallTool handler should return error for unknown tool", async () => {
      const callToolCall = mockSetRequestHandler.mock.calls.find(
        (call) => call[0] === "CallToolRequestSchema"
      );
      const handler = callToolCall![1];
      const result = await handler({
        params: { name: "nonexistent_tool", arguments: {} },
      });
      expect(result.isError).toBe(true);
      expect(result.content[0].text).toContain("Unknown tool");
    });

    it("CallTool handler should handle missing arguments gracefully", async () => {
      const callToolCall = mockSetRequestHandler.mock.calls.find(
        (call) => call[0] === "CallToolRequestSchema"
      );
      const handler = callToolCall![1];
      const result = await handler({
        params: { name: "browser_navigate" },
      });
      // Should get error about missing url
      expect(result.isError).toBe(true);
    });

    it("CallTool handler should return image content for screenshot", async () => {
      // Need a new server instance with a full mock that supports screenshot
      const screenshotPage = {
        title: vi.fn().mockResolvedValue("Test"),
        url: vi.fn().mockReturnValue("about:blank"),
        screenshot: vi.fn().mockResolvedValue(Buffer.from("png-data")),
        locator: vi.fn().mockReturnValue({
          first: vi.fn().mockReturnValue({
            screenshot: vi.fn().mockResolvedValue(Buffer.from("el-png")),
          }),
        }),
      } as unknown as Page;

      const fullManager: IBrowserManager = {
        ensureConnected: vi.fn().mockResolvedValue(undefined),
        getActivePage: vi.fn().mockResolvedValue(screenshotPage),
        getPageByIndex: vi.fn().mockResolvedValue(screenshotPage),
        getPages: vi.fn().mockResolvedValue([screenshotPage]),
        switchToPage: vi.fn().mockResolvedValue(screenshotPage),
        createNewPage: vi.fn().mockResolvedValue(screenshotPage),
        closePage: vi.fn().mockResolvedValue(undefined),
        getBrowser: vi.fn().mockReturnValue(null),
        getContext: vi.fn().mockReturnValue(null),
        disconnect: vi.fn().mockResolvedValue(undefined),
        isConnected: vi.fn().mockReturnValue(true),
      };

      // Creating a new server registers handlers
      const _screenshotServer = new BrowserPilotServer(mockLauncher, fullManager);
      // The last CallToolRequestSchema handler is from the new server
      const calls = mockSetRequestHandler.mock.calls.filter(
        (call) => call[0] === "CallToolRequestSchema"
      );
      const handler = calls[calls.length - 1]![1];
      const result = await handler({
        params: { name: "browser_screenshot", arguments: {} },
      });
      expect(result.content[0].type).toBe("image");
      expect(result.content[0].data).toBeDefined();
      expect(result.content[0].mimeType).toBe("image/png");
    });
  });
});
