import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Switches the active tab to a different one by index.
 */
export class SwitchTabTool extends BaseTool {
  public readonly name = "browser_switch_tab";
  public readonly description = "Switch the active browser tab to one at a specified index";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      index: {
        type: "number",
        description: "The index of the tab to switch to (use browser_tabs to see available indices)",
      },
    },
    required: ["index"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const index = args["index"] as number;

    const page = await this.browserManager.switchToPage(index);
    const title = await page.title();
    const url = page.url();

    return this.textResult(`Switched to tab [${index}]: ${title || "(untitled)"} - ${url}`);
  }
}
