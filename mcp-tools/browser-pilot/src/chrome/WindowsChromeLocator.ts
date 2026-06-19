import { access } from "node:fs/promises";
import { constants } from "node:fs";
import type { IChromeLocator } from "../interfaces/index.js";

/**
 * Locates Chrome on Windows by checking common installation paths.
 */
export class WindowsChromeLocator implements IChromeLocator {
  private readonly candidatePaths: string[] = [
    `${process.env["PROGRAMFILES"] ?? "C:\\Program Files"}\\Google\\Chrome\\Application\\chrome.exe`,
    `${process.env["PROGRAMFILES(X86)"] ?? "C:\\Program Files (x86)"}\\Google\\Chrome\\Application\\chrome.exe`,
    `${process.env["LOCALAPPDATA"] ?? ""}\\Google\\Chrome\\Application\\chrome.exe`,
  ];

  public async locate(): Promise<string | null> {
    for (const candidatePath of this.candidatePaths) {
      if (await this.exists(candidatePath)) {
        return candidatePath;
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
