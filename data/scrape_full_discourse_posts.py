import json, time
from playwright.sync_api import sync_playwright

SESSION_DIR = "auth_storage/session.json"
INPUT_FILE = "tds_kb_posts.json"
OUTPUT_FILE = "tds_kb_full_posts.json"

def scrape_post_content(playwright, posts):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=SESSION_DIR)
    page = context.new_page()

    results = []
    for i, post in enumerate(posts):
        url = post.get("url")
        if not url:
            continue

        try:
            print(f"[{i+1}/{len(posts)}] Visiting {url}")
            page.goto(url, timeout=60000)
            page.wait_for_selector(".topic-body .cooked", timeout=15000)

            content_el = page.query_selector(".topic-body .cooked")
            content = content_el.inner_text().strip() if content_el else ""

            results.append({
                "title": post.get("title"),
                "url": url,
                "content": content
            })

        except Exception as e:
            print(f"⚠️ Failed to load {url}: {e}")

        time.sleep(1)

    context.close()
    browser.close()
    return results

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    with sync_playwright() as playwright:
        full_posts = scrape_post_content(playwright, posts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_posts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(full_posts)} posts to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
