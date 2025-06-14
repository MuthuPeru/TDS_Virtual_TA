import json
from playwright.sync_api import sync_playwright

COOKIES_FILE = "tds_cookies.json"
OUTPUT_FILE = "tds_kb_posts.json"
CATEGORY_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34/l/latest"

def load_saved_context(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Load previously saved cookies
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
        context.add_cookies(cookies)

    return browser, context

def scrape_tds_kb_posts():
    with sync_playwright() as p:
        browser, context = load_saved_context(p)
        page = context.new_page()
        print("🔍 Navigating to TDS KB page...")
        page.goto(CATEGORY_URL)
        page.wait_for_selector("table.topic-list", timeout=10000)

        print("📥 Scraping post titles and URLs...")
        rows = page.query_selector_all("table.topic-list tbody tr")

        posts = []
        for row in rows:
            title_elem = row.query_selector("a.title")
            if title_elem:
                title = title_elem.inner_text().strip()
                url = title_elem.get_attribute("href")
                if url and not url.startswith("http"):
                    url = f"https://discourse.onlinedegree.iitm.ac.in{url}"
                posts.append({"title": title, "url": url})

        print(f"✅ Found {len(posts)} posts. Saving to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

        browser.close()

if __name__ == "__main__":
    scrape_tds_kb_posts()
