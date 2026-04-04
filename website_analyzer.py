# Import Necessary Libraries
import os
import json
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from pathlib import Path
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import google.generativeai as genai

load_dotenv()

# Load the Model.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3-flash-preview")

# Function to do the mock server.
def start_mock_server(directory, port=8888):
    """Start HTTP server in a background thread, serving from 'directory'."""
    original_dir = os.getcwd()
    os.chdir(str(directory))
    
    handler = MockAPIHandler
    httpd = HTTPServer(("localhost", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    # Store original dir to allow changing back if needed)
    httpd.original_dir = original_dir
    return httpd, port


# Mock API server
class MockAPIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self._handle_api_get()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):  
            self._handle_api_post()
        else:
            self.send_error(404)
    
    def _handle_api_get(self):
        parts = self.path.split('/')
        if len(parts) < 3:
            self.send_error(404)
            return
        slug = parts[2]
        endpoint = '/'.join(parts[3:])

        products = [
            {"id": 1, "title": "Classic Tee", "mrp": 29.99, "special_price": 19.99,
             "stock_status": "in_stock", "image_url": "https://picsum.photos/id/1/400/500"},
            {"id": 2, "title": "Running Shoes", "mrp": 89.99, "special_price": 69.99,
             "stock_status": "in_stock", "image_url": "https://picsum.photos/id/20/400/500"},
            {"id": 3, "title": "Denim Jacket", "mrp": 79.99, "special_price": 59.99,
             "stock_status": "out_of_stock", "image_url": ""}
        ]

        if endpoint == 'products':
            data = {"success": True, "products": products}
        elif endpoint.startswith('product/'):
            try:
                pid = int(endpoint.split('/')[1])
            except:
                pid = None
            prod = next((p for p in products if p['id'] == pid), None) if pid else None
            data = {"product": prod} if prod else {"error": "not found"}
        elif endpoint == 'cart':
            data = {"cart": [], "total_items": 0, "total_price": 0}
        elif endpoint == 'wishlist':
            data = {"wishlist": [], "total_items": 0}
        else:
            data = {"error": "unknown"}
        self._send_json(data)

    def _handle_api_post(self):
        parts = self.path.split('/')
        if len(parts) < 3:
            self.send_error(404)
            return
        endpoint = '/'.join(parts[3:])

        if 'cart' in endpoint or 'wishlist' in endpoint or endpoint == 'checkout':
            data = {"success": True, "message": "OK"}
        elif endpoint == 'register':
            data = {"success": True, "message": "User registered"}
        elif endpoint == 'login':
            data = {"success": True, "user_id": 1, "message": "Login successful"}
        else:
            data = {"error": "unknown"}
        self._send_json(data)

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        pass 


class WebsiteAnalyzerAgent:
    def __init__(self, site_dir: str):
        self.site_dir = Path(site_dir).resolve()
        self.slug = self.site_dir.name
        self.server = None
        self.port = None
        self.issues = []

    async def run(self):
        print(f"\nAnalyzing {self.slug} ...")
        
        self.server, self.port = start_mock_server(self.site_dir)
        base_url = f"http://localhost:{self.port}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                console_errors = []
                page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)

                # Home page
                await page.goto(base_url)
                await page.wait_for_load_state('networkidle')

                # Functional & UI checks
                await self._check_footer(page)
                await self._check_product_grid(page)
                await self._check_product_detail(page)
                await self._check_cart_operations(page)
                await self._check_wishlist(page)
                await self._check_login_modal(page)   
                await self._check_responsive(page, base_url)

                # Performance check
                perf = await page.evaluate('''() => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    return { loadTime: nav.loadEventEnd - nav.fetchStart };
                }''')
                if perf['loadTime'] > 3000:
                    self.issues.append({
                        "severity": "medium",
                        "category": "Performance",
                        "issue": f"Page load time {perf['loadTime']:.0f}ms > 3s",
                        "suggestion": "Optimize images, defer JS, use lazy loading."
                    })

                # UX critique with Gemini
                ux_issues = await self._gemini_ux_critique(page)
                self.issues.extend(ux_issues)

                # Console errors
                if console_errors:
                    self.issues.append({
                        "severity": "high",
                        "category": "JavaScript Errors",
                        "issue": f"{len(console_errors)} console error(s): {console_errors[:2]}",
                        "suggestion": "Fix undefined variables, missing event listeners, or broken API calls."
                    })

                await browser.close()
        finally:
            # Stop server and restore original working directory
            if self.server:
                self.server.shutdown()
                # Restore original directory if needed
                if hasattr(self.server, 'original_dir'):
                    os.chdir(self.server.original_dir)

        self._print_issues_list()
        return self.issues

    async def _check_footer(self, page):
        footer = await page.query_selector('footer')
        if not footer:
            self.issues.append({
                "severity": "high",
                "category": "UI Structure",
                "issue": "Missing <footer> element",
                "suggestion": "Add a footer with brand, links, social icons, and copyright."
            })
            return

        has_year = await page.evaluate('''() => {
            const footer = document.querySelector('footer');
            const year = new Date().getFullYear();
            return footer?.innerText.includes(year.toString());
        }''')
        if not has_year:
            self.issues.append({
                "severity": "low",
                "category": "Content",
                "issue": "Footer missing or not auto-updating copyright year",
                "suggestion": "Use JavaScript to insert current year in footer."
            })

    async def _check_product_grid(self, page):
        cards = await page.query_selector_all('.product-card, .grid > div, [data-product-id]')
        if len(cards) == 0:
            self.issues.append({
                "severity": "high",
                "category": "Functionality",
                "issue": "No product cards displayed on shop page",
                "suggestion": "Ensure products are fetched from API and rendered correctly."
            })
            return

        img = await page.query_selector('.product-card img')
        if img:
            src = await img.get_attribute('src')
            if not src or 'placehold.co' in src:
                self.issues.append({
                    "severity": "medium",
                    "category": "UI",
                    "issue": "Product image missing or using fallback placeholder",
                    "suggestion": "Verify API returns valid image_url and onerror handler is present."
                })

    async def _check_product_detail(self, page):
        first_card = await page.query_selector('.product-card, .grid > div')
        if not first_card:
            return
        await first_card.click()
        await page.wait_for_timeout(1000)
        if '#product' not in page.url and '/product' not in page.url:
            self.issues.append({
                "severity": "high",
                "category": "Navigation",
                "issue": "Product Detail Page (PDP) not reachable",
                "suggestion": "Implement viewProduct() with hash routing (e.g., #product/123)."
            })
        add_btn = await page.query_selector('button:has-text("Add to Cart")')
        if not add_btn:
            self.issues.append({
                "severity": "high",
                "category": "Functionality",
                "issue": "PDP missing 'Add to Cart' button",
                "suggestion": "Add addToCart() call on PDP."
            })

    async def _check_cart_operations(self, page):
        await page.goto(f"http://localhost:{self.port}")
        add_btn = await page.query_selector('.product-card button:has-text("Add to Cart"), .add-to-cart')
        if add_btn:
            await add_btn.click()
            await page.wait_for_timeout(500)
            cart_link = await page.query_selector('a[href*="cart"], button:has-text("Cart")')
            if cart_link:
                await cart_link.click()
                await page.wait_for_timeout(500)
                items = await page.query_selector_all('.cart-item, [data-cart-item]')
                if len(items) == 0:
                    self.issues.append({
                        "severity": "high",
                        "category": "Cart",
                        "issue": "Cart page shows empty after adding product",
                        "suggestion": "Call loadCart() after POST and render cart items."
                    })
            else:
                self.issues.append({
                    "severity": "medium",
                    "category": "Navigation",
                    "issue": "No visible link/button to view cart",
                    "suggestion": "Add a cart icon with item count."
                })

    async def _check_wishlist(self, page):
        await page.goto(f"http://localhost:{self.port}")
        wish_btn = await page.query_selector('.product-card button:has-text("Wishlist"), .add-to-wishlist')
        if not wish_btn:
            self.issues.append({
                "severity": "low",
                "category": "Functionality",
                "issue": "No wishlist button on products",
                "suggestion": "Add 'Add to Wishlist' button and call /api/{slug}/wishlist/{id}."
            })

    async def _check_login_modal(self, page):
        login_btn = await page.query_selector('button:has-text("Login"), a:has-text("Login")')
        if not login_btn:
            self.issues.append({
                "severity": "medium",
                "category": "Auth",
                "issue": "No login/register button",
                "suggestion": "Implement a login modal that appears when user clicks 'Account' or tries to checkout."
            })
            return
        await login_btn.click()
        await page.wait_for_timeout(500)
        modal = await page.query_selector('.modal, [role="dialog"]')
        if not modal:
            self.issues.append({
                "severity": "high",
                "category": "Auth",
                "issue": "Login modal does not appear after clicking login button",
                "suggestion": "Create a modal with email/password fields and connect to /api/{slug}/login."
            })

    async def _check_responsive(self, page, base_url):
        for width in [375, 768]:
            await page.set_viewport_size({"width": width, "height": 800})
            await page.goto(base_url)
            scroll_width = await page.evaluate('document.documentElement.scrollWidth')
            if scroll_width > width + 10:
                self.issues.append({
                    "severity": "medium",
                    "category": "Responsive",
                    "issue": f"Horizontal scroll at {width}px width (scrollWidth={scroll_width})",
                    "suggestion": "Use flex-wrap, grid with minmax, and avoid fixed widths."
                })

    async def _gemini_ux_critique(self, page):
        screenshot = await page.screenshot(full_page=True)
        prompt = """
        You are a UX expert. Analyze this e-commerce website screenshot.
        Return a JSON list of issues. Each issue: {"severity":"low/medium/high", "category":"...", "issue":"...", "suggestion":"..."}
        Focus on: visual hierarchy, color contrast, typography, button placement, spacing, clarity of CTAs, mobile friendliness.
        """
        response = model.generate_content(
            [prompt, {"mime_type": "image/png", "data": screenshot}],
            generation_config={"response_mime_type": "application/json"}
        )
        try:
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini UX critique failed: {e}")
            return []

    def _print_issues_list(self):
        print("\n" + "="*70)
        print(f"ANALYSIS COMPLETE for '{self.slug}' – {len(self.issues)} ISSUES FOUND")
        print("="*70)
        if not self.issues:
            print("No issues detected! Great job.")
            return
        for i, issue in enumerate(self.issues, 1):
            sev = issue.get('severity', 'unknown').upper()
            cat = issue.get('category', 'General')
            desc = issue.get('issue', 'No description')
            sugg = issue.get('suggestion', 'No suggestion')
            print(f"\n{i}. [{sev}] {cat}")
            print(f"Issue: {desc}")
            print(f"Fix:   {sugg}")
        print("\n" + "="*70)


async def analyze_site(site_folder_path):
    agent = WebsiteAnalyzerAgent(site_folder_path)
    issues_list = await agent.run()
    return issues_list

if __name__ == "__main__":
    asyncio.run(analyze_site("sites/website_bio_books"))
