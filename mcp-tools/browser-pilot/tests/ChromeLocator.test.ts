import { describe, it, expect, vi, beforeEach } from "vitest";
import { ChromeLocatorFactory } from "../src/chrome/ChromeLocatorFactory.js";
import { WindowsChromeLocator } from "../src/chrome/WindowsChromeLocator.js";
import { MacChromeLocator } from "../src/chrome/MacChromeLocator.js";
import { LinuxChromeLocator } from "../src/chrome/LinuxChromeLocator.js";
import * as fs from "node:fs/promises";

vi.mock("node:fs/promises", () => ({
  access: vi.fn(),
}));

describe("ChromeLocatorFactory", () => {
  it("should return WindowsChromeLocator for win32", () => {
    const locator = ChromeLocatorFactory.create("win32");
    expect(locator).toBeInstanceOf(WindowsChromeLocator);
  });

  it("should return MacChromeLocator for darwin", () => {
    const locator = ChromeLocatorFactory.create("darwin");
    expect(locator).toBeInstanceOf(MacChromeLocator);
  });

  it("should return LinuxChromeLocator for linux", () => {
    const locator = ChromeLocatorFactory.create("linux");
    expect(locator).toBeInstanceOf(LinuxChromeLocator);
  });

  it("should throw for unsupported platform", () => {
    expect(() => ChromeLocatorFactory.create("freebsd" as NodeJS.Platform))
      .toThrow("Unsupported platform: freebsd");
  });

  it("should use process.platform when no platform provided", () => {
    const locator = ChromeLocatorFactory.create();
    expect(locator).toBeDefined();
  });
});

describe("WindowsChromeLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when Chrome is not found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new WindowsChromeLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return the first found path", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new WindowsChromeLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result).toContain("chrome.exe");
  });
});

describe("MacChromeLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when Chrome is not found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new MacChromeLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return the first found path", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new MacChromeLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result).toContain("Google Chrome");
  });
});

describe("LinuxChromeLocator", () => {
  beforeEach(() => {
    vi.mocked(fs.access).mockReset();
  });

  it("should return null when Chrome is not found", async () => {
    vi.mocked(fs.access).mockRejectedValue(new Error("ENOENT"));
    const locator = new LinuxChromeLocator();
    const result = await locator.locate();
    expect(result).toBeNull();
  });

  it("should return the first found path", async () => {
    vi.mocked(fs.access).mockResolvedValueOnce(undefined);
    const locator = new LinuxChromeLocator();
    const result = await locator.locate();
    expect(result).not.toBeNull();
    expect(result).toContain("google-chrome");
  });
});
