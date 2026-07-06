import urllib.parse
from typing import List
from playwright.sync_api import sync_playwright
from app.job_discovery.base_provider import BaseJobProvider
from app.job_discovery.provider_registry import ProviderRegistry
from app.job_discovery.models import DiscoveredJob
from app.core.logger import system_logger
from datetime import datetime

class WellfoundProvider(BaseJobProvider):
    @property
    def provider_name(self) -> str:
        return "Wellfound"

    def search_jobs(self, query: str, location: str, limit: int, **kwargs) -> List[DiscoveredJob]:
        system_logger.info("Using Playwright headless mode for Wellfound scraping...")
        jobs = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                # Format URL (Wellfound search requires specific role slugs, but for basic search we can use generic roles url or keyword)
                url_query = urllib.parse.quote(query.replace(" ", "-").lower())
                url = f"https://wellfound.com/role/l/{url_query}"
                
                page.goto(url, timeout=30000)
                
                # Wait for job listings (sometimes protected by Cloudflare or requires login to see details)
                try:
                    page.wait_for_selector(".styles_component__26K3j", timeout=10000) # common wellfound listing class
                except:
                    system_logger.warning("Could not find common Wellfound job listings. Attempting fallback selectors...")
                
                # Since Wellfound changes classes frequently and blocks headless aggressively, 
                # we'll try a generic anchor tag extraction if the specific class fails.
                
                job_links = page.locator("a[href*='/jobs/']").all()
                processed_urls = set()
                
                for link in job_links:
                    if len(jobs) >= limit:
                        break
                        
                    try:
                        href = link.get_attribute("href")
                        if not href or href in processed_urls or "wellfound.com/jobs/" not in href:
                            continue
                            
                        processed_urls.add(href)
                        title = link.inner_text().strip()
                        if not title:
                            continue
                        
                        jobs.append(DiscoveredJob(
                            title=title,
                            company="Wellfound Startup",
                            location="Remote",
                            employment_type="Full-time",
                            salary="Unknown",
                            experience="Unknown",
                            description="Extracted via Playwright",
                            skills=[],
                            url=href if href.startswith("http") else f"https://wellfound.com{href}",
                            source="Wellfound",
                            posted_date=datetime.utcnow().isoformat(),
                            company_logo=None,
                            remote=True
                        ))
                    except Exception as e:
                        system_logger.warning(f"Error parsing Wellfound job card: {e}")
                
                browser.close()
        except Exception as e:
            system_logger.error(f"Playwright Wellfound scraping failed: {e}")
            raise Exception(f"Playwright Wellfound scraping failed: {e}")
            
        return jobs

ProviderRegistry.register(WellfoundProvider())
