import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Navigates forward in the browser history.
 */
export class ForwardTool extends BaseTool {
  public readonly name = "browser_forward";
  public readonly description = "Navigate forward in the browser history";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      waitUntil: {
        type: "string",
        description: "When to consider navigation complete",
        enum: ["load", "domcontentloaded", "networkidle", "commit"],
        default: "load",
      },
    },
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const waitUntil = (args["waitUntil"] as "load" | "domcontentloaded" | "networkidle" | "commit") ?? "load";

    const page = await this.browserManager.getActivePage();
    await page.goForward({ waitUntil });

    const url = page.url();
    const title = await page.title();
    return this.textResult(`Navigated forward to: ${url} (title: "${title}")`);
  }
}
