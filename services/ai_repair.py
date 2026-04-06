# Import Necessary Libraries
import re
from services.ai_generator import ai_generator

# Fix add to cart logic
async def fix_add_to_cart_logic(js_path: str, api_base: str) -> bool:
    with open(js_path, 'r') as f:
        js = f.read()
    
    # Extract existing addToCart function
    match = re.search(r'(async function addToCart\([^)]*\)\s*\{.*?\})', js, re.DOTALL)
    if not match:
        return False
    old_func = match.group(1)
    prompt = f"""
    The following addToCart function does not update the cart UI correctly.
    Rewrite it to:
    1. Send POST request to `{api_base}/cart/{{productId}}`
    2. After success, call `await loadCart()` and `render()`
    3. Show a toast message "Added to cart"
    Return ONLY the corrected function code (no extra text).

    Current function:
    {old_func}
    """
    response_text, _ = ai_generator.generate_code(prompt, is_json=False)
    if response_text:
        new_js = js.replace(old_func, response_text.strip())
        with open(js_path, 'w') as f:
            f.write(new_js)
        return True
    return False