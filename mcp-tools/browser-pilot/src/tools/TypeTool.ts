import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Types text into an input element on the page.
 */
export class TypeTool extends BaseTool {
  public readonly name = "browser_type";
  public readonly description = "Type text into an input element on the page";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector for the input element",
      },
      text: {
        type: "string",
        description: "Text to type",
      },
      delay: {
        type: "number",
        description: "Delay between key presses in milliseconds (default: 0)",
        default: 0,
      },
      clear: {
        type: "boolean",
        description: "Whether to clear the input before typing (default: false)",
        default: false,
      },
    },
    required: ["selector", "text"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string;
    const text = args["text"] as string;
    const delay = (args["delay"] as number) ?? 0;
    const clear = (args["clear"] as boolean) ?? false;

    const page = await this.browserManager.getActivePage();

    if (clear) {
      await page.fill(selector, "");
    }

    await page.type(selector, text, { delay });
    return this.textResult(`Typed "${text}" into ${selector}`);
  }
}
