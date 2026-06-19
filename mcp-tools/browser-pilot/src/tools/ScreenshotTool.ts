import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Captures a screenshot of the page or a specific element.
 */
export class ScreenshotTool extends BaseTool {
  public readonly name = "browser_screenshot";
  public readonly description = "Capture a screenshot of the page or a specific element";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector for a specific element to screenshot (optional, defaults to full page)",
      },
      fullPage: {
        type: "boolean",
        description: "Whether to capture the full scrollable page (default: false)",
        default: false,
      },
    },
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string | undefined;
    const fullPage = (args["fullPage"] as boolean) ?? false;

    const page = await this.browserManager.getActivePage();
    let buffer: Buffer;

    if (selector) {
      const element = await page.locator(selector).first();
      buffer = await element.screenshot();
    } else {
      buffer = await page.screenshot({ fullPage });
    }

    const base64 = buffer.toString("base64");
    return this.imageResult(base64, "image/png");
  }
}
