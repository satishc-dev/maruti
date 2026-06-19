import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import type { IBrowserManager } from "../interfaces/index.js";
import type { IChromeLauncher } from "../interfaces/index.js";
import {
  ToolRegistry,
  NavigateTool,
  ClickTool,
  TypeTool,
  ScreenshotTool,
  GetTextTool,
  ScrollTool,
  WaitForTool,
  EvaluateTool,
  SelectTool,
  UploadTool,
  CookiesTool,
  PdfTool,
  BackTool,
  ForwardTool,
  CloseTool,
  TabsTool,
  SwitchTabTool,
} from "../tools/index.js";

/**
 * The main MCP server class that wires together Chrome launcher,
 * browser manager, and all tool implementations.
 */
export class BrowserPilotServer {
  private readonly server: Server;
  private readonly toolRegistry: ToolRegistry;
  private readonly browserManager: IBrowserManager;
  private readonly chromeLauncher: IChromeLauncher;

  public constructor(chromeLauncher: IChromeLauncher, browserManager: IBrowserManager) {
    this.chromeLauncher = chromeLauncher;
    this.browserManager = browserManager;
    this.toolRegistry = new ToolRegistry();
    this.server = new Server(
      { name: "browser-pilot", version: "1.0.0" },
      { capabilities: { tools: {} } }
    );

    this.registerTools();
    this.setupHandlers();
  }

  /**
   * Starts the MCP server using stdio transport.
   */
  public async start(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    // Graceful shutdown
    process.on("SIGINT", () => this.shutdown());
    process.on("SIGTERM", () => this.shutdown());
  }

  /**
   * Shuts down the server and cleans up resources.
   */
  public async shutdown(): Promise<void> {
    await this.browserManager.disconnect();
    await this.chromeLauncher.shutdown();
    await this.server.close();
  }

  /**
   * Returns the tool registry (for testing).
   */
  public getToolRegistry(): ToolRegistry {
    return this.toolRegistry;
  }

  private registerTools(): void {
    this.toolRegistry.registerAll([
      new NavigateTool(this.browserManager),
      new ClickTool(this.browserManager),
      new TypeTool(this.browserManager),
      new ScreenshotTool(this.browserManager),
      new GetTextTool(this.browserManager),
      new ScrollTool(this.browserManager),
      new WaitForTool(this.browserManager),
      new EvaluateTool(this.browserManager),
      new SelectTool(this.browserManager),
      new UploadTool(this.browserManager),
      new CookiesTool(this.browserManager),
      new PdfTool(this.browserManager),
      new BackTool(this.browserManager),
      new ForwardTool(this.browserManager),
      new CloseTool(this.browserManager),
      new TabsTool(this.browserManager),
      new SwitchTabTool(this.browserManager),
    ]);
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = this.toolRegistry.getAll().map((tool) => ({
        name: tool.name,
        description: tool.description,
        inputSchema: tool.inputSchema,
      }));
      return { tools };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const toolName = request.params.name;
      const args = (request.params.arguments ?? {}) as Record<string, unknown>;

      const tool = this.toolRegistry.get(toolName);
      if (!tool) {
        return {
          content: [{ type: "text" as const, text: `Unknown tool: ${toolName}` }],
          isError: true,
        };
      }

      const result = await tool.execute(args);
      return {
        content: result.content.map((c) => {
          if (c.type === "image") {
            return { type: "image" as const, data: c.data ?? "", mimeType: c.mimeType ?? "image/png" };
          }
          return { type: "text" as const, text: c.text ?? "" };
        }),
        isError: result.isError,
      };
    });
  }
}
