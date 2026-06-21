import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Lists all open browser tabs with their URLs and titles.
 */
export class TabsTool extends BaseTool {
  public readonly name = "browser_tabs";
  public readonly description = "List all open browser tabs with their URLs and titles";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {},
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(_args: Record<string, unknown>): Promise<ToolResult> {
    const pages = await this.browserManager.getPages();

    const tabInfo = await Promise.all(
      pages.map(async (page, index) => {
        const title = await page.title();
        const url = page.url();
        return `[${index}] ${title || "(untitled)"} - ${url}`;
      })
    );

    return this.textResult(tabInfo.join("\n"));
  }
}
