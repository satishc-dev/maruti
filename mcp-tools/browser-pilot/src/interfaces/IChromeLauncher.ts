import type { ChildProcess } from "node:child_process";

/**
 * Configuration options for launching Chrome.
 */
export interface ChromeLaunchOptions {
  /** Port for remote debugging (default: 9222). */
  port?: number;
  /** Whether to use the existing user profile (default: true). */
  useExistingProfile?: boolean;
  /** Custom path to Chrome executable (overrides auto-detection). */
  chromePath?: string;
  /** Whether to launch in headless mode (default: false — headed). */
  headless?: boolean;
}

/**
 * Interface for Chrome process lifecycle management.
 */
export interface IChromeLauncher {
  /**
   * Launches Chrome with remote debugging enabled.
   * If Chrome is already running with debugging on the target port, returns without re-launching.
   */
  launch(options?: ChromeLaunchOptions): Promise<void>;

  /** Terminates the managed Chrome process. */
  shutdown(): Promise<void>;

  /** Returns the WebSocket debugger URL for CDP connection. */
  getDebuggerUrl(): Promise<string>;

  /** Returns the debugging port. */
  getPort(): number;

  /** Returns whether Chrome is currently running. */
  isRunning(): boolean;

  /** Returns the underlying child process, or null if not launched by us. */
  getProcess(): ChildProcess | null;
}
