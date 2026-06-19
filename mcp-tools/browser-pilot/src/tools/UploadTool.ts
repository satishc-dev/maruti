import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Uploads a file to a file input element.
 */
export class UploadTool extends BaseTool {
  public readonly name = "browser_upload";
  public readonly description = "Upload a file to a file input element";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      selector: {
        type: "string",
        description: "CSS selector for the file input element",
      },
      filePaths: {
        type: "array",
        description: "Array of absolute file paths to upload",
        items: { type: "string" },
      },
    },
    required: ["selector", "filePaths"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const selector = args["selector"] as string;
    const filePaths = args["filePaths"] as string[];

    const page = await this.browserManager.getActivePage();
    await page.setInputFiles(selector, filePaths);

    return this.textResult(`Uploaded ${filePaths.length} file(s) to ${selector}`);
  }
}
