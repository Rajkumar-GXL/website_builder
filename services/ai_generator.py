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
        return re.sub(r"```.*?\n|```", "", text, flags=re.DOTALL).strip()

    # Function to extract the json file.
    def extract_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group(0)
            return "{}"
        except:
            return "{}"
    
    # Function to generate website application.
    def generate_code(self, prompt: str) -> str:
        for _ in range(2):
            try:
                # Add higher temperature to increase creative variability (uniqueness)
                response = self.model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.95, "top_p": 0.95}
                )

                if hasattr(response, "text") and response.text:
                    return self.clean_code(response.text)

                if response.candidates:
                    parts = response.candidates[0].content.parts
                    text = "".join([p.text for p in parts if hasattr(p, "text")])
                    return self.clean_code(text)

            except Exception as e:
                print("Gemini Error:", str(e))

        return ""

    # Function to generate the full Application
    def generate_full_application(self, slug, title, category):
        design_systems = [
            {
                "style": "Glassmorphism (Frosted glass cards, neon accents, blurred backgrounds)",
                "nav": "Centered top navigation bar with animated underline hover effects and logo in center",
                "layout": "Bento Grid (Modular blocks of varying sizes for products)"
            },
            {
                "style": "High-Contrast Brutalism (Heavy 4px black borders, bold primary colors, sharp edges)",
                "nav": "Sticky top bar with hamburger menu that reveals a full-screen mega menu",
                "layout": "Asymmetric split-screen (Fixed hero on left, scrolling products on right)"
            },
            {
                "style": "Modern Swiss Minimalism (Massive typography, 0.5pt thin lines, monochromatic)",
                "nav": "Floating circular menu button (FAB) that expands into a radial navigation wheel",
                "layout": "Horizontal scrolling product gallery (Side-scrolling on desktop)"
            },
            {
                "style": "Neubrutalism (Bold colors, rough edges, quirky illustrations, playful vibe)",
                "nav": "Top rail with segmented pill buttons that slide horizontally on scroll",
                "layout": "Masonry grid with staggered card heights"
            },
            {
                "style": "Cyberpunk/Neon Noir (Dark mode with neon glows, scanlines, futuristic elements)",
                "nav": "Bottom-anchored control panel that slides up/down with touch/mouse drag",
                "layout": "Hexagonal grid product display with hover animations"
            },
            {
                "style": "Organic/Biophilic Design (Curved shapes, nature colors, flowing gradients)",
                "nav": "Radial menu that blooms from a leaf-shaped button in corner",
                "layout": "Waterfall layout with organic card shapes (non-rectangular)"
            },
            {
                "style": "Retro/Vaporwave (Synthwave gradients, chrome effects, 80s aesthetic)",
                "nav": "Arcade-style top bar with pixelated icons and CRT scanline effect",
                "layout": "Grid with perspective tilt (3D-like product showcase)"
            },
            {
                "style": "Minimalist/Whitespace Heavy (Breathing room, fine details, elegant typography)",
                "nav": "Progressive disclosure - nav appears only on scroll-up, hides on scroll-down",
                "layout": "Single column with parallax scrolling sections"
            },
            {
                "style": "Abstract/Experimental (Broken grid, overlapping elements, asymmetry)",
                "nav": "Anchored to mouse cursor, follows pointer with delay, collapses on click",
                "layout": "Collage-style overlapping cards with rotation transforms"
            },
            {
                "style": "Luxury/Opulent (Gold accents, rich textures, serif typography, slow animations)",
                "nav": "Left-aligned vertical marquee that scrolls menu items continuously",
                "layout": "Grid with featured product taking 2x size spotlight"
            }
        ]
        
        hero_styles = [
            "Full-screen cinematic hero with large parallax overlapping text",
            "Split-screen design: sticky left text, scrolling right collage of images",
            "3D interactive placeholder centered with bold, elegant typography",
            "Typographic hero using massive structural text without traditional photos",
            "Grid-based hero: staggered masonry cards that reveal on load"
        ]
        
        typography_styles = [
            "Grotesque Sans-serif headers (impactful) + Humanist Sans-serif body (readable)",
            "High-contrast elegant Serif (luxury) + geometric Sans-serif body",
            "Monospace retro-computer type + clean sans-serif for regular text",
            "Chunky Y2K aesthetic typefaces with outline effects + simple sans-serif",
            "Ultra-thin minimalist Sans-serif with extremely large Tracking/Letter-spacing"
        ]

        interaction_styles = [
            "Magnetic buttons, custom cursor trails, fluid spring hover states",
            "Parallax scrolling image reveals and staggered text entry animations",
            "Brutalist marquee scrolling text, harsh flashing hovers, inverted colors",
            "Soft glassmorphism fade-ins, gentle floating elements, layered blur effects",
            "Page transitions with circular SVG masks and morphing containers"
        ]

        design = random.choice(design_systems)
        hero = random.choice(hero_styles)
        typography = random.choice(typography_styles)
        interaction = random.choice(interaction_styles)
        
        prompt = f"""
        Act as a Senior Creative Developer. Build a HIGH-END, PRODUCTION-READY Ecommerce Frontend for:
        - BRAND: {title}
        - DOMAIN: {category}
        - SLUG: {slug}

        --- MANDATORY DESIGN SYSTEM ---
        1. THEME: {design['style']}
        2. NAVIGATION: {design['nav']}
        3. GRID: {design['layout']}
        4. HERO SECTION: {hero}
        5. TYPOGRAPHY: {typography}
        6. MICRO-INTERACTIONS: {interaction}
        7. COLOR PALETTE: Generate a completely UNIQUE 5-color palette (Primary, Secondary, Surface, Accent, Text) avoiding generic colors.
        
        --- MANDATORY FRONTEND LOGIC (script.js) ---
        1. API BASE: `const API_BASE = '/api/{slug}';`
        2. STATE: Use a global `state = {{ products: [], cart: [], view: 'home' }}`.
        3. RE-RENDERING: Every time state changes, call a `render()` function that updates the UI without page reload.
        4. DYNAMIC FEATURES:
           - On page load, fetch `${{API_BASE}}/products`.
           - Implement `addToCart(id)` and `placeOrder()` with fetch calls.
           - Implement `switchView(viewName)` to toggle visibility between Home, Shop, and Checkout sections.
        5. PERSISTENCE: Save/Load the cart to `localStorage`.


        --- BACKEND MAPPING ---
        Ensure all fetch calls strictly use: `${{API_BASE}}/products`, `${{API_BASE}}/cart`, `${{API_BASE}}/checkout`.

        --- OUTPUT ---
        Return ONLY valid JSON.
        {{
          "index.html": "...",
          "script.js": "...",
          "styles.css": "..."
        }}
        --- OUTPUT FORMAT ---
        Return ONLY valid JSON.
        {{
          "index.html": "...",
          "script.js": "...",
          "styles.css": "..."
        }}

        --- MANDATORY DESIGN UNIQUENESS ---
        1. Create a unique Header/Footer layout (e.g., side-nav, bottom-dock, or floating).
        2. Generate a custom Color Palette and Font Pairing in 'styles.css'.
        3. Use {category}-specific terminology in the UI.

        --- MANDATORY FUNCTIONALITY (JAVASCRIPT) ---
        The 'script.js' MUST implement these features using 'fetch' to your API:
        1. CONSTANT: Define `const API_BASE = '/api/{slug}';` at the top.
        2. LOADING: On page load, fetch `${{API_BASE}}/products` and render them.
        3. CART: Functions `addToCart(id)` and `removeFromCart(id)` must call the POST/DELETE endpoints.
        4. WISHLIST: Functions for `POST/DELETE ${{API_BASE}}/wishlist/${{id}}`.
        5. STATE: Keep a local `cartCount` and update the UI header when items are added.
        6. ROUTING: Use a simple hidden/show logic or URL params to switch between Home, PLP, and Checkout views.

        --- BACKEND API REFERENCE ---
        Follow these exact paths:
        - GET ${{API_BASE}}/products
        - GET ${{API_BASE}}/product/{{id}}
        - GET/POST/DELETE ${{API_BASE}}/cart
        - GET/POST/DELETE ${{API_BASE}}/wishlist
        - POST ${{API_BASE}}/login
        - POST ${{API_BASE}}/checkout

        OUTPUT FORMAT:
        Return ONLY valid JSON.
        {{
          "index.html": "...",
          "script.js": "...",
          "styles.css": "..."
        }}
        
        REQUIREMENTS FOR EXTREME UNIQUENESS:
        1. DESIGN SYSTEM: Define an extremely unique color palette and font pairing that deeply fits the '{category}' domain but has a distinct aggressive aesthetic. 
        2. CUSTOM COMPONENTS: The Header and Footer must be entirely un-orthodox and custom-built for this exact vibe. NO generic Bootstrap/Tailwind standard navbars. Try floating elements, bottom docks, vertical sidebars, or circular radial menus as requested.
        3. DOMAIN FEATURES: Invent one highly unique UI interaction or feature specific to '{category}' (e.g., if 'Art', an AR preview button; if 'Tech', a terminal-like filter console).
        4. CSS CRAFTSMANSHIP: Do not rely solely on basic Tailwind utilities. Include advanced CSS styling, custom scrollbars, text selection colors, and clip-paths to break out of the box.

        COVER THESE FLOWS:
        - Home (with a unique hero section based on {title})
        - PLP, PDP, Cart, Wishlist, Checkout.
        
        Website: {title}
        Slug: {slug}
        Website Variable: "website" (used as path param in APIs)

        --- BACKEND MAPPING ---
        
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
            print("EMPTY AI RESPONSE")
            return {"files": {}}

        cleaned = self.extract_json(response)

        try:
            parsed = json.loads(cleaned)
            return {"files": parsed}
        except Exception as e:
            print("JSON ERROR:", e)
            print("RAW:", response)
            return {"files": {}}
        

ai_generator = WebsiteGenerator()