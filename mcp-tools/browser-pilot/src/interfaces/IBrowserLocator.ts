/**
 * Information about a discovered Chromium-based browser.
 */
export interface BrowserInfo {
  /** Absolute path to the browser executable. */
  path: string;
  /** Human-readable browser name (e.g., "Chrome", "Edge", "Brave", "Chromium"). */
  name: string;
}

/**
 * Interface for platform-specific Chromium browser discovery.
 * Implementations search for any Chromium-based browser in priority order.
 */
export interface IBrowserLocator {
  /**
   * Returns info about the first available Chromium-based browser,
   * or null if none is found.
   */
  locate(): Promise<BrowserInfo | null>;
}
