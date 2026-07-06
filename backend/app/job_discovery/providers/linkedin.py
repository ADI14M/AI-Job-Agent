import os
import urllib.parse
from typing import List
from playwright.sync_api import sync_playwright
from app.job_discovery.base_provider import BaseJobProvider
from app.job_discovery.provider_registry import ProviderRegistry
from app.job_discovery.models import DiscoveredJob
from app.core.logger import system_logger
from datetime import datetime

class LinkedInProvider(BaseJobProvider):
    @property
    def provider_name(self) -> str:
        return "LinkedIn"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        api_key = os.getenv("LINKEDIN_RAPID_API_KEY")
        if api_key:
            system_logger.info("Using RapidAPI for LinkedIn")
            # Implement RapidAPI here if needed
            return []
            
        system_logger.info("Using Playwright headful mode for LinkedIn scraping...")
        jobs = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                # Format URL
                url_query = urllib.parse.quote(query)
                url_loc = urllib.parse.quote(location)
                url = f"https://www.linkedin.com/jobs/search/?keywords={url_query}&location={url_loc}"
                
                page.goto(url, timeout=60000)
                
                # Wait for job cards to load (public search page has different selectors than logged-in)
                page.wait_for_selector("ul.jobs-search__results-list li", timeout=15000)
                
                # Get job cards
                cards = page.locator("ul.jobs-search__results-list li").all()
                for card in cards:
                    if len(jobs) >= limit:
                        break
                        
                    try:
                        title_el = card.locator("h3.base-search-card__title")
                        company_el = card.locator("h4.base-search-card__subtitle")
                        location_el = card.locator("span.job-search-card__location")
                        url_el = card.locator("a.base-card__full-link")
                        
                        if title_el.count() == 0:
                            continue
                            
                        title = title_el.inner_text().strip()
                        company = company_el.inner_text().strip() if company_el.count() > 0 else "Unknown"
                        job_location = location_el.inner_text().strip() if location_el.count() > 0 else "Unknown"
                        job_url = url_el.get_attribute("href") if url_el.count() > 0 else ""
                        
                        jobs.append(DiscoveredJob(
                            title=title,
                            company=company,
                            location=job_location,
                            employment_type="Full-time",
                            salary="Unknown",
                            experience="Unknown",
                            description="Extracted via Playwright", # Need to click to get full description, keeping it simple for now to avoid bot detection
                            skills=[],
                            url=job_url,
                            source="LinkedIn",
                            posted_date=datetime.utcnow().isoformat(),
                            company_logo=None,
                            remote="remote" in job_location.lower()
                        ))
                    except Exception as e:
                        system_logger.warning(f"Error parsing LinkedIn job card: {e}")
                
                browser.close()
        except Exception as e:
            system_logger.error(f"Playwright LinkedIn scraping failed: {e}")
            raise Exception(f"Playwright LinkedIn scraping failed: {e}")
            
        return jobs

ProviderRegistry.register(LinkedInProvider())
