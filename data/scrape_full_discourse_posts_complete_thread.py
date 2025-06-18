import json, time
from playwright.sync_api import sync_playwright

SESSION_DIR = "auth_storage/session.json"
INPUT_FILE = "tds_kb_posts.json"
OUTPUT_FILE = "tds_kb_full_threads.json"

def scrape_full_thread(playwright, posts):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=SESSION_DIR)
    page = context.new_page()

    all_threads = []
    for i, post in enumerate(posts):
        url = post.get("url")
        title = post.get("title")
        if not url:
            continue

        try:
            print(f"[{i+1}/{len(posts)}] Visiting thread: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_selector(".topic-body .cooked", timeout=15000)

            # Collect all posts in the thread
            post_els = page.query_selector_all("article")
            thread_posts = []

            for el in post_els:
                try:
                    username = el.query_selector(".creator a")
                    timestamp = el.query_selector("time")
                    content_el = el.query_selector(".cooked")

                    thread_posts.append({
                        "username": username.inner_text().strip() if username else "",
                        "created_at": timestamp.get_attribute("datetime") if timestamp else "",
                        "content": content_el.inner_text().strip() if content_el else ""
                    })
                except Exception as sub_e:
                    print(f"  ⚠️ Skipped a post due to error: {sub_e}")

            all_threads.append({
                "title": title,
                "url": url,
                "posts": thread_posts
            })

        except Exception as e:
            print(f"⚠️ Failed to load thread {url}: {e}")

        time.sleep(1)

    context.close()
    browser.close()
    return all_threads

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    with sync_playwright() as playwright:
        full_threads = scrape_full_thread(playwright, posts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full_threads, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(full_threads)} threads to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
