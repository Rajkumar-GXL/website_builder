import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

class WebsiteGenerator:

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def clean_code(self, text):
        return re.sub(r"```.*?\n|```", "", text, flags=re.DOTALL).strip()

    def extract_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return match.group(0)
            return "{}"
        except:
            return "{}"
    
    def generate_code(self, prompt: str) -> str:
        for _ in range(2):
            try:
                response = self.model.generate_content(prompt)

                if hasattr(response, "text") and response.text:
                    return self.clean_code(response.text)

                if response.candidates:
                    parts = response.candidates[0].content.parts
                    text = "".join([p.text for p in parts if hasattr(p, "text")])
                    return self.clean_code(text)

            except Exception as e:
                print("Gemini Error:", str(e))

        return ""

    def generate_full_application(self, slug, title, category):
        prompt = f"""
        You are the ecommerce website creator. Create an ecommerce applicatiom for modern look and design.
        its should cover all ecom flows like 
        - Home page
        - Product Listing Page (PLP)
        - Product Detail Page (PDP)
        - Add to Cart
        - Wishlist
        - Checkout
        
        Website: {title}
        Slug: {slug}
        Website Variable: "website" (used as path param in APIs)

        ----------------------------------------
        BACKEND API FORMAT (USE EXACTLY)
        ----------------------------------------

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



        ### 5. OUTPUT FORMAT
        Return ONLY a valid JSON object. No prose. No markdown blocks outside the JSON values.
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