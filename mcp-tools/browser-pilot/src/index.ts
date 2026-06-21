#!/usr/bin/env node

import { ChromeLauncher } from "./chrome/index.js";
import { BrowserManager } from "./browser/index.js";
import { BrowserPilotServer } from "./server/index.js";

/**
 * Entry point for the Browser Pilot MCP server.
 * Instantiates the Chrome launcher, browser manager, and server, then starts.
 */
async function main(): Promise<void> {
  const launcher = new ChromeLauncher();
  const browserManager = BrowserManager.getInstance(launcher);
  const server = new BrowserPilotServer(launcher, browserManager);

  await server.start();
}

main().catch((error: unknown) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
