from playwright.sync_api import sync_playwright
import json

COOKIES_FILE = "tds_cookies.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Open browser visibly
    context = browser.new_context()
    page = context.new_page()

    print("🧭 Navigate to login page manually and log in.")
    page.goto("https://discourse.onlinedegree.iitm.ac.in/login")

    input("✅ After logging in, press Enter here to continue...")

    # Save cookies
    cookies = context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)

    print(f"✅ Saved session cookies to {COOKIES_FILE}")
    browser.close()
