import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { BrowserManager } from "../src/browser/BrowserManager.js";
import type { IChromeLauncher } from "../src/interfaces/index.js";
import type { ChildProcess } from "node:child_process";

// Mock playwright-core
const createMockPlaywrightPage = () => ({
  title: vi.fn().mockResolvedValue("Test Page"),
  url: vi.fn().mockReturnValue("https://example.com"),
  close: vi.fn().mockResolvedValue(undefined),
  goto: vi.fn().mockResolvedValue({ status: () => 200 }),
});

let mockPages = [createMockPlaywrightPage()];

vi.mock("playwright-core", () => {
  const mockContext = {
    pages: vi.fn().mockImplementation(() => mockPages),
    newPage: vi.fn().mockImplementation(() => {
      const page = createMockPlaywrightPage();
      mockPages.push(page);
      return Promise.resolve(page);
    }),
    cookies: vi.fn().mockResolvedValue([]),
    addCookies: vi.fn().mockResolvedValue(undefined),
    clearCookies: vi.fn().mockResolvedValue(undefined),
  };

  const mockBrowser = {
    isConnected: vi.fn().mockReturnValue(true),
    contexts: vi.fn().mockReturnValue([mockContext]),
    newContext: vi.fn().mockResolvedValue(mockContext),
    close: vi.fn().mockResolvedValue(undefined),
    on: vi.fn(),
  };

  return {
    chromium: {
      connectOverCDP: vi.fn().mockResolvedValue(mockBrowser),
    },
  };
});

class MockChromeLauncher implements IChromeLauncher {
  private running: boolean = true;

  public async launch(): Promise<void> {
    this.running = true;
  }
  public async shutdown(): Promise<void> {
    this.running = false;
  }
  public async getDebuggerUrl(): Promise<string> {
    return "ws://127.0.0.1:9222/devtools/browser/test";
  }
  public getPort(): number {
    return 9222;
  }
  public isRunning(): boolean {
    return this.running;
  }
  public getProcess(): ChildProcess | null {
    return null;
  }
}

