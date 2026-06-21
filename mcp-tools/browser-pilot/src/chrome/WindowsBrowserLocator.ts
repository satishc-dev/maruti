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
 * Locates Chromium-based browsers on Windows.
 * Searches in priority order: Chrome > Edge > Brave.
 */
export class WindowsBrowserLocator implements IBrowserLocator {
  private readonly candidates: BrowserCandidate[] = [
    // Chrome
    { name: "Chrome", path: `${process.env["PROGRAMFILES"] ?? "C:\\Program Files"}\\Google\\Chrome\\Application\\chrome.exe` },
    { name: "Chrome", path: `${process.env["PROGRAMFILES(X86)"] ?? "C:\\Program Files (x86)"}\\Google\\Chrome\\Application\\chrome.exe` },
    { name: "Chrome", path: `${process.env["LOCALAPPDATA"] ?? ""}\\Google\\Chrome\\Application\\chrome.exe` },
    // Edge
    { name: "Edge", path: `${process.env["PROGRAMFILES(X86)"] ?? "C:\\Program Files (x86)"}\\Microsoft\\Edge\\Application\\msedge.exe` },
    { name: "Edge", path: `${process.env["PROGRAMFILES"] ?? "C:\\Program Files"}\\Microsoft\\Edge\\Application\\msedge.exe` },
    // Brave
    { name: "Brave", path: `${process.env["PROGRAMFILES"] ?? "C:\\Program Files"}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe` },
    { name: "Brave", path: `${process.env["LOCALAPPDATA"] ?? ""}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe` },
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
