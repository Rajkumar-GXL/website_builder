# Import necessary Libraries
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import json
import random

load_dotenv()

# Class to generte the website
class WebsiteGenerator:
    # Function to do the initialization
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def clean_code(self, text):
        text = re.sub(r"```(?:json|html|javascript|css)?\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        return text.strip()

    def extract_json(self, text):
        try:
            match = re.search(r'\{[\s\S]*\}', text)
            if not match:
                return "{}"
            json_str = match.group(0)
            # Fix trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json_str
        except Exception as e:
            print(f"JSON extraction error: {e}")
            return "{}"
    
    # Function to generate website application.
    def generate_code(self, prompt: str) -> str:
        for attempt in range(2):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.85,      
                        "top_p": 0.95,
                        "response_mime_type": "application/json"
                    }
                )
                if response.text:
                    return self.clean_code(response.text)
                if response.candidates:
                    parts = response.candidates[0].content.parts
                    text = "".join(p.text for p in parts if hasattr(p, "text"))
                    return self.clean_code(text)
            except Exception as e:
                print(f"Gemini attempt {attempt+1} error: {e}")
        return ""

    def save_website_files(self, files_dict, slug):
        sites_dir = "sites"
        os.makedirs(sites_dir, exist_ok=True)
        site_dir = os.path.join(sites_dir, slug)
        os.makedirs(site_dir, exist_ok=True)
        saved = []
        for filename, content in files_dict.items():
            if content:
                filepath = os.path.join(site_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved.append(filepath)
                print(f"Saved: {filepath}")
        return saved

    # Function to generate the full Application
    def generate_full_application(self, slug, title, category):
        design_systems = [
            {
                "style": "Clean Modern (soft shadows, rounded corners, white space)",
                "nav": "Top sticky navbar with dropdown menus and search bar",
                "layout": "Responsive product grid (3-4 columns on desktop)"
            },
            {
                "style": "Bold & Vibrant (high contrast, accent colors, playful but professional)",
                "nav": "Left sidebar navigation with category accordion",
                "layout": "Masonry grid for product discovery"
            },
            {
                "style": "Minimal & Elegant (serif headings, light background, fine lines)",
                "nav": "Centered top bar with hamburger menu on mobile",
                "layout": "List view with large product images"
            },
            {
                "style": "Corporate/Trustworthy (blue/grays, card-based, clear CTAs)",
                "nav": "Traditional top bar with mega menu for categories",
                "layout": "Grid with quick-view modal on hover"
            },
            {
                "style": "Lifestyle/Editorial (large imagery, magazine-style typography)",
                "nav": "Floating action button that reveals quick links",
                "layout": "Full-width hero + 3-column product showcase"
            },
            {
                "style": "Dark Mode E‑commerce (dark background, neon accents, high readability)",
                "nav": "Bottom navigation bar (mobile-first) + top search",
                "layout": "Card-based grid with add-to-cart buttons"
            }
        ]
        
        hero_styles = [
            "Full-width hero with headline, CTA, and background product image",
            "Split hero: left side text + email signup, right side carousel",
            "Centered hero with animated text and shop now button",
            "Minimal hero: large brand statement + simple illustration",
            "Video background hero with overlay text and CTA"
        ]
        
        typography_styles = [
            "Sans-serif headings (Inter) + Sans-serif body (system-ui)",
            "Serif headings (Playfair Display) + Sans-serif body (Roboto)",
            "Modern geometric (Poppins) for both headings and body",
            "Slab serif (Roboto Slab) for headings + Open Sans for body"
        ]

        interaction_styles = [
            "Subtle hover scale on product cards, fade-in animations",
            "Slide-up effects on scroll, smooth page transitions",
            "Button ripple effects, loading skeletons",
            "Hover underline for links, zoom on product images"
        ]

        color_directions = [
            "Neutral & Minimal (warm off-white, soft gray, charcoal, subtle beige, pure white) – clean and elegant",
            "Professional Blue (navy, slate, steel blue, light blue, white) – trustworthy, corporate",
            "Forest & Sage (deep green, sage, cream, warm gray, dark charcoal) – natural, sustainable brands",
            "Warm Terracotta (clay, sand, cream, rust, warm brown) – artisan, handmade, cozy",
            "Cool Gray & Indigo (indigo, cool gray, light gray, white, soft blue) – tech, modern, sleek",
            "Luxury Monochrome (black, off-black, dark charcoal, champagne, ivory) – high‑end fashion",
            "Soft Pastel Commerce (dusty rose, pale mint, lavender, cream, light gray) – beauty, wellness",
            "Deep Ocean (teal, navy, aqua, white, light gray) – travel, electronics, reliability",
            "Earthy Olive (olive green, tan, off-white, dark brown, warm gray) – outdoor, organic",
            "Clean White & Slate (white, slate, light gray, dark gray, subtle blue accent) – SaaS, modern retail"
        ]

        design = random.choice(design_systems)
        hero = random.choice(hero_styles)
        typography = random.choice(typography_styles)
        interaction = random.choice(interaction_styles)
        chosen_color_direction = random.choice(color_directions)

        prompt = f"""
        Build a COMPLETE, WORKING e-commerce website. Use the following exact specifications.        
        
        Brand: {title}
        Category: {category}
        Slug: {slug}

        DESIGN:
        - Theme: {design['style']}
        - Navigation: {design['nav']}
        - Layout: {design['layout']}
        - Hero section: {hero}
        - Typography: {typography}
        - Micro-interactions: {interaction}
        - Color direction: {chosen_color_direction} (generate 5 CSS variables)

        **FOOTER REQUIREMENTS (MUST INCLUDE):**
        - Create a `<footer>` element at the bottom of every page.
        - The footer must be visually consistent with the overall design (use the same color scheme).
        - Include:
            * Brand name: "{title}"
            * Tagline related to the category "{category}" (e.g., "Best {category} deals").
            * Useful links: Home, Shop, About Us, Contact, Privacy Policy, Terms of Service.
            * Social media icons (use Font Awesome CDN or simple text links).
            * Copyright notice with current year (auto-updating using JavaScript).
        - The footer should be responsive (stack on mobile).
        - Do not hardcode placeholder text – use the actual brand and category.
        - Use `<hr>` or border-top to separate from main content.
        
        CRITICAL RULES (MUST FOLLOW):
        1. Every function must be implemented exactly as described.
        2. The website must work without errors – no undefined variables, no missing event listeners.
        3. Use the API responses for all data – DO NOT hardcode products or images.
        4. Escape double quotes inside strings with backslash.
        5. No trailing commas in JSON.
        6. All JavaScript must be self-contained and initialised after DOMContentLoaded.
        7. The `slug` must be used to construct all API URLs: const API_BASE = `/api/{slug}`;

        **IMAGE HANDLING (STRICT):**
        - Always use `product.image_url` from the API response.
        - If `image_url` is empty/null, display a fallback grey box with "No Image".
        - Add `onerror="this.src='https://placehold.co/400x500?text=No+Image'"` to every `<img>` tag.
        - In JavaScript, map products ensuring `image_url` is used exactly as returned.
        
        **REQUIRED FUNCTIONALITY (ALL MUST WORK):**
        1. localStorage: save/load cart and wishlist (as backup, but primary data comes from backend APIs).
        2. All views: home, shop, product detail (PDP), profile, cart, wishlist, checkout, login/register modal.
        3. Use Tailwind CSS CDN + custom CSS for unique styling.
        
        **PRODUCT DETAIL PAGE (PDP) – MUST IMPLEMENT:**
        - When a product card is clicked (anywhere on the card), call `viewProduct(id)`.
        - `viewProduct(id)` must:
        - Fetch product from `GET ${{API_BASE}}/product/${{id}}`
        - Store result in `state.currentProduct`
        - Set `state.view = 'product'`
        - Call `render()`
        - PDP must show:
        - Large product image (using `image_url` with fallback)
        - Product title, price (special_price and MRP strikethrough)
        - Stock status (if available)
        - Quantity selector (1–10)
        - "Add to Cart" button that calls `addToCart(id, quantity)`
        - "Add to Wishlist" button
        - "Back to Shop" link that switches to `view='shop'`
        - Implement URL hash routing (e.g., `#product/123`) so PDP is directly reachable.
        
        --- BACKEND API REFERENCE ---
        1. Products:
        GET    /api/{{website}}/products
        Response: {{
            "success": true,
            "website": "...",
            "total_products": 10,
            "products": [
                {{
                    "id": 1,
                    "name": "...",
                    "title": "...",
                    "mrp": 0,
                    "special_price": 0,
                    "stock_count": 0,
                    "stock_status": "...",
                    "image_url": "...",
                    "created_at": "..."
                }}
            ]
        }}

        GET    /api/{{website}}/product/{{product_id}}
        Response: {{
            "product": 
            {{                     
                "id": 1,
                "name": "...",
                "title": "...",
                "mrp": 0,
                "special_price": 0,
                "stock_count": 0,
                "stock_status": "...",
                "image_url": "...",
                "created_at": "..."
            }}
        }}

        2. Cart:
        GET    /api/{{website}}/cart
        Response: {{
            "cart": [
                {{
                    "cart_id": 1,
                    "product_id": 1,
                    "quantity": 1,
                    "added_date": "...",
                    "product": {{
                        "title": "...",
                        "price": 0,
                        "image": "..."
                    }}
                }}
            ],
            "total_items": 1,
            "total_price": 100,
            "message": "..."
        }}

        POST   /api/{{website}}/cart/{{product_id}}
        DELETE /api/{{website}}/cart/{{product_id}}
        Response: {{ "success": true, "message": "...", "product_id": 1 }}

        3. Wishlist:
        GET    /api/{{website}}/wishlist
        POST   /api/{{website}}/wishlist/{{product_id}}
        DELETE /api/{{website}}/wishlist/{{product_id}}
        Response (GET): {{
            "wishlist": [ ...same structure as cart... ],
            "total_items": 1,
            "message": "..."
        }}
        Response (POST/DELETE): {{ "success": true, "message": "...", "product_id": 1 }}

        4. Checkout:
        POST   /api/{{website}}/checkout
        Response: {{
            "success": true,
            "message": "Order placed successfully!",
            "order": {{
                "order_id": "...",
                "items": [{{ "product_id": 1, "title": "...", "quantity": 1, "price": 0, "total": 0 }}],
                "subtotal": 0,
                "tax_gst": 0,
                "grand_total": 0,
                "status": "confirmed",
                "timestamp": "..."
            }}
        }}

        ### 6. USER AUTH FLOW
        Before placing an order (checkout), the user must be registered and logged in:

        1. Registration:
        POST /api/{{website}}/register
        Request body: {{
            "name": "...",
            "email": "...",
            "password": "..."
        }}
        Response: {{
            "success": true,
            "message": "User registered successfully"
        }}

        2. Login:
        POST /api/{{website}}/login
        Request body: {{
            "email": "...",
            "password": "..."
        }}
        Response: {{
            "success": true,
            "user_id": 1,
            "message": "Login successful"
        }}

        **JAVASCRIPT STRUCTURE (TEMPLATE TO FOLLOW):**
        ```javascript
        // state
        let state = {{ view: 'shop', products: [], cart: [], wishlist: [], currentProduct: null, user: null }};

        // DOM elements cache
        let app;

        // helper functions
        function setView(view) {{ ... }}
        function render() {{ ... }}
        async function loadProducts() {{ ... }}
        async function loadCart() {{ ... }}
        async function loadWishlist() {{ ... }}
        async function addToCart(productId, quantity) {{ ... }}
        async function addToWishlist(productId) {{ ... }}
        async function viewProduct(productId) {{ ... }}
        function updateCartUI() {{ ... }}

        // initialisation
        document.addEventListener('DOMContentLoaded', () => {{
        app = document.getElementById('app');
        loadProducts();
        loadCart();
        loadWishlist();
        // set up routing
        window.addEventListener('hashchange', handleRouting);
        handleRouting();
        }});
        --- OUTPUT RULES ---
        - Include custom CSS keyframe animations for page transitions.
        - Use Tailwind CSS via CDN in the HTML header for responsiveness.
        - Return ONLY a valid JSON object:
        {{
          "index.html": "...",
          "script.js": "...",
          "styles.css": "..."
        }}
        """

        response = self.generate_code(prompt)
        if not response:
            return {"files": {}, "success": False}
        
        cleaned = self.extract_json(response)
        parsed = None
        
        # Attempt 1: Normal JSON parse
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print("JSON parse failed, using regex fallback...")
            # Attempt 2: Regex extraction
            files = {}
            for key in ["index.html", "script.js", "styles.css"]:
                pattern = rf'"{key}":\s*"((?:[^"\\]|\\.)*)"'
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    content = match.group(1).replace('\\"', '"').replace('\\n', '\n')
                    files[key] = content
            if len(files) == 3:
                parsed = files
        
        if parsed and all(k in parsed for k in ["index.html", "script.js", "styles.css"]):
            saved = self.save_website_files(parsed, slug)
            return {"files": parsed, "success": True, "saved_files": saved, "slug": slug}
        else:
            print("Could not extract valid files from AI response")
            print("Response preview:", response[:300])
            return {"files": {}, "success": False}

ai_generator = WebsiteGenerator()