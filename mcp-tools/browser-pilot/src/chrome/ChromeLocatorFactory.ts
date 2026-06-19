import type { IChromeLocator } from "../interfaces/index.js";
import { WindowsChromeLocator } from "./WindowsChromeLocator.js";
import { MacChromeLocator } from "./MacChromeLocator.js";
import { LinuxChromeLocator } from "./LinuxChromeLocator.js";

/**
 * Factory that produces the appropriate IChromeLocator for the current platform.
 */
export class ChromeLocatorFactory {
  /**
   * Creates a platform-specific Chrome locator based on process.platform.
   */
  public static create(platform?: NodeJS.Platform): IChromeLocator {
    const currentPlatform = platform ?? process.platform;

    switch (currentPlatform) {
      case "win32":
        return new WindowsChromeLocator();
      case "darwin":
        return new MacChromeLocator();
      case "linux":
        return new LinuxChromeLocator();
      default:
        throw new Error(`Unsupported platform: ${currentPlatform}. Chrome auto-detection supports Windows, macOS, and Linux.`);
    }
  }
}
