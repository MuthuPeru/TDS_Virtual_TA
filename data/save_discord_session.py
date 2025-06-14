from playwright.sync_api import sync_playwright
import os

SESSION_FILE = "auth_storage/session.json"
os.makedirs("auth_storage", exist_ok=True)

def save_login_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Open UI so you can log in
        context = browser.new_context()  # Do NOT load any previous session
        page = context.new_page()

        print("🔐 Opening login page... Please log in using Google.")
        page.goto("https://discourse.onlinedegree.iitm.ac.in/login")

        print("⏳ Waiting for login to complete...")
        page.wait_for_url("https://discourse.onlinedegree.iitm.ac.in/", timeout=180000)

        context.storage_state(path=SESSION_FILE)
        print(f"✅ Session saved to {SESSION_FILE}")
        browser.close()

if __name__ == "__main__":
    save_login_session()
