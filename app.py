from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
from agents import AgentFactory
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-commerce MCP Server")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class SearchRequest(BaseModel):
    platform: str
    query: str
    filters: Optional[Dict] = None

class ProductRequest(BaseModel):
    platform: str
    product_id: str

class CartRequest(BaseModel):
    platform: str
    product_id: str
    quantity: int = 1

class OrderRequest(BaseModel):
    platform: str
    shipping_address: Dict[str, str]
    payment_info: Dict[str, str]

@app.get("/")
async def root():
    """Serve the web interface"""
    return FileResponse("static/index.html")

@app.post("/search")
async def search_products(request: SearchRequest):
    """Search for products on the specified platform"""
    try:
        agent = await AgentFactory.get_agent(request.platform)
        results = await agent.search(request.query, request.filters)
        return {
            "status": "success",
            "platform": request.platform,
            "results": results
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/product")
async def get_product_details(request: ProductRequest):
    """Get detailed information about a specific product"""
    try:
        agent = await AgentFactory.get_agent(request.platform)
        details = await agent.get_product_details(request.product_id)
        return {
            "status": "success",
            "platform": request.platform,
            "product": details
        }
    except Exception as e:
        logger.error(f"Product details error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cart/add")
async def add_to_cart(request: CartRequest):
    """Add a product to the shopping cart"""
    try:
        agent = await AgentFactory.get_agent(request.platform)
        success = await agent.add_to_cart(request.product_id, request.quantity)
        return {
            "status": "success" if success else "error",
            "platform": request.platform,
            "message": "Product added to cart" if success else "Failed to add product to cart"
        }
    except Exception as e:
        logger.error(f"Add to cart error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/order")
async def place_order(request: OrderRequest):
    """Place an order on the specified platform"""
    try:
        agent = await AgentFactory.get_agent(request.platform)
        result = await agent.place_order(request.shipping_address, request.payment_info)
        return {
            "status": "success" if result["success"] else "error",
            "platform": request.platform,
            "order_id": result.get("order_id"),
            "error": result.get("error")
        }
    except Exception as e:
        logger.error(f"Order placement error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when shutting down"""
    await AgentFactory.close_all()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)