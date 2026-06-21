import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Closes the browser or a specific tab.
 */
export class CloseTool extends BaseTool {
  public readonly name = "browser_close";
  public readonly description = "Close the browser or a specific tab";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      tabIndex: {
        type: "number",
        description: "Index of the tab to close (optional, closes active tab if not specified)",
      },
      all: {
        type: "boolean",
        description: "Whether to close all tabs and disconnect (default: false)",
        default: false,
      },
    },
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const tabIndex = args["tabIndex"] as number | undefined;
    const all = (args["all"] as boolean) ?? false;

    if (all) {
      await this.browserManager.disconnect();
      return this.textResult("Browser disconnected and all tabs closed");
    }

    await this.browserManager.closePage(tabIndex);
    return this.textResult(`Tab ${tabIndex ?? "active"} closed`);
  }
}
