# services/test_runner.py
import sys
import json
from playwright.sync_api import sync_playwright
import time

def run_tests(base_url: str) -> list:
    issues = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        time.sleep(1)  

        # Wishlist remove button
        page.goto(f"{base_url}#wishlist")
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)
        remove_btn = page.query_selector('button:has-text("Remove"), button:has-text("🗑"), .remove-from-wishlist')
        if not remove_btn:
            issues.append({
                "severity": "high",
                "component": "wishlist",
                "issue": "No 'Remove' button on wishlist items",
                "suggestion": "Each wishlist item must have a visible remove button.",
                "fix_type": "deterministic"
            })

        # Cart functionality
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        # Wait for product cards to appear
        try:
            page.wait_for_selector('.product-card, .grid > div', timeout=5000)
        except:
            issues.append({
                "severity": "high",
                "component": "cart",
                "issue": "No product cards found on page",
                "suggestion": "Ensure products are loaded from API and rendered.",
                "fix_type": "ai_function"
            })
            browser.close()
            return issues

        # Find add to cart button on first product
        add_to_cart = page.query_selector('.product-card button:has-text("Add to Cart"), .add-to-cart')
        if add_to_cart:
            try:
                # Wait for button to be attached and visible
                add_to_cart.wait_for_element_state("stable", timeout=3000)
                add_to_cart.click()
                page.wait_for_timeout(500)
                cart_link = page.query_selector('a[href*="cart"], button:has-text("Cart")')
                if cart_link:
                    cart_link.click()
                    page.wait_for_load_state("networkidle")
                    cart_items = page.query_selector_all('.cart-item, [data-cart-item]')
                    if len(cart_items) == 0:
                        issues.append({
                            "severity": "high",
                            "component": "cart",
                            "issue": "Cart shows empty after adding product",
                            "suggestion": "Call loadCart() after POST and re-render cart.",
                            "fix_type": "deterministic"
                        })
            except Exception as e:
                print(f"Cart test error: {e}")
        else:
            issues.append({
                "severity": "medium",
                "component": "cart",
                "issue": "No 'Add to Cart' button on product cards",
                "suggestion": "Add an add-to-cart button that calls addToCart(productId).",
                "fix_type": "ai_function"
            })

        # Login modal test
        login_btn = page.query_selector('button:has-text("Login"), a:has-text("Login")')
        if not login_btn:
            issues.append({
                "severity": "medium",
                "component": "auth",
                "issue": "Missing Login/Register button",
                "suggestion": "Add a login button that opens a modal with login/register tabs.",
                "fix_type": "deterministic"
            })

        # Product detail page test
        first_product = page.query_selector('.product-card, .grid > div')
        if first_product:
            try:
                first_product.click()
                page.wait_for_timeout(1000)
                if "#product" not in page.url:
                    issues.append({
                        "severity": "high",
                        "component": "pdp",
                        "issue": "Product detail page not reachable",
                        "suggestion": "Implement viewProduct() with hash routing (#product/ID).",
                        "fix_type": "ai_function"
                    })
                add_btn_pdp = page.query_selector('button:has-text("Add to Cart")')
                if not add_btn_pdp:
                    issues.append({
                        "severity": "high",
                        "component": "pdp",
                        "issue": "PDP missing 'Add to Cart' button",
                        "suggestion": "Place an add-to-cart button on the product detail page.",
                        "fix_type": "deterministic"
                    })
            except Exception as e:
                print(f"PDP test error: {e}")

        # Footer test
        footer = page.query_selector('footer')
        if not footer:
            issues.append({
                "severity": "high",
                "component": "footer",
                "issue": "Missing <footer> element",
                "suggestion": "Add a footer with brand, tagline, links, and copyright.",
                "fix_type": "deterministic"
            })

        # Console errors test
        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
        page.reload()
        page.wait_for_timeout(2000)
        if console_errors:
            issues.append({
                "severity": "high",
                "component": "javascript",
                "issue": f"Console errors: {console_errors[:2]}",
                "suggestion": "Fix undefined variables, missing API handlers, or incorrect selectors.",
                "fix_type": "ai_function"
            })

        browser.close()
    return issues

if __name__ == "__main__":
    base_url = sys.argv[1]
    issues = run_tests(base_url)
    print(json.dumps(issues))