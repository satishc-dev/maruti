import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Navigates the active page to a URL.
 */
export class NavigateTool extends BaseTool {
  public readonly name = "browser_navigate";
  public readonly description = "Navigate the browser to a specified URL";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      url: {
        type: "string",
        description: "The URL to navigate to",
      },
      waitUntil: {
        type: "string",
        description: "When to consider navigation complete",
        enum: ["load", "domcontentloaded", "networkidle", "commit"],
        default: "load",
      },
    },
    required: ["url"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const url = args["url"] as string;
    const waitUntil = (args["waitUntil"] as "load" | "domcontentloaded" | "networkidle" | "commit") ?? "load";

    const page = await this.browserManager.getActivePage();
    const response = await page.goto(url, { waitUntil });

    const status = response?.status() ?? "unknown";
    const title = await page.title();
    return this.textResult(`Navigated to ${url} (status: ${status}, title: "${title}")`);
  }
}
