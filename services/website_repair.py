# services/website_repair.py
import asyncio
import subprocess
import sys
import json
from pathlib import Path
from services.patches import (
    add_wishlist_remove_button,
    add_footer_if_missing,
    fix_cart_refresh
)
from services.ai_repair import fix_add_to_cart_logic

class WebsiteRepairAgent:
    def __init__(self, generator, sites_base_dir: Path):
        self.generator = generator
        self.sites_base_dir = Path(sites_base_dir)
        self.max_repair_attempts = 2

    async def repair(self, slug: str, title: str, category: str, base_url: str):
        site_dir = self.sites_base_dir / slug
        js_path = site_dir / "script.js"
        html_path = site_dir / "index.html"

        issues = await self._run_tests_subprocess(base_url)
        attempt = 0
        while issues and attempt < self.max_repair_attempts:
            print(f"🔧 Repair attempt {attempt+1}, {len(issues)} issues")
            for issue in issues:
                if issue["fix_type"] == "deterministic":
                    if issue["component"] == "wishlist":
                        add_wishlist_remove_button(js_path)
                    elif issue["component"] == "footer":
                        add_footer_if_missing(html_path, title, category)
                    elif issue["component"] == "cart" and "refresh" in issue["issue"]:
                        fix_cart_refresh(js_path)
                elif issue["fix_type"] == "ai_function":
                    if issue["component"] == "cart":
                        await fix_add_to_cart_logic(js_path, f"/api/{slug}")
            issues = await self._run_tests_subprocess(base_url)
            attempt += 1
        return {"repair_attempted": attempt > 0, "remaining_issues": issues}

    async def _run_tests_subprocess(self, base_url: str):
        """Run test_runner.py in a separate thread using subprocess.run (synchronous)."""
        test_runner = Path(__file__).parent / "test_runner.py"
        
        def run():
            result = subprocess.run(
                [sys.executable, str(test_runner), base_url],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                print(f"Test runner error: {result.stderr}")
                return []
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {result.stdout}")
                return []
        
        return await asyncio.to_thread(run)