import { access } from "node:fs/promises";
import { constants } from "node:fs";
import type { IBrowserLocator, BrowserInfo } from "../interfaces/index.js";

/**
 * Candidate entry pairing a browser name with its executable path.
 */
interface BrowserCandidate {
  name: string;
  path: string;
}

/**
 * Locates Chromium-based browsers on macOS.
 * Searches in priority order: Chrome > Edge > Brave > Chromium.
 */
export class MacBrowserLocator implements IBrowserLocator {
  private readonly candidates: BrowserCandidate[] = [
    // Chrome
    { name: "Chrome", path: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" },
    { name: "Chrome", path: `${process.env["HOME"] ?? ""}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` },
    // Edge
    { name: "Edge", path: "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" },
    // Brave
    { name: "Brave", path: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" },
    // Chromium
    { name: "Chromium", path: "/Applications/Chromium.app/Contents/MacOS/Chromium" },
  ];

  public async locate(): Promise<BrowserInfo | null> {
    for (const candidate of this.candidates) {
      if (await this.exists(candidate.path)) {
        return { path: candidate.path, name: candidate.name };
      }
    }
    return null;
  }

  private async exists(filePath: string): Promise<boolean> {
    try {
      await access(filePath, constants.X_OK);
      return true;
    } catch {
      return false;
    }
  }
}
