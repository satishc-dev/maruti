/**
 * Schema definition for an MCP tool's input parameters.
 */
export interface ToolInputSchema {
  type: "object";
  properties: Record<string, {
    type: string;
    description: string;
    enum?: string[];
    default?: unknown;
    items?: { type: string };
  }>;
  required?: string[];
}

/**
 * Result returned from a tool execution.
 */
export interface ToolResult {
  content: Array<{
    type: "text" | "image";
    text?: string;
    data?: string;
    mimeType?: string;
  }>;
  isError?: boolean;
}

/**
 * Interface that all MCP tool implementations must satisfy.
 */
export interface ITool {
  /** The MCP tool name (e.g., "browser_navigate"). */
  readonly name: string;

  /** Human-readable description of what the tool does. */
  readonly description: string;

  /** JSON Schema for the tool's input parameters. */
  readonly inputSchema: ToolInputSchema;

  /**
   * Executes the tool with the given arguments.
   * @param args - The validated input arguments.
   * @returns The tool result containing text or image content.
   */
  execute(args: Record<string, unknown>): Promise<ToolResult>;
}
