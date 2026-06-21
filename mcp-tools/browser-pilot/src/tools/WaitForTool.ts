import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Waits for a selector, navigation, or network idle.
 */
export class WaitForTool extends BaseTool {
  public readonly name = "browser_wait_for";
  public readonly description = "Wait for a selector to appear, navigation to complete, or network to become idle";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector to wait for (mutually exclusive with 'event')",
      },
      event: {
        type: "string",
        description: "Event to wait for (mutually exclusive with 'selector')",
        enum: ["load", "domcontentloaded", "networkidle"],
      },
      timeout: {
        type: "number",
        description: "Maximum wait time in milliseconds (default: 30000)",
        default: 30000,
      },
      state: {
        type: "string",
        description: "State to wait for when using selector (default: 'visible')",
        enum: ["attached", "detached", "visible", "hidden"],
        default: "visible",
      },
    },
  };

  protected override validate(args: Record<string, unknown>): void {
    if (!args["selector"] && !args["event"]) {
      throw new Error("Either 'selector' or 'event' must be provided.");
    }
  }

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string | undefined;
    const event = args["event"] as string | undefined;
    const timeout = (args["timeout"] as number) ?? 30000;
    const state = (args["state"] as "attached" | "detached" | "visible" | "hidden") ?? "visible";

    const page = await this.browserManager.getActivePage();

    if (selector) {
      await page.locator(selector).first().waitFor({ state, timeout });
      return this.textResult(`Element '${selector}' is now ${state}`);
    }

    // event must be defined since validate() ensures selector or event exists
    await page.waitForLoadState(event as "load" | "domcontentloaded" | "networkidle", { timeout });
    return this.textResult(`Page reached '${event}' state`);
  }
}
