from .ecommerce_agent import EcommerceAgent
from typing import Dict, List, Optional
import logging
import re
import json

class AmazonAgent(EcommerceAgent):
    def __init__(self):
        super().__init__("amazon")
        self.base_url = "https://www.amazon.com"
        
    async def login(self, credentials: Dict[str, str]):
        """Login to Amazon"""
        try:
            await self.page.goto(f"{self.base_url}/signin")
            
            # Enter email
            await self._safe_type("#ap_email", credentials["email"])
            await self._safe_click("#continue")
            
            # Enter password
            await self._safe_type("#ap_password", credentials["password"])
            await self._safe_click("#signInSubmit")
            
            # Check if login was successful
            try:
                await self.page.wait_for_selector("#nav-link-accountList-nav-line-1", timeout=5000)
                self.logged_in = True
                self._save_cookies("amazon_cookies.json")
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to login to Amazon: {str(e)}")
            return False

    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for products on Amazon"""
        try:
            # Construct search URL with filters
            search_url = f"{self.base_url}/s?k={query}"
            if filters:
                if filters.get("min_price"):
                    search_url += f"&low-price={filters['min_price']}"
                if filters.get("max_price"):
                    search_url += f"&high-price={filters['max_price']}"
                
            await self.page.goto(search_url)
            
            # Wait for search results
            await self.page.wait_for_selector("[data-component-type='s-search-result']")
            
            # Extract product information
            products = await self.page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll("[data-component-type='s-search-result']").forEach(item => {
                        const title = item.querySelector("h2 span")?.textContent;
                        const price = item.querySelector(".a-price-whole")?.textContent;
                        const asin = item.getAttribute("data-asin");
                        const rating = item.querySelector(".a-icon-star-small .a-icon-alt")?.textContent;
                        const image = item.querySelector("img.s-image")?.src;
                        
                        if (title && price && asin) {
                            results.push({
                                id: asin,
                                title: title,
                                price: parseFloat(price.replace(/[^0-9.]/g, "")),
                                rating: rating ? parseFloat(rating.split(" ")[0]) : null,
                                image_url: image || null
                            });
                        }
                    });
                    return results;
                }
            """)
            
            return products
            
        except Exception as e:
            logging.error(f"Failed to search Amazon: {str(e)}")
            return []

    async def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information about a specific Amazon product"""
        try:
            await self.page.goto(f"{self.base_url}/dp/{product_id}")
            
            # Wait for product details to load
            await self.page.wait_for_selector("#productTitle")
            
            # Extract product details
            details = await self.page.evaluate("""
                () => {
                    return {
                        title: document.querySelector("#productTitle")?.textContent.trim(),
                        price: document.querySelector(".a-price-whole")?.textContent,
                        description: document.querySelector("#productDescription")?.textContent.trim(),
                        rating: document.querySelector("#acrPopover")?.getAttribute("title"),
                        availability: document.querySelector("#availability")?.textContent.trim(),
                        features: Array.from(document.querySelectorAll("#feature-bullets li")).map(li => li.textContent.trim())
                    }
                }
            """)
            
            details["id"] = product_id
            return details
            
        except Exception as e:
            logging.error(f"Failed to get Amazon product details: {str(e)}")
            return {}

    async def add_to_cart(self, product_id: str, quantity: int = 1) -> bool:
        """Add a product to the Amazon shopping cart"""
        try:
            await self.page.goto(f"{self.base_url}/dp/{product_id}")
            
            # Set quantity if needed
            if quantity > 1:
                await self._safe_click("#a-autoid-0-announce")
                await self._safe_click(f"#quantity_{quantity}")
            
            # Click add to cart button
            await self._safe_click("#add-to-cart-button")
            
            # Verify product was added successfully
            try:
                await self.page.wait_for_selector("#nav-cart-count", timeout=5000)
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to add product to Amazon cart: {str(e)}")
            return False

    async def place_order(self, shipping_address: Dict[str, str], payment_info: Dict[str, str]) -> Dict:
        """Place an order for items in the cart"""
        try:
            # Go to cart
            await self.page.goto(f"{self.base_url}/gp/cart/view.html")
            
            # Proceed to checkout
            await self._safe_click("#sc-buy-box-ptc-button")
            
            # Fill shipping address if needed
            if await self.page.query_selector("#add-new-address-popover-link"):
                await self._safe_click("#add-new-address-popover-link")
                await self._safe_type("#address-ui-widgets-enterAddressFullName", shipping_address["full_name"])
                await self._safe_type("#address-ui-widgets-enterAddressLine1", shipping_address["address_line1"])
                await self._safe_type("#address-ui-widgets-enterAddressCity", shipping_address["city"])
                await self._safe_type("#address-ui-widgets-enterAddressStateOrRegion", shipping_address["state"])
                await self._safe_type("#address-ui-widgets-enterAddressPostalCode", shipping_address["postal_code"])
                await self._safe_type("#address-ui-widgets-enterAddressPhoneNumber", shipping_address["phone"])
                await self._safe_click("#address-ui-widgets-form-submit-button")
            
            # Select payment method if needed
            if payment_info.get("new_card"):
                await self._safe_click("#pp-YqiDWv-126")  # Add payment method button
                # Fill card details
                await self._safe_type("#pp-YqiDWv-16", payment_info["card_number"])
                await self._safe_type("#pp-YqiDWv-18", payment_info["name_on_card"])
                await self._safe_type("#pp-YqiDWv-21", payment_info["expiry"])
                await self._safe_type("#pp-YqiDWv-23", payment_info["cvv"])
                await self._safe_click("#pp-YqiDWv-64")  # Use this payment method button
            
            # Place the order
            await self._safe_click("#submitOrderButtonId")
            
            # Get order confirmation
            try:
                await self.page.wait_for_selector(".a-color-success", timeout=10000)
                order_id = await self.page.evaluate('document.querySelector(".a-color-success")?.textContent')
                return {
                    "success": True,
                    "order_id": re.search(r"#(\d{3}-\d{7}-\d{7})", order_id).group(1) if order_id else None
                }
            except:
                return {
                    "success": False,
                    "error": "Failed to confirm order placement"
                }
                
        except Exception as e:
            logging.error(f"Failed to place Amazon order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 