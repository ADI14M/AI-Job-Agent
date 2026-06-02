import logging
import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)

class PlaywrightEngine:
    """
    Abstract Engine controlling Playwright for Job Automation.
    Includes rules against bypassing CAPTCHA and MFA.
    """
    def __init__(self, headless: bool = False):
        # We run non-headless by default for human approval/CAPTCHA pauses
        self.headless = headless
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def detect_captcha(self, page: Page) -> bool:
        """
        Detect standard CAPTCHA and Cloudflare challenge screens.
        """
        # Very simplified CAPTCHA detection logic
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            "div.g-recaptcha",
            "#cf-challenge-running"
        ]
        
        for selector in captcha_selectors:
            try:
                # small timeout for detection
                element = await page.wait_for_selector(selector, timeout=2000, state="visible")
                if element:
                    logger.warning(f"CAPTCHA detected via selector: {selector}")
                    return True
            except Exception:
                continue
                
        return False

    async def pause_for_human(self, page: Page):
        """
        Pauses the automation loop, waiting for the user to resolve CAPTCHA or MFA manually.
        """
        logger.info("Pausing execution for Human Intervention (CAPTCHA/MFA).")
        # In Playwright, page.pause() opens the inspector and stops execution until resumed
        await page.pause()
        logger.info("Human Intervention complete, resuming automation.")
