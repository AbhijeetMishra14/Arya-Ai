from playwright.sync_api import sync_playwright

class InternetModule:
    """Handles deep web automation using Playwright (Puppeteer for Python)."""

    def extract_website_content(self, url: str) -> str:
        """Opens a specific URL, waits for the page to load, and extracts the visible text. Use this when you need detailed context from a specific link."""
        try:
            with sync_playwright() as p:
                # Launch Chromium (Puppeteer equivalent headless browser)
                browser = p.chromium.launch(headless=True, args=['--log-level=3'])
                page = browser.new_page()
                
                # Navigate to the URL
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                
                # Extract text from the body
                text = page.locator("body").inner_text()
                browser.close()
                
                # Truncate to avoid blowing up the LLM context window
                max_chars = 8000
                if len(text) > max_chars:
                    return f"Content extracted from {url} (truncated):\n\n{text[:max_chars]}..."
                
                return f"Content extracted from {url}:\n\n{text}"
        except Exception as e:
            return f"Failed to automate browser and extract content from {url}: {str(e)}"

    def get_current_location(self) -> str:
        """Retrieves the user's current city and country based on IP geolocation. Use this first before answering location-based questions."""
        import requests
        try:
            # High-speed IP geolocation fetch
            response = requests.get('https://ipapi.co/json/', timeout=5).json()
            city = response.get('city', 'Unknown')
            region = response.get('region', 'Unknown')
            country = response.get('country_name', 'Unknown')
            lat = response.get('latitude', 'Unknown')
            lon = response.get('longitude', 'Unknown')
            return f"Neural Geosync Successful. Location: {city}, {region}, {country} (Lat/Lon: {lat}, {lon})."
        except Exception as e:
            return f"Geolocation fetch failed: {str(e)}"

    def search_google(self, query: str) -> str:
        """Searches Google for the specified query and returns the top result titles and links. Use this during complex system troubleshooting to find technical solutions."""
        import requests
        from bs4 import BeautifulSoup
        try:
            # Standard desktop User-Agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            url = f"https://www.google.com/search?q={query}"
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            results = []
            for g in soup.find_all('div', class_='g')[:5]:
                h3 = g.find('h3')
                a = g.find('a')
                if h3 and a:
                    title = h3.text
                    link = a['href']
                    if "/url?q=" in link: 
                        link = link.split("/url?q=")[1].split("&sa=")[0]
                    results.append(f"• {title}: {link}")
            
            if not results:
                return f"Neural research check for '{query}' returned no immediate results."
            return f"Top research results for '{query}':\n" + "\n".join(results)
        except Exception as e:
            return f"Neural research failed: {str(e)}"
