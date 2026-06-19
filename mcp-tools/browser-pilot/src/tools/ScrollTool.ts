import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Scrolls the page or a specific element.
 */
export class ScrollTool extends BaseTool {
  public readonly name = "browser_scroll";
  public readonly description = "Scroll the page or a specific element";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      direction: {
        type: "string",
        description: "Scroll direction",
        enum: ["up", "down", "left", "right"],
        default: "down",
      },
      amount: {
        type: "number",
        description: "Scroll amount in pixels (default: 500)",
        default: 500,
      },
      selector: {
        type: "string",
        description: "CSS selector for a specific element to scroll (optional, defaults to page)",
      },
    },
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const direction = (args["direction"] as string) ?? "down";
    const amount = (args["amount"] as number) ?? 500;
    const selector = args["selector"] as string | undefined;

    const page = await this.browserManager.getActivePage();

    let deltaX = 0;
    let deltaY = 0;

    switch (direction) {
      case "up": deltaY = -amount; break;
      case "down": deltaY = amount; break;
      case "left": deltaX = -amount; break;
      case "right": deltaX = amount; break;
    }

    if (selector) {
      await page.locator(selector).first().evaluate(
        (el, { dx, dy }) => { el.scrollBy(dx, dy); },
        { dx: deltaX, dy: deltaY }
      );
    } else {
      await page.mouse.wheel(deltaX, deltaY);
    }

    return this.textResult(`Scrolled ${direction} by ${amount}px`);
  }
}
