import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Executes JavaScript in the page context and returns the result.
 */
export class EvaluateTool extends BaseTool {
  public readonly name = "browser_evaluate";
  public readonly description = "Execute JavaScript code in the page context and return the result";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      script: {
        type: "string",
        description: "JavaScript code to execute in the page context",
      },
    },
    required: ["script"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const script = args["script"] as string;

    const page = await this.browserManager.getActivePage();
    const result = await page.evaluate(script);

    const output = result === undefined ? "undefined" : JSON.stringify(result, null, 2);
    return this.textResult(output);
  }
}
