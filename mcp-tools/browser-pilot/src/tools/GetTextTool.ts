import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Gets text content from the page or a specific element.
 */
export class GetTextTool extends BaseTool {
  public readonly name = "browser_get_text";
  public readonly description = "Get the text content of the page or a specific element";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector for a specific element (optional, defaults to body)",
      },
    },
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = (args["selector"] as string) ?? "body";

    const page = await this.browserManager.getActivePage();
    const text = await page.locator(selector).first().innerText();

    return this.textResult(text);
  }
}
