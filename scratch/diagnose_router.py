from arya.modules.router import RouterModule
from arya.core.config import Config
import logging

# Set up logging to console to see what's happening
logging.basicConfig(level=logging.INFO)

def diagnose():
    print("--- ARYA Router Module Diagnostic ---")
    router = RouterModule()
    
    print(f"\nTarget URL: {router.url}")
    print(f"Target User: {router.username}")
    
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Launching with headless=False to potentially see what's happening if I could see the screen
        # But I can't, so I'll stay headless and rely on logs.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("\nAttempting Login...")
        success = router._login(page)
        
        if success:
            print("✅ Login Successful!")
            print("\nTesting Status Fetch...")
            status = router.get_router_status()
            print(f"Status: {status}")
        else:
            print("❌ Login Failed. Check router_control.log for details.")
            # Let's take a screenshot if it failed
            page.screenshot(path="login_failed_debug.png")
            print("Saved debug screenshot to login_failed_debug.png")
        
        browser.close()

if __name__ == "__main__":
    diagnose()
