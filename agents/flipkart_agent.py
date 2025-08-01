from .ecommerce_agent import EcommerceAgent
from typing import Dict, List, Optional
import logging
import re
import json

class FlipkartAgent(EcommerceAgent):
    def __init__(self):
        super().__init__("flipkart")
        self.base_url = "https://www.flipkart.com"
        
    async def login(self, credentials: Dict[str, str]):
        """Login to Flipkart"""
        try:
            await self.page.goto(f"{self.base_url}/account/login")
            
            # Enter mobile number/email
            await self._safe_type("input[class='_2IX_2- VJZDxU']", credentials["username"])
            await self._safe_type("input[type='password']", credentials["password"])
            await self._safe_click("button[type='submit']")
            
            # Check if login was successful
            try:
                await self.page.wait_for_selector("div[class='exehdJ']", timeout=5000)
                self.logged_in = True
                self._save_cookies("flipkart_cookies.json")
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to login to Flipkart: {str(e)}")
            return False

    async def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for products on Flipkart"""
        try:
            # Construct search URL
            search_url = f"{self.base_url}/search?q={query}"
            if filters:
                if filters.get("min_price"):
                    search_url += f"&p%5B%5D=facets.price_range.from%3D{filters['min_price']}"
                if filters.get("max_price"):
                    search_url += f"&p%5B%5D=facets.price_range.to%3D{filters['max_price']}"
            
            await self.page.goto(search_url)
            
            # Wait for search results
            await self.page.wait_for_selector("div[class='_1AtVbE col-12-12']")
            
            # Extract product information
            products = await self.page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll("div[class='_1AtVbE col-12-12']").forEach(item => {
                        const title = item.querySelector("div[class='_4rR01T']")?.textContent;
                        const price = item.querySelector("div[class='_30jeq3 _1_WHN1']")?.textContent;
                        const link = item.querySelector("a[class='_1fQZEK']")?.href;
                        const rating = item.querySelector("div[class='_3LWZlK']")?.textContent;
                        const image = item.querySelector("img[class='_396cs4']")?.src;
                        
                        if (title && price && link) {
                            const id = link.split("pid=")[1]?.split("&")[0];
                            results.push({
                                id: id,
                                title: title,
                                price: parseFloat(price.replace(/[^0-9.]/g, "")),
                                rating: rating ? parseFloat(rating) : null,
                                image_url: image || null
                            });
                        }
                    });
                    return results;
                }
            """)
            
            return products
            
        except Exception as e:
            logging.error(f"Failed to search Flipkart: {str(e)}")
            return []

    async def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information about a specific Flipkart product"""
        try:
            await self.page.goto(f"{self.base_url}/p/{product_id}")
            
            # Wait for product details to load
            await self.page.wait_for_selector("span[class='B_NuCI']")
            
            # Extract product details
            details = await self.page.evaluate("""
                () => {
                    return {
                        title: document.querySelector("span[class='B_NuCI']")?.textContent.trim(),
                        price: document.querySelector("div[class='_30jeq3 _16Jk6d']")?.textContent,
                        description: document.querySelector("div[class='_1mXcCf RmoJUa']")?.textContent.trim(),
                        rating: document.querySelector("div[class='_3LWZlK']")?.textContent,
                        availability: document.querySelector("div[class='_16FRp0']")?.textContent.trim(),
                        highlights: Array.from(document.querySelectorAll("li[class='_21Ahn-']")).map(li => li.textContent.trim())
                    }
                }
            """)
            
            details["id"] = product_id
            return details
            
        except Exception as e:
            logging.error(f"Failed to get Flipkart product details: {str(e)}")
            return {}

    async def add_to_cart(self, product_id: str, quantity: int = 1) -> bool:
        """Add a product to the Flipkart shopping cart"""
        try:
            await self.page.goto(f"{self.base_url}/p/{product_id}")
            
            # Click add to cart button
            await self._safe_click("button._2KpZ6l._2U9uOA._3v1-ww")
            
            # Verify product was added successfully
            try:
                await self.page.wait_for_selector("div._2sKwjB", timeout=5000)
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Failed to add product to Flipkart cart: {str(e)}")
            return False

    async def place_order(self, shipping_address: Dict[str, str], payment_info: Dict[str, str]) -> Dict:
        """Place an order for items in the cart"""
        try:
            # Go to cart
            await self.page.goto(f"{self.base_url}/viewcart")
            
            # Click place order button
            await self._safe_click("button._2KpZ6l._2ObVJD._3AWRsL")
            
            # Fill shipping address if needed
            if await self.page.query_selector("button._2KpZ6l._1uR9yB._3dESVI"):
                await self._safe_click("button._2KpZ6l._1uR9yB._3dESVI")
                await self._safe_type("input[name='name']", shipping_address["full_name"])
                await self._safe_type("input[name='phone']", shipping_address["phone"])
                await self._safe_type("input[name='pincode']", shipping_address["postal_code"])
                await self._safe_type("input[name='addressLine1']", shipping_address["address_line1"])
                await self._safe_type("input[name='addressLine2']", shipping_address["address_line2"])
                await self._safe_type("input[name='city']", shipping_address["city"])
                await self._safe_type("input[name='state']", shipping_address["state"])
                await self._safe_click("button._2KpZ6l._1JDhFS._1o0c4q")
            
            # Select payment method
            if payment_info.get("method") == "card":
                await self._safe_click("div._3AWRsL")  # Credit/Debit card option
                await self._safe_type("input[name='cardNumber']", payment_info["card_number"])
                await self._safe_type("input[name='expiryMonth']", payment_info["expiry_month"])
                await self._safe_type("input[name='expiryYear']", payment_info["expiry_year"])
                await self._safe_type("input[name='cvv']", payment_info["cvv"])
                await self._safe_click("button._2KpZ6l._1seccl._3AWRsL")
            
            # Place the order
            await self._safe_click("button._2KpZ6l._2ObVJD._3AWRsL")
            
            # Get order confirmation
            try:
                await self.page.wait_for_selector("div._3-wDH3", timeout=10000)
                order_id = await self.page.evaluate('document.querySelector("div._3-wDH3")?.textContent')
                return {
                    "success": True,
                    "order_id": re.search(r"OD\d+", order_id).group(0) if order_id else None
                }
            except:
                return {
                    "success": False,
                    "error": "Failed to confirm order placement"
                }
                
        except Exception as e:
            logging.error(f"Failed to place Flipkart order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 