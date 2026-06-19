import type { ITool } from "../interfaces/index.js";

/**
 * Registry that maps tool names to their implementations.
 * Used by the MCP server to look up tools by name.
 */
export class ToolRegistry {
  private readonly tools: Map<string, ITool> = new Map();

  /**
   * Registers a tool instance.
   */
  public register(tool: ITool): void {
    if (this.tools.has(tool.name)) {
      throw new Error(`Tool '${tool.name}' is already registered.`);
    }
    this.tools.set(tool.name, tool);
  }

  /**
   * Registers multiple tools at once.
   */
  public registerAll(tools: ITool[]): void {
    for (const tool of tools) {
      this.register(tool);
    }
  }

  /**
   * Retrieves a tool by name.
   */
  public get(name: string): ITool | undefined {
    return this.tools.get(name);
  }

  /**
   * Returns all registered tools.
   */
  public getAll(): ITool[] {
    return Array.from(this.tools.values());
  }

  /**
   * Returns the number of registered tools.
   */
  public get size(): number {
    return this.tools.size;
  }
}
