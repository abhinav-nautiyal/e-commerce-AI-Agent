from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from playwright.async_api import async_playwright
import logging
import json
import os

class EcommerceAgent(ABC):
    def __init__(self, platform: str):
        self.platform = platform
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
        
    async def initialize(self):
        """Initialize the browser and create a new context"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()

    @abstractmethod
    async def login(self, credentials: Dict[str, str]):
        """Login to the e-commerce platform"""
        pass

    @abstractmethod
    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for products"""
        pass

    @abstractmethod
    async def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information about a specific product"""
        pass

    @abstractmethod
    async def add_to_cart(self, product_id: str, quantity: int = 1) -> bool:
        """Add a product to the shopping cart"""
        pass

    @abstractmethod
    async def place_order(self, shipping_address: Dict[str, str], payment_info: Dict[str, str]) -> Dict:
        """Place an order for items in the cart"""
        pass

    async def _safe_click(self, selector: str, timeout: int = 5000):
        """Safely click an element with retry logic"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            await element.click()
            return True
        except Exception as e:
            logging.error(f"Failed to click element {selector}: {str(e)}")
            return False

    async def _safe_type(self, selector: str, text: str, timeout: int = 5000):
        """Safely type text into an input field"""
        try:
            element = await self.page.wait_for_selector(selector, timeout=timeout)
            await element.fill(text)
            return True
        except Exception as e:
            logging.error(f"Failed to type into element {selector}: {str(e)}")
            return False

    def _save_cookies(self, filename: str):
        """Save session cookies to a file"""
        if self.context:
            cookies = self.context.cookies()
            with open(filename, 'w') as f:
                json.dump(cookies, f)

    async def _load_cookies(self, filename: str):
        """Load session cookies from a file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies) 