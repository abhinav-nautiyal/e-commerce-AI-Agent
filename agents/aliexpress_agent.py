from .ecommerce_agent import EcommerceAgent
from typing import Dict, List, Optional
import logging
import re
import json

class AliExpressAgent(EcommerceAgent):
    def __init__(self):
        super().__init__("aliexpress")
        self.base_url = "https://www.aliexpress.com"
        
    async def login(self, credentials: Dict[str, str]):
        """Login to AliExpress"""
        try:
            await self.page.goto(f"{self.base_url}/login.html")
            
            # Enter email/username
            await self._safe_type("#fm-login-id", credentials["username"])
            await self._safe_type("#fm-login-password", credentials["password"])
            await self._safe_click("button.fm-button")
            
            # Check if login was successful
            try:
                await self.page.wait_for_selector(".user-account", timeout=5000)
                self.logged_in = True
                self._save_cookies("aliexpress_cookies.json")
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to login to AliExpress: {str(e)}")
            return False

    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for products on AliExpress"""
        try:
            # Construct search URL
            search_url = f"{self.base_url}/wholesale?SearchText={query}"
            if filters:
                if filters.get("min_price"):
                    search_url += f"&minPrice={filters['min_price']}"
                if filters.get("max_price"):
                    search_url += f"&maxPrice={filters['max_price']}"
            
            await self.page.goto(search_url)
            
            # Wait for search results
            await self.page.wait_for_selector(".list--gallery--34TropR")
            
            # Extract product information
            products = await self.page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('a[href*="/item/"]').forEach(item => {
                        const card = item.closest('.list--gallery--34TropR');
                        if (card) {
                            const title = card.querySelector('.multi--titleText--nXeOvyr')?.textContent;
                            const price = card.querySelector('.multi--price-sale--U-S0jtj')?.textContent;
                            const productId = item.href.match(/\\d+\\.html/)?.[0]?.replace('.html', '');
                            const rating = card.querySelector('.multi--score-info--tXZHwzz')?.textContent;
                            const image = card.querySelector('img.images--item--3XZa6xf')?.src;
                            
                            if (title && price && productId) {
                                results.push({
                                    id: productId,
                                    title: title,
                                    price: parseFloat(price.replace(/[^0-9.]/g, '')),
                                    rating: rating ? parseFloat(rating) : null,
                                    image_url: image || null
                                });
                            }
                        }
                    });
                    return results;
                }
            """)
            
            return products
            
        except Exception as e:
            logging.error(f"Failed to search AliExpress: {str(e)}")
            return []

    async def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information about a specific AliExpress product"""
        try:
            await self.page.goto(f"{self.base_url}/item/{product_id}.html")
            
            # Wait for product details to load
            await self.page.wait_for_selector(".product-title")
            
            # Extract product details
            details = await self.page.evaluate("""
                () => {
                    return {
                        title: document.querySelector('.product-title')?.textContent.trim(),
                        price: document.querySelector('.product-price-value')?.textContent,
                        description: document.querySelector('.product-description')?.textContent.trim(),
                        rating: document.querySelector('.overview-rating-average')?.textContent,
                        availability: document.querySelector('.product-quantity-tip')?.textContent.trim(),
                        shipping: document.querySelector('.product-shipping-info')?.textContent.trim()
                    }
                }
            """)
            
            details["id"] = product_id
            return details
            
        except Exception as e:
            logging.error(f"Failed to get AliExpress product details: {str(e)}")
            return {}

    async def add_to_cart(self, product_id: str, quantity: int = 1) -> bool:
        """Add a product to the AliExpress shopping cart"""
        try:
            await self.page.goto(f"{self.base_url}/item/{product_id}.html")
            
            # Set quantity if needed
            if quantity > 1:
                await self._safe_type(".next-input input[type='number']", str(quantity))
            
            # Click add to cart button
            await self._safe_click(".add-to-cart-button")
            
            # Verify product was added successfully
            try:
                await self.page.wait_for_selector(".next-dialog-body", timeout=5000)
                success_text = await self.page.evaluate('document.querySelector(".next-dialog-body")?.textContent')
                return "successfully" in (success_text or "").lower()
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to add product to AliExpress cart: {str(e)}")
            return False

    async def place_order(self, shipping_address: Dict[str, str], payment_info: Dict[str, str]) -> Dict:
        """Place an order for items in the cart"""
        try:
            # Go to cart
            await self.page.goto(f"{self.base_url}/shopcart/list")
            
            # Select all items
            await self._safe_click(".select-all-items input")
            
            # Click buy now
            await self._safe_click(".buy-now")
            
            # Fill shipping address if needed
            if await self.page.query_selector(".address-form"):
                await self._safe_type("input[name='contactPerson']", shipping_address["full_name"])
                await self._safe_type("input[name='address']", shipping_address["address_line1"])
                await self._safe_type("input[name='address2']", shipping_address.get("address_line2", ""))
                await self._safe_type("input[name='city']", shipping_address["city"])
                await self._safe_type("input[name='province']", shipping_address["state"])
                await self._safe_type("input[name='zip']", shipping_address["postal_code"])
                await self._safe_type("input[name='mobileNo']", shipping_address["phone"])
                await self._safe_click(".save-address-button")
            
            # Select payment method
            if payment_info.get("method") == "card":
                await self._safe_click(".credit-card-option")
                await self._safe_type("input[name='cardNumber']", payment_info["card_number"])
                await self._safe_type("input[name='cardHolder']", payment_info["name_on_card"])
                await self._safe_type("input[name='expireDate']", payment_info["expiry"])
                await self._safe_type("input[name='cvv']", payment_info["cvv"])
            
            # Place the order
            await self._safe_click(".place-order-button")
            
            # Get order confirmation
            try:
                await self.page.wait_for_selector(".order-success", timeout=10000)
                order_id = await self.page.evaluate('document.querySelector(".order-number")?.textContent')
                return {
                    "success": True,
                    "order_id": order_id.strip() if order_id else None
                }
            except:
                return {
                    "success": False,
                    "error": "Failed to confirm order placement"
                }
                
        except Exception as e:
            logging.error(f"Failed to place AliExpress order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 