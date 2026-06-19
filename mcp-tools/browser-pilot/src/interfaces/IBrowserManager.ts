import type { Page, Browser, BrowserContext } from "playwright-core";

/**
 * Interface for managing the Playwright browser connection and pages.
 */
export interface IBrowserManager {
  /** Ensures a browser connection is established (lazy initialization). */
  ensureConnected(): Promise<void>;

  /** Returns the active page, creating one if necessary. */
  getActivePage(): Promise<Page>;

  /** Returns a specific page by index. */
  getPageByIndex(index: number): Promise<Page>;

  /** Returns all open pages. */
  getPages(): Promise<Page[]>;

  /** Switches the active page to the one at the given index. */
  switchToPage(index: number): Promise<Page>;

  /** Creates a new page/tab and sets it as active. */
  createNewPage(): Promise<Page>;

  /** Closes a page by index. If it's the last page, closes the browser. */
  closePage(index?: number): Promise<void>;

  /** Returns the underlying Playwright Browser instance. */
  getBrowser(): Browser | null;

  /** Returns the browser context. */
  getContext(): BrowserContext | null;

  /** Gracefully disconnects from the browser. */
  disconnect(): Promise<void>;

  /** Returns whether the manager is connected to a browser. */
  isConnected(): boolean;
}
