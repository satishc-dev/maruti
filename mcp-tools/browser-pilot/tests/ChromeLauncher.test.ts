import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import type { IChromeLocator } from "../src/interfaces/index.js";
import { ChromeLauncher } from "../src/chrome/ChromeLauncher.js";

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

// Mock child_process
vi.mock("node:child_process", () => ({
  spawn: vi.fn().mockReturnValue({
    unref: vi.fn(),
    kill: vi.fn(),
    on: vi.fn(),
    pid: 12345,
  }),
}));

class MockChromeLocator implements IChromeLocator {
  private readonly path: string | null;
  public constructor(path: string | null = "/usr/bin/google-chrome") {
    this.path = path;
  }
  public async locate(): Promise<string | null> {
    return this.path;
  }
}

describe("ChromeLauncher", () => {
  let launcher: ChromeLauncher;

  beforeEach(() => {
    vi.clearAllMocks();
    launcher = new ChromeLauncher(new MockChromeLocator());
  });

  afterEach(async () => {
    await launcher.shutdown();
  });

  describe("launch", () => {
    it("should connect to existing Chrome if debug port is active", async () => {
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch();

      expect(launcher.isRunning()).toBe(true);
      expect(launcher.getProcess()).toBeNull(); // didn't spawn
    });

    it("should throw if Chrome is not found and no custom path", async () => {
      const noChromeLauncher = new ChromeLauncher(new MockChromeLocator(null));
      mockFetch.mockRejectedValue(new Error("connection refused"));

      await expect(noChromeLauncher.launch()).rejects.toThrow("Chrome executable not found");
    });

    it("should spawn Chrome when debug port is not active", async () => {
      const { spawn } = await import("node:child_process");

      // Port not active initially, then becomes active
      mockFetch
        .mockRejectedValueOnce(new Error("connection refused")) // initial check
        .mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) }); // after spawn

      await launcher.launch({ port: 9222 });

      expect(spawn).toHaveBeenCalled();
      expect(launcher.isRunning()).toBe(true);
    });

    it("should not re-launch if already running", async () => {
      mockFetch.mockResolvedValue({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch();
      await launcher.launch(); // second call should be no-op

      expect(launcher.isRunning()).toBe(true);
    });

    it("should use custom port", async () => {
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9333" }) });

      await launcher.launch({ port: 9333 });

      expect(launcher.getPort()).toBe(9333);
    });

    it("should use custom chromePath", async () => {
      const { spawn } = await import("node:child_process");

      mockFetch
        .mockRejectedValueOnce(new Error("connection refused"))
        .mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch({ chromePath: "/custom/chrome" });

      expect(spawn).toHaveBeenCalledWith("/custom/chrome", expect.any(Array), expect.any(Object));
    });

    it("should pass headless flag when specified", async () => {
      const { spawn } = await import("node:child_process");

      mockFetch
        .mockRejectedValueOnce(new Error("connection refused"))
        .mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch({ headless: true });

      const args = (spawn as ReturnType<typeof vi.fn>).mock.calls[0]?.[1] as string[];
      expect(args).toContain("--headless=new");
    });

    it("should use temp profile when useExistingProfile is false", async () => {
      const { spawn } = await import("node:child_process");

      mockFetch
        .mockRejectedValueOnce(new Error("connection refused"))
        .mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch({ useExistingProfile: false });

      const args = (spawn as ReturnType<typeof vi.fn>).mock.calls[0]?.[1] as string[];
      expect(args.some((a: string) => a.startsWith("--user-data-dir="))).toBe(true);
    });

    it("should throw if Chrome fails to start after retries", async () => {
      mockFetch.mockRejectedValue(new Error("connection refused"));

      await expect(launcher.launch()).rejects.toThrow("Chrome failed to start debugging");
    }, 30000);
  });

  describe("shutdown", () => {
    it("should kill the process and mark as not running", async () => {
      mockFetch
        .mockRejectedValueOnce(new Error("connection refused"))
        .mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://127.0.0.1:9222" }) });

      await launcher.launch();
      await launcher.shutdown();

      expect(launcher.isRunning()).toBe(false);
      expect(launcher.getProcess()).toBeNull();
    });

    it("should be safe to call when not running", async () => {
      await expect(launcher.shutdown()).resolves.toBeUndefined();
    });
  });

  describe("getDebuggerUrl", () => {
    it("should fetch and return the WebSocket URL", async () => {
      const wsUrl = "ws://127.0.0.1:9222/devtools/browser/abc123";
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ webSocketDebuggerUrl: wsUrl }),
      });

      // Launch first
      await launcher.launch();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ webSocketDebuggerUrl: wsUrl }),
      });

      const url = await launcher.getDebuggerUrl();
      expect(url).toBe(wsUrl);
    });

    it("should throw if HTTP request fails", async () => {
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ webSocketDebuggerUrl: "ws://x" }) });
      await launcher.launch();

      mockFetch.mockResolvedValueOnce({ ok: false, status: 500 });

      await expect(launcher.getDebuggerUrl()).rejects.toThrow("Failed to get debugger URL");
    });
  });

  describe("getPort", () => {
    it("should return the default port", () => {
      expect(launcher.getPort()).toBe(9222);
    });
  });
});
