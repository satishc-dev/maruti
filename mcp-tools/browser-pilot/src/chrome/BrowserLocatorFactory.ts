import type { IBrowserLocator } from "../interfaces/index.js";
import { WindowsBrowserLocator } from "./WindowsBrowserLocator.js";
import { MacBrowserLocator } from "./MacBrowserLocator.js";
import { LinuxBrowserLocator } from "./LinuxBrowserLocator.js";

/**
 * Factory that produces the appropriate IBrowserLocator for the current platform.
 */
export class BrowserLocatorFactory {
  /**
   * Creates a platform-specific browser locator based on process.platform.
   */
  public static create(platform?: NodeJS.Platform): IBrowserLocator {
    const currentPlatform = platform ?? process.platform;

    switch (currentPlatform) {
      case "win32":
        return new WindowsBrowserLocator();
      case "darwin":
        return new MacBrowserLocator();
      case "linux":
        return new LinuxBrowserLocator();
      default:
        throw new Error(`Unsupported platform: ${currentPlatform}. Browser auto-detection supports Windows, macOS, and Linux.`);
    }
  }
}
