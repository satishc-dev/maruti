import type { IBrowserManager, ToolInputSchema, ToolResult } from "../interfaces/index.js";
import { BaseTool } from "./BaseTool.js";

/**
 * Manages browser cookies: get, set, or delete.
 */
export class CookiesTool extends BaseTool {
  public readonly name = "browser_cookies";
  public readonly description = "Get, set, or delete browser cookies";
  public readonly inputSchema: ToolInputSchema = {
    type: "object",
    properties: {
      action: {
        type: "string",
        description: "The cookie operation to perform",
        enum: ["get", "set", "delete", "clear"],
      },
      name: {
        type: "string",
        description: "Cookie name (required for set and delete)",
      },
      value: {
        type: "string",
        description: "Cookie value (required for set)",
      },
      domain: {
        type: "string",
        description: "Cookie domain (required for set)",
      },
      path: {
        type: "string",
        description: "Cookie path (default: '/')",
        default: "/",
      },
      url: {
        type: "string",
        description: "URL to filter cookies by (for get action)",
      },
    },
    required: ["action"],
  };

  public constructor(browserManager: IBrowserManager) {
    super(browserManager);
  }

  protected async runImpl(args: Record<string, unknown>): Promise<ToolResult> {
    const action = args["action"] as string;
    const context = this.browserManager.getContext();

    if (!context) {
      throw new Error("No browser context available.");
    }

    switch (action) {
      case "get":
        return await this.getCookies(args);
      case "set":
        return await this.setCookie(args);
      case "delete":
        return await this.deleteCookie(args);
      case "clear":
        return await this.clearCookies();
      default:
        throw new Error(`Unknown cookie action: ${action}`);
    }
  }

  private async getCookies(args: Record<string, unknown>): Promise<ToolResult> {
    const context = this.browserManager.getContext()!;
    const url = args["url"] as string | undefined;

    const cookies = url
      ? await context.cookies(url)
      : await context.cookies();

    return this.textResult(JSON.stringify(cookies, null, 2));
  }

  private async setCookie(args: Record<string, unknown>): Promise<ToolResult> {
    const context = this.browserManager.getContext()!;
    const name = args["name"] as string;
    const value = args["value"] as string;
    const domain = args["domain"] as string;
    const path = (args["path"] as string) ?? "/";

    if (!name || !value || !domain) {
      throw new Error("Cookie 'name', 'value', and 'domain' are required for set action.");
    }

    await context.addCookies([{ name, value, domain, path }]);
    return this.textResult(`Cookie '${name}' set for domain '${domain}'`);
  }

  private async deleteCookie(args: Record<string, unknown>): Promise<ToolResult> {
    const context = this.browserManager.getContext()!;
    const name = args["name"] as string;

    if (!name) {
      throw new Error("Cookie 'name' is required for delete action.");
    }

    // Playwright doesn't have a direct delete API — clear and re-add all except target
    const allCookies = await context.cookies();
    await context.clearCookies();
    const remaining = allCookies.filter((c) => c.name !== name);
    if (remaining.length > 0) {
      await context.addCookies(remaining);
    }

    return this.textResult(`Cookie '${name}' deleted`);
  }

  private async clearCookies(): Promise<ToolResult> {
    const context = this.browserManager.getContext()!;
    await context.clearCookies();
    return this.textResult("All cookies cleared");
  }
}
