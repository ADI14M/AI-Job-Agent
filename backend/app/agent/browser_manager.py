from playwright.sync_api import sync_playwright
import os
from app.core.logger import system_logger

class BrowserManager:
    """
    Singleton wrapper for Playwright to ensure we don't spawn infinite browser instances.
    Supports Chromium by default, extensible to Firefox/WebKit.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
            cls._instance.playwright = None
            cls._instance.browser = None
        return cls._instance

    def start(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
            # Launch in headless mode for server execution, headful for debugging if needed
            self.browser = self.playwright.chromium.launch(headless=True)
            system_logger.info("Playwright Chromium browser started.")

    def new_context(self, storage_state_path: str = None):
        if not self.browser:
            self.start()
        
        context_args = {}
        if storage_state_path and os.path.exists(storage_state_path):
            context_args['storage_state'] = storage_state_path
            
        return self.browser.new_context(**context_args)

    def close(self):
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
        system_logger.info("Playwright browser closed.")

browser_manager = BrowserManager()
