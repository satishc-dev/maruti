import type { IBrowserManager } from "../interfaces/index.js";
import type { ITool, ToolInputSchema, ToolResult } from "../interfaces/index.js";

/**
 * Abstract base class for all MCP tool implementations.
 * Uses the Template Method pattern: execute() defines the workflow,
 * subclasses override runImpl() with their specific logic.
 */
export abstract class BaseTool implements ITool {
  public abstract readonly name: string;
  public abstract readonly description: string;
  public abstract readonly inputSchema: ToolInputSchema;

  protected readonly browserManager: IBrowserManager;

  protected constructor(browserManager: IBrowserManager) {
    this.browserManager = browserManager;
  }

  /**
   * Template method that defines the execution workflow:
   * 1. Validate arguments
   * 2. Ensure browser is connected
   * 3. Run the tool-specific logic
   * 4. Format the result
   */
  public async execute(args: Record<string, unknown>): Promise<ToolResult> {
    try {
      this.validate(args);
      await this.browserManager.ensureConnected();
      return await this.runImpl(args);
    } catch (error: unknown) {
      return this.formatError(error);
    }
  }

  /**
   * Subclasses implement their specific tool logic here.
   */
  protected abstract runImpl(args: Record<string, unknown>): Promise<ToolResult>;

  /**
   * Validates that required arguments are present.
   * Subclasses can override for custom validation.
   */
  protected validate(args: Record<string, unknown>): void {
    const required = this.inputSchema.required ?? [];
    for (const field of required) {
      if (args[field] === undefined || args[field] === null) {
        throw new Error(`Missing required argument: '${field}'`);
      }
    }
  }

  /**
   * Creates a successful text result.
   */
  protected textResult(text: string): ToolResult {
    return {
      content: [{ type: "text", text }],
    };
  }

  /**
   * Creates an image result (base64-encoded).
   */
  protected imageResult(data: string, mimeType: string = "image/png"): ToolResult {
    return {
      content: [{ type: "image", data, mimeType }],
    };
  }

  /**
   * Formats an error into a ToolResult.
   */
  private formatError(error: unknown): ToolResult {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${message}` }],
      isError: true,
    };
  }
}
