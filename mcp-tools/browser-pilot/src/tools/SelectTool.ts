import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Selects an option from a dropdown/select element.
 */
export class SelectTool extends BaseTool {
  public readonly name = "browser_select";
  public readonly description = "Select an option from a dropdown/select element";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector for the select element",
      },
      value: {
        type: "string",
        description: "The value attribute of the option to select",
      },
      label: {
        type: "string",
        description: "The visible text of the option to select (alternative to value)",
      },
    },
    required: ["selector"],
  };

  protected override validate(args: Record<string, unknown>): void {
    super.validate(args);
    if (!args["value"] && !args["label"]) {
      throw new Error("Either 'value' or 'label' must be provided.");
    }
  }

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string;
    const value = args["value"] as string | undefined;
    const label = args["label"] as string | undefined;

    const page = await this.browserManager.getActivePage();

    let selected: string[];
    if (value) {
      selected = await page.selectOption(selector, { value });
    } else {
      selected = await page.selectOption(selector, { label: label! });
    }

    return this.textResult(`Selected option(s): ${selected.join(", ")}`);
  }
}
