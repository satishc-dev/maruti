import { chromium, type Browser, type BrowserContext, type Page } from "playwright-core";
import type { IBrowserManager } from "../interfaces/index.js";
import type { IChromeLauncher } from "../interfaces/index.js";

/**
 * Singleton manager for the Playwright browser connection.
 * Connects to Chrome via CDP and manages page/tab lifecycle.
 */
export class BrowserManager implements IBrowserManager {
  private static instance: BrowserManager | null = null;

  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private activePageIndex: number = 0;
  private connected: boolean = false;
  private readonly launcher: IChromeLauncher;

  public constructor(launcher: IChromeLauncher) {
    this.launcher = launcher;
  }

  /**
   * Gets or creates the singleton instance.
   */
  public static getInstance(launcher: IChromeLauncher): BrowserManager {
    if (!BrowserManager.instance) {
      BrowserManager.instance = new BrowserManager(launcher);
    }
    return BrowserManager.instance;
  }

  /**
   * Resets the singleton (primarily for testing).
   */
  public static resetInstance(): void {
    BrowserManager.instance = null;
  }

  public async ensureConnected(): Promise<void> {
    if (this.connected && this.browser?.isConnected()) {
      return;
    }

    // Ensure Chrome is running
    if (!this.launcher.isRunning()) {
      await this.launcher.launch();
    }

    const wsUrl = await this.launcher.getDebuggerUrl();
    this.browser = await chromium.connectOverCDP(wsUrl);
    this.connected = true;

    // Get existing context or create one
    const contexts = this.browser.contexts();
    this.context = contexts.length > 0 ? contexts[0]! : await this.browser.newContext();

    // Listen for disconnection
    this.browser.on("disconnected", () => {
      this.connected = false;
      this.browser = null;
      this.context = null;
    });
  }

  public async getActivePage(): Promise<Page> {
    await this.ensureConnected();

    const pages = this.context!.pages();
    if (pages.length === 0) {
      const newPage = await this.context!.newPage();
      this.activePageIndex = 0;
      return newPage;
    }

    // Clamp index to valid range
    if (this.activePageIndex >= pages.length) {
      this.activePageIndex = pages.length - 1;
    }

    return pages[this.activePageIndex]!;
  }

  public async getPageByIndex(index: number): Promise<Page> {
    await this.ensureConnected();

    const pages = this.context!.pages();
    if (index < 0 || index >= pages.length) {
      throw new Error(`Invalid page index: ${index}. Available pages: 0-${pages.length - 1}`);
    }

    return pages[index]!;
  }

  public async getPages(): Promise<Page[]> {
    await this.ensureConnected();
    return this.context!.pages();
  }

  public async switchToPage(index: number): Promise<Page> {
    const page = await this.getPageByIndex(index);
    this.activePageIndex = index;
    return page;
  }

  public async createNewPage(): Promise<Page> {
    await this.ensureConnected();
    const page = await this.context!.newPage();
    const pages = this.context!.pages();
    this.activePageIndex = pages.length - 1;
    return page;
  }

  public async closePage(index?: number): Promise<void> {
    await this.ensureConnected();

    const pages = this.context!.pages();
    const targetIndex = index ?? this.activePageIndex;

    if (targetIndex < 0 || targetIndex >= pages.length) {
      throw new Error(`Invalid page index: ${targetIndex}. Available pages: 0-${pages.length - 1}`);
    }

    await pages[targetIndex]!.close();

    // Adjust active page index
    const remainingPages = this.context!.pages();
    if (remainingPages.length === 0) {
      await this.disconnect();
    } else if (this.activePageIndex >= remainingPages.length) {
      this.activePageIndex = remainingPages.length - 1;
    }
  }

  public getBrowser(): Browser | null {
    return this.browser;
  }

  public getContext(): BrowserContext | null {
    return this.context;
  }

  public async disconnect(): Promise<void> {
    if (this.browser) {
      await this.browser.close();
    }
    this.browser = null;
    this.context = null;
    this.connected = false;
    this.activePageIndex = 0;
  }

  public isConnected(): boolean {
    return this.connected && (this.browser?.isConnected() ?? false);
  }
}
