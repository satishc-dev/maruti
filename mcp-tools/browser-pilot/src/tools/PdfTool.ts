import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Saves the current page as a PDF file.
 */
export class PdfTool extends BaseTool {
  public readonly name = "browser_pdf";
  public readonly description = "Save the current page as a PDF file";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "File path to save the PDF to",
      },
      format: {
        type: "string",
        description: "Paper format (default: 'Letter')",
        enum: ["Letter", "Legal", "Tabloid", "Ledger", "A0", "A1", "A2", "A3", "A4", "A5", "A6"],
        default: "Letter",
      },
      landscape: {
        type: "boolean",
        description: "Whether to use landscape orientation (default: false)",
        default: false,
      },
    },
    required: ["path"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const filePath = args["path"] as string;
    const format = (args["format"] as string) ?? "Letter";
    const landscape = (args["landscape"] as boolean) ?? false;

    const page = await this.browserManager.getActivePage();
    await page.pdf({ path: filePath, format, landscape });

    return this.textResult(`PDF saved to: ${filePath}`);
  }
}
