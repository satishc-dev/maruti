/**
 * Interface for platform-specific Chrome executable discovery.
 */
export interface IChromeLocator {
  /**
   * Returns the file path to the Chrome executable on this platform,
   * or null if Chrome is not found.
   */
  locate(): Promise<string | null>;
}
