# Import necessary Libraries
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
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

        self.client = genai.Client(api_key=api_key)

        self.model_name = "gemini-3-flash-preview"

        self.cache_name = None

        # self._init_cache()

    def _init_cache(self):
        static_prompt = """
        You are an expert full-stack web developer and UI/UX designer.
        Your task is to generate a complete, production-ready static website for a given business idea.
        Follow all the rules, API specs, and JavaScript structure described below.
        """
        cache = self.client.caches.create(
            model=self.model_name,
            contents=[types.Content(parts=[types.Part(text=static_prompt)])],
            ttl="3600s"
        )
        self.cache_name = cache.name
        
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
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            return json_str
        except Exception as e:
            print(f"JSON extraction error: {e}")
            return "{}"
    
    # Function to generate website application.
    def generate_code(self, prompt: str, is_json: bool = True):
        for attempt in range(2):
            try:
                config_kwargs = {
                    "temperature": 0.85,
                    "top_p": 0.95,
                }
                if is_json:
                    config_kwargs["response_mime_type"] = "application/json"
                
                config = types.GenerateContentConfig(**config_kwargs)
                if self.cache_name:
                    config.cached_content = self.cache_name

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                # Extract token usage
                usage = {}
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    um = response.usage_metadata
                    usage = {
                        "prompt_tokens": um.prompt_token_count,
                        "completion_tokens": um.candidates_token_count,
                        "total_tokens": um.total_token_count,
                        "cached_tokens": getattr(um, 'cached_content_token_count', 0)
                    }
                if response.text:
                    return self.clean_code(response.text), usage
                if response.candidates:
                    parts = response.candidates[0].content.parts
                    text = "".join(p.text for p in parts if hasattr(p, "text"))
                    return self.clean_code(text), usage
            except Exception as e:
                print(f"Gemini attempt {attempt+1} error: {e}")
        return "", {}

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
        - Color direction: {chosen_color_direction} → generate 5 CSS variables (primary, secondary, accent, background, text)
        - Test that all text is legible and professional-looking.
        
        CRITICAL RULES (MUST FOLLOW):
        - Every function must be implemented exactly as described.
        - The website must work without errors – no undefined variables, no missing event listeners.
        - Use the API responses for all data – DO NOT hardcode products or images.
        - Escape double quotes inside strings with backslash.
        - No trailing commas in JSON.
        - All JavaScript must be self-contained and initialised after DOMContentLoaded.
        - The `slug` must be used to construct all API URLs: const API_BASE = `/api/{slug}`;

        **REQUIRED FUNCTIONALITY (ALL MUST WORK):**
        1. Data comes from backend APIs.
        2. All views: home, shop, product detail (PDP), profile, cart, wishlist, checkout, login/register modal.
        3. Use Tailwind CSS CDN + custom CSS for unique styling.
        
        1. **PRODUCTS**  
        - Use the API response from `${{API_BASE}}/products`. 
        - Do NOT create mock products manually.
        - Always fetch products from API and render dynamically.
          Product mapping:  
          - product.id → use as unique identifier
          - product.title → display title
          - product.special_price → display price
          - product.image_url → use for images

        2. **WISHLIST**  
        - Every product card must include a heart icon or "♡ Wishlist" button that calls `toggleWishlist(id)`. 
        - the wishlist button should be filled with red color when the product is added to the wishlist.
        - adding and deleting from wishlist should be reflected in the wishlist page.
        - Implement `login(email, password)` and `register(name, email, password)` using the API endpoints.
        - Each wishlist item must have a **"Remove"** button or a trash icon.
        - The wishlist page should update immediately without a page reload.
        - If the wishlist is empty, show a message: "Your wishlist is empty."
        
        3. **LOGIN/REGISTER BUTTON**  
        - Add a **"Login/Register"** button in the header (next to cart).
        - Create a modal with two tabs: Login and Register.
        - Implement `login(email, password)` and `register(name, email, password)` using `${{API_BASE}}/login` and `${{API_BASE}}/register`.

        4. **HIGH CONTRAST & READABILITY**      
        - Product titles and prices must be `#1a1a1a` (dark gray) on light backgrounds, or `#f5f5f5` on dark backgrounds.  
        - Navigation links must have a contrast ratio ≥ 4.5:1.  
        - Primary CTA buttons (Shop Now, Add to Cart) must use a **highly visible accent color** (e.g., `#ff6600`, `#00c853`, `#2196f3`).  
        - On screens < 768px, collapse the navigation menu into a hamburger menu (use JavaScript to toggle). Keep cart and login icons visible.
        
        5. **FOOTER (MANDATORY)**     
        - Create a `<footer>` element at the bottom of every page.
        - The footer must be visually consistent with the overall design (use the same color scheme).
        - Font Should be professional and readable.
        - Include:
            * Brand name: "{title}"
            * Tagline related to the category "{category}" (e.g., "Best {category} deals").
            * Useful links: Home, Shop, About Us, Contact, Privacy Policy, Terms of Service.
            * Social media icons (use Font Awesome CDN or simple text links).
            * Copyright notice with current year (auto-updating using JavaScript).
        - The footer should be responsive (stack on mobile).
        - Do not hardcode placeholder text – use the actual brand and category.
        - Use `<hr>` or border-top to separate from main content.

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

        response_text, token_usage = self.generate_code(prompt)   
        if not response_text:
            return {"files": {}, "success": False, "token_usage": token_usage}  
        
        cleaned = self.extract_json(response_text)
        parsed = None
        
        # Attempt 1: Normal JSON parse
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print("JSON parse failed, using regex fallback...")
            files = {}
            for key in ["index.html", "script.js", "styles.css"]:
                pattern = rf'"{key}":\s*"((?:[^"\\]|\\.)*)"'
                match = re.search(pattern, response_text, re.DOTALL)   # use response_text
                if match:
                    content = match.group(1).replace('\\"', '"').replace('\\n', '\n')
                    files[key] = content
            if len(files) == 3:
                parsed = files

        if parsed and all(k in parsed for k in ["index.html", "script.js", "styles.css"]):
            saved = self.save_website_files(parsed, slug)
            print(f"\nToken usage for {slug}:")
            print(f"Prompt tokens: {token_usage.get('prompt_tokens', 0)}")
            print(f"Completion tokens: {token_usage.get('completion_tokens', 0)}")
            print(f"Total tokens: {token_usage.get('total_tokens', 0)}")
            if token_usage.get('cached_tokens'):
                print(f"Cached tokens: {token_usage['cached_tokens']}")
            return {
                "files": parsed,
                "success": True,
                "saved_files": saved,
                "slug": slug,
                "token_usage": token_usage
            }
        else:
            print("Could not extract valid files from AI response")
            print("Response preview:", response_text[:300])
            return {"files": {}, "success": False, "token_usage": token_usage}

ai_generator = WebsiteGenerator()