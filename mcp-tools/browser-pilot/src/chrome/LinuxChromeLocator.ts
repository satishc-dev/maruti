import { access } from "node:fs/promises";
import { constants } from "node:fs";
import type { IChromeLocator } from "../interfaces/index.js";

/**
 * Locates Chrome on Linux by checking common installation paths.
 */
export class LinuxChromeLocator implements IChromeLocator {
  private readonly candidatePaths: string[] = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/snap/bin/chromium",
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
