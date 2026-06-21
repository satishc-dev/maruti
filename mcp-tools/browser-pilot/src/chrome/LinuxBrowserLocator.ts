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
 * Locates Chromium-based browsers on Linux.
 * Searches in priority order: Chrome > Edge > Brave > Chromium.
 */
export class LinuxBrowserLocator implements IBrowserLocator {
  private readonly candidates: BrowserCandidate[] = [
    // Chrome
    { name: "Chrome", path: "/usr/bin/google-chrome" },
    { name: "Chrome", path: "/usr/bin/google-chrome-stable" },
    // Edge
    { name: "Edge", path: "/usr/bin/microsoft-edge" },
    { name: "Edge", path: "/usr/bin/microsoft-edge-stable" },
    // Brave
    { name: "Brave", path: "/usr/bin/brave-browser" },
    // Chromium
    { name: "Chromium", path: "/usr/bin/chromium-browser" },
    { name: "Chromium", path: "/usr/bin/chromium" },
    { name: "Chromium", path: "/snap/bin/chromium" },
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
