import { access } from "node:fs/promises";
import { constants } from "node:fs";
import type { IChromeLocator } from "../interfaces/index.js";

/**
 * Locates Chrome on macOS by checking common installation paths.
 */
export class MacChromeLocator implements IChromeLocator {
  private readonly candidatePaths: string[] = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    `${process.env["HOME"] ?? ""}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`,
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
