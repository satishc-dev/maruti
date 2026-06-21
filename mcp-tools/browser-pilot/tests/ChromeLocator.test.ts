import { describe, it, expect, vi, beforeEach } from "vitest";
import { BrowserLocatorFactory } from "../src/chrome/BrowserLocatorFactory.js";
import { WindowsBrowserLocator } from "../src/chrome/WindowsBrowserLocator.js";
import { MacBrowserLocator } from "../src/chrome/MacBrowserLocator.js";
import { LinuxBrowserLocator } from "../src/chrome/LinuxBrowserLocator.js";
import * as fs from "node:fs/promises";

vi.mock("node:fs/promises", () => ({
  access: vi.fn(),
}));

describe("BrowserLocatorFactory", () => {
  it("should return WindowsBrowserLocator for win32", () => {
    const locator = BrowserLocatorFactory.create("win32");
    expect(locator).toBeInstanceOf(WindowsBrowserLocator);
  });

  it("should return MacBrowserLocator for darwin", () => {
    const locator = BrowserLocatorFactory.create("darwin");
    expect(locator).toBeInstanceOf(MacBrowserLocator);
  });

  it("should return LinuxBrowserLocator for linux", () => {
    const locator = BrowserLocatorFactory.create("linux");
    expect(locator).toBeInstanceOf(LinuxBrowserLocator);
  });

  it("should throw for unsupported platform", () => {
    expect(() => BrowserLocatorFactory.create("freebsd" as NodeJS.Platform))
      .toThrow("Unsupported platform: freebsd");
  });

  it("should use process.platform when no platform provided", () => {
    const locator = BrowserLocatorFactory.create();
    expect(locator).toBeDefined();
  });
});

describe("WindowsBrowserLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when no browser is found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new WindowsBrowserLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return Chrome when it is found first", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new WindowsBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Chrome");
    expect(result!.path).toContain("chrome.exe");
  });

  it("should return Edge when Chrome is not found", async () => {
    // Reject for all 3 Chrome paths, then resolve for first Edge path
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new WindowsBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Edge");
    expect(result!.path).toContain("msedge.exe");
  });

  it("should return Brave when Chrome and Edge are not found", async () => {
    // Reject for 3 Chrome + 2 Edge = 5, then resolve for Brave
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new WindowsBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Brave");
    expect(result!.path).toContain("brave.exe");
  });
});

describe("MacBrowserLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when no browser is found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new MacBrowserLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return Chrome when it is found first", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new MacBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Chrome");
    expect(result!.path).toContain("Google Chrome");
  });

  it("should return Edge when Chrome is not found", async () => {
    // Reject for 2 Chrome paths, resolve for Edge
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new MacBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Edge");
    expect(result!.path).toContain("Microsoft Edge");
  });

  it("should return Chromium as last resort", async () => {
    // Reject for 2 Chrome + 1 Edge + 1 Brave = 4, resolve for Chromium
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new MacBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Chromium");
  });
});

describe("LinuxBrowserLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when no browser is found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new LinuxBrowserLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return Chrome when it is found first", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new LinuxBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Chrome");
    expect(result!.path).toContain("google-chrome");
  });

  it("should return Edge when Chrome is not found", async () => {
    // Reject for 2 Chrome paths, resolve for Edge
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new LinuxBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Edge");
    expect(result!.path).toContain("microsoft-edge");
  });

  it("should return Chromium as last resort", async () => {
    // Reject for 2 Chrome + 2 Edge + 1 Brave = 5, resolve for Chromium
    vi.mocked(fs.access)
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockRejectedValueOnce(new Error("ENOENT"))
      .mockResolvedValueOnce(undefined);
    const locator = new LinuxBrowserLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result!.name).toBe("Chromium");
  });
});
