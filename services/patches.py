# Import Necessary Libraries
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Add wishlist remove button
def add_wishlist_remove_button(js_path: Path) -> bool:
    """Insert a remove button in renderWishlist() if missing."""
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()
    if "removeFromWishlist" in js and "Remove" in js:
        return False  
    
    # Add remove button inside the wishlist item template
    pattern = r'(<div class="[^"]*wishlist-item[^"]*">.*?)(</div>)'
    replacement = r'\1<button onclick="removeFromWishlist(item.product_id)" class="remove-wishlist-btn">🗑 Remove</button>\2'
    new_js = re.sub(pattern, replacement, js, flags=re.DOTALL)
    
    # Ensure removeFromWishlist function exists
    if "function removeFromWishlist" not in new_js:
        remove_func = """
        async function removeFromWishlist(productId) {
            const response = await fetch(`${API_BASE}/wishlist/${productId}`, { method: 'DELETE' });
            if (response.ok) {
                await loadWishlist();
                render();
                showToast('Removed from wishlist');
            }
        }
        """
        new_js = new_js.replace("</script>", remove_func + "\n</script>")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(new_js)
    return True

# Add footer if missing
def add_footer_if_missing(html_path: Path, brand: str, category: str) -> bool:
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    if "<footer" in html:
        return False
    soup = BeautifulSoup(html, 'html.parser')
    footer = soup.new_tag("footer")
    footer.string = f"© {brand} - Best {category} deals"
    soup.body.append(footer)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    return True

# Fix cart refresh
def fix_cart_refresh(js_path: Path) -> bool:
    """Ensure addToCart calls loadCart() and re-renders."""
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    start_idx = js.find('async function addToCart')
    if start_idx == -1:
        return False
        
    brace_count = 0
    in_function = False
    end_idx = -1
    
    for i in range(start_idx, len(js)):
        if js[i] == '{':
            brace_count += 1
            in_function = True
        elif js[i] == '}':
            brace_count -= 1
            
        if in_function and brace_count == 0:
            end_idx = i
            break
            
    if end_idx != -1:
        func_body = js[start_idx:end_idx]
        if "loadCart" not in func_body or "render" not in func_body:
            new_func = func_body + "    await loadCart();\n    render();\n"
            new_js = js[:start_idx] + new_func + js[end_idx:]
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(new_js)
            return True

    return False