import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Clicks an element on the page by CSS selector or text content.
 */
export class ClickTool extends BaseTool {
  public readonly name = "browser_click";
  public readonly description = "Click an element on the page by CSS selector or text content";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector or text content to find the element (use 'text=...' for text matching)",
      },
      button: {
        type: "string",
        description: "Mouse button to use",
        enum: ["left", "right", "middle"],
        default: "left",
      },
      clickCount: {
        type: "number",
        description: "Number of clicks (default: 1, use 2 for double-click)",
        default: 1,
      },
    },
    required: ["selector"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string;
    const button = (args["button"] as "left" | "right" | "middle") ?? "left";
    const clickCount = (args["clickCount"] as number) ?? 1;

    const page = await this.browserManager.getActivePage();
    await page.click(selector, { button, clickCount });

    return this.textResult(`Clicked element: ${selector}`);
  }
}
