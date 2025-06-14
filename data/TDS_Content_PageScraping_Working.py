import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://tds.s-anand.net/#/"
OUTPUT_FILE = "data/tds_content.json"

TDS_PATHS = [
    "development-tools",
    "vscode",
    "github-copilot",
    
    # Add more paths if needed
]

def scrape_tds():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        content = {}

        for path in TDS_PATHS:
            full_url = BASE_URL + path
            print(f"Visiting {full_url}")
            page.goto(full_url)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            try:
                body = page.query_selector("main")
                text = body.inner_text()
                content[path] = text
            except Exception as e:
                print(f"Failed to extract {path}: {e}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        print(f"Scraped {len(content)} pages.")
        browser.close()

if __name__ == "__main__":
    scrape_tds()