describe("BrowserManager", () => {
  let manager: BrowserManager;
  let launcher: MockChromeLauncher;

  beforeEach(() => {
    BrowserManager.resetInstance();
    mockPages = [createMockPlaywrightPage()];
    launcher = new MockChromeLauncher();
    manager = BrowserManager.getInstance(launcher);
  });

  afterEach(async () => {
    await manager.disconnect();
    BrowserManager.resetInstance();
  });

  describe("getInstance", () => {
    it("should return the same instance (singleton)", () => {
      const instance1 = BrowserManager.getInstance(launcher);
      const instance2 = BrowserManager.getInstance(launcher);
      expect(instance1).toBe(instance2);
    });

    it("should return fresh instance after reset", () => {
      const instance1 = BrowserManager.getInstance(launcher);
      BrowserManager.resetInstance();
      const instance2 = BrowserManager.getInstance(launcher);
      expect(instance1).not.toBe(instance2);
    });
  });

  describe("ensureConnected", () => {
    it("should connect to Chrome via CDP", async () => {
      await manager.ensureConnected();
      expect(manager.isConnected()).toBe(true);
    });

    it("should not reconnect if already connected", async () => {
      await manager.ensureConnected();
      await manager.ensureConnected(); // second call is no-op
      expect(manager.isConnected()).toBe(true);
    });

    it("should launch Chrome if not running", async () => {
      const stoppedLauncher = new MockChromeLauncher();
      await stoppedLauncher.shutdown();
      BrowserManager.resetInstance();
      const mgr = BrowserManager.getInstance(stoppedLauncher);

      await mgr.ensureConnected();
      expect(mgr.isConnected()).toBe(true);
    });

    it("should create new context if browser has no existing contexts", async () => {
      // Override the mock to return empty contexts
      const { chromium } = await import("playwright-core");
      const mockBrowserNoContexts = {
        isConnected: vi.fn().mockReturnValue(true),
        contexts: vi.fn().mockReturnValue([]),
        newContext: vi.fn().mockResolvedValue({
          pages: vi.fn().mockReturnValue(mockPages),
          newPage: vi.fn().mockResolvedValue(createMockPlaywrightPage()),
        }),
        close: vi.fn().mockResolvedValue(undefined),
        on: vi.fn(),
      };
      vi.mocked(chromium.connectOverCDP).mockResolvedValueOnce(mockBrowserNoContexts as never);

      BrowserManager.resetInstance();
      const mgr = BrowserManager.getInstance(launcher);
      await mgr.ensureConnected();
      expect(mockBrowserNoContexts.newContext).toHaveBeenCalled();
    });

    it("should handle browser disconnection event", async () => {
      const { chromium } = await import("playwright-core");
      let disconnectHandler: (() => void) | undefined;
      const mockBrowserWithEvent = {
        isConnected: vi.fn().mockReturnValue(true),
        contexts: vi.fn().mockReturnValue([{
          pages: vi.fn().mockReturnValue(mockPages),
          newPage: vi.fn().mockResolvedValue(createMockPlaywrightPage()),
        }]),
        close: vi.fn().mockResolvedValue(undefined),
        on: vi.fn().mockImplementation((event: string, handler: () => void) => {
          if (event === "disconnected") disconnectHandler = handler;
        }),
      };
      vi.mocked(chromium.connectOverCDP).mockResolvedValueOnce(mockBrowserWithEvent as never);

      BrowserManager.resetInstance();
      const mgr = BrowserManager.getInstance(launcher);
      await mgr.ensureConnected();
      expect(mgr.isConnected()).toBe(true);

      // Simulate disconnection
      disconnectHandler!();
      expect(mgr.isConnected()).toBe(false);
    });
  });

  describe("getActivePage", () => {
    it("should return the first page by default", async () => {
      const page = await manager.getActivePage();
      expect(page).toBeDefined();
      expect(await page.title()).toBe("Test Page");
    });

    it("should create a new page if no pages exist", async () => {
      mockPages.length = 0;
      const page = await manager.getActivePage();
      expect(page).toBeDefined();
      // newPage was called, so mockPages should have one element now
      expect(mockPages.length).toBe(1);
    });

    it("should clamp activePageIndex when it exceeds page count", async () => {
      // Start with 2 pages
      mockPages.push(createMockPlaywrightPage());
      await manager.ensureConnected();
      await manager.switchToPage(1);
      // Now remove page 1 externally
      mockPages.splice(1, 1);
      // getActivePage should clamp index to 0
      const page = await manager.getActivePage();
      expect(page).toBeDefined();
    });
  });

  describe("getPages", () => {
    it("should return all pages", async () => {
      const pages = await manager.getPages();
      expect(pages.length).toBeGreaterThan(0);
    });
  });

  describe("getPageByIndex", () => {
    it("should return the page at given index", async () => {
      const page = await manager.getPageByIndex(0);
      expect(page).toBeDefined();
    });

    it("should throw for invalid index", async () => {
      await manager.ensureConnected();
      await expect(manager.getPageByIndex(99)).rejects.toThrow("Invalid page index");
    });

    it("should throw for negative index", async () => {
      await manager.ensureConnected();
      await expect(manager.getPageByIndex(-1)).rejects.toThrow("Invalid page index");
    });
  });

  describe("switchToPage", () => {
    it("should switch active page", async () => {
      const page = await manager.switchToPage(0);
      expect(page).toBeDefined();
    });
  });

  describe("createNewPage", () => {
    it("should create and return a new page", async () => {
      const page = await manager.createNewPage();
      expect(page).toBeDefined();
    });
  });

  describe("closePage", () => {
    it("should close the page at given index", async () => {
      await manager.ensureConnected();
      const pageBefore = mockPages[0]!;
      await manager.closePage(0);
      expect(pageBefore.close).toHaveBeenCalled();
    });

    it("should throw for invalid index", async () => {
      await manager.ensureConnected();
      await expect(manager.closePage(99)).rejects.toThrow("Invalid page index");
    });

    it("should throw for negative index", async () => {
      await manager.ensureConnected();
      await expect(manager.closePage(-1)).rejects.toThrow("Invalid page index");
    });

    it("should disconnect when closing the last page", async () => {
      await manager.ensureConnected();
      // Simulate: after close, pages becomes empty
      const page = mockPages[0]!;
      page.close.mockImplementation(async () => {
        mockPages.length = 0;
      });

      await manager.closePage(0);
      expect(manager.isConnected()).toBe(false);
    });

    it("should adjust activePageIndex when closing causes overflow", async () => {
      // Add a second page
      mockPages.push(createMockPlaywrightPage());
      await manager.ensureConnected();
      // Switch to page 1
      await manager.switchToPage(1);
      // Close page 1 — it removes itself, leaving only page 0
      const page1 = mockPages[1]!;
      page1.close.mockImplementation(async () => {
        mockPages.splice(1, 1);
      });

      await manager.closePage(1);
      // activePageIndex should be clamped to 0
      const activePage = await manager.getActivePage();
      expect(activePage).toBeDefined();
    });
  });

  describe("disconnect", () => {
    it("should disconnect from browser", async () => {
      await manager.ensureConnected();
      await manager.disconnect();
      expect(manager.isConnected()).toBe(false);
      expect(manager.getBrowser()).toBeNull();
      expect(manager.getContext()).toBeNull();
    });

    it("should be safe to call when not connected", async () => {
      await expect(manager.disconnect()).resolves.toBeUndefined();
    });
  });

  describe("getBrowser / getContext", () => {
    it("should return null before connection", () => {
      BrowserManager.resetInstance();
      const fresh = new BrowserManager(launcher);
      expect(fresh.getBrowser()).toBeNull();
      expect(fresh.getContext()).toBeNull();
    });

    it("should return instances after connection", async () => {
      await manager.ensureConnected();
      expect(manager.getBrowser()).not.toBeNull();
      expect(manager.getContext()).not.toBeNull();
    });
  });
});
