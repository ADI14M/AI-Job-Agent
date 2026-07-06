import time
from playwright.sync_api import sync_playwright
import os

ROUTES = [
    "/",
    "/login",
    "/resumes",
    "/jobs",
    "/application-package",
    "/career-memory",
    "/automation"
]

def main():
    os.makedirs("screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        base_url = "http://localhost:5173"
        
        for route in ROUTES:
            url = f"{base_url}{route}"
            print(f"Visiting {url}...")
            try:
                page.goto(url, timeout=10000)
                # Wait a bit for React to render
                time.sleep(2)
                
                # Check for vite error overlay
                error_overlay = page.locator("vite-error-overlay").count()
                if error_overlay > 0:
                    print(f"FAILED: Vite Error Overlay found on {route}")
                
                # Save screenshot
                safe_name = route.replace("/", "_")
                if safe_name == "_":
                    safe_name = "_dashboard"
                
                page.screenshot(path=f"screenshots/{safe_name}.png", full_page=True)
                print(f"SUCCESS: {route}")
            except Exception as e:
                print(f"FAILED to visit {route}: {e}")
                
        browser.close()

if __name__ == "__main__":
    main()
