import { spawn, type ChildProcess } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";
import type { IChromeLauncher, ChromeLaunchOptions, IBrowserLocator } from "../interfaces/index.js";
import { BrowserLocatorFactory } from "./BrowserLocatorFactory.js";

const DEFAULT_PORT = 9222;
const STARTUP_WAIT_MS = 2000;
const MAX_RETRIES = 10;
const RETRY_DELAY_MS = 500;

/**
 * Manages the Chrome browser process with remote debugging enabled.
 * Handles launching, port detection, and graceful shutdown.
 */
export class ChromeLauncher implements IChromeLauncher {
  private process: ChildProcess | null = null;
  private port: number = DEFAULT_PORT;
  private running: boolean = false;
  private readonly locator: IBrowserLocator;

  public constructor(locator?: IBrowserLocator) {
    this.locator = locator ?? BrowserLocatorFactory.create();
  }

  public async launch(options?: ChromeLaunchOptions): Promise<void> {
    if (this.running) {
      return;
    }

    // Check if Chrome is already running with debugging on this port
    this.port = options?.port ?? DEFAULT_PORT;
    if (await this.isDebugPortActive()) {
      this.running = true;
      return;
    }

    const browserInfo = options?.chromePath
      ? { path: options.chromePath, name: "Custom" }
      : await this.locator.locate();
    if (!browserInfo) {
      throw new Error(
        "No Chromium-based browser found. Please install Chrome, Edge, Brave, or Chromium, or provide a custom path via the 'chromePath' option."
      );
    }

    const args = this.buildLaunchArgs(options);
    this.process = spawn(browserInfo.path, args, {
      detached: true,
      stdio: "ignore",
    });

    this.process.unref();

    this.process.on("exit", () => {
      this.running = false;
      this.process = null;
    });

    // Wait for Chrome to start accepting debug connections
    await this.waitForDebugPort();
    this.running = true;
  }

  public async shutdown(): Promise<void> {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
    this.running = false;
  }

  public async getDebuggerUrl(): Promise<string> {
    const response = await fetch(`http://127.0.0.1:${this.port}/json/version`);
    if (!response.ok) {
      throw new Error(`Failed to get debugger URL: HTTP ${response.status}`);
    }
    const data = await response.json() as { webSocketDebuggerUrl: string };
    return data.webSocketDebuggerUrl;
  }

  public getPort(): number {
    return this.port;
  }

  public isRunning(): boolean {
    return this.running;
  }

  public getProcess(): ChildProcess | null {
    return this.process;
  }

  private buildLaunchArgs(options?: ChromeLaunchOptions): string[] {
    const args: string[] = [
      `--remote-debugging-port=${this.port}`,
      "--no-first-run",
      "--no-default-browser-check",
    ];

    if (options?.headless) {
      args.push("--headless=new");
    }

    if (options?.useExistingProfile === false) {
      const tempDir = join(homedir(), ".browser-pilot", "chrome-profile");
      args.push(`--user-data-dir=${tempDir}`);
    }

    return args;
  }

  private async isDebugPortActive(): Promise<boolean> {
    try {
      const response = await fetch(`http://127.0.0.1:${this.port}/json/version`);
      return response.ok;
    } catch {
      return false;
    }
  }

  private async waitForDebugPort(): Promise<void> {
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      if (await this.isDebugPortActive()) {
        return;
      }
      await this.delay(attempt === 0 ? STARTUP_WAIT_MS : RETRY_DELAY_MS);
    }
    throw new Error(
      `Chrome failed to start debugging on port ${this.port} after ${MAX_RETRIES} retries.`
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
