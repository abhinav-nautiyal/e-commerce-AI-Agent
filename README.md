# E-commerce MCP Server
The E-commerce MCP Server is a FastAPI-based application that provides a unified interface for interacting with multiple e-commerce platforms (Amazon, Flipkart, and AliExpress) through browser automation. This project combines web scraping, browser automation, and RESTful APIs to enable automated e-commerce operations across different platforms.

## Table of Content
- [Project Structure](#Project_Structure)
- [Prerequisites & Installation](#Prerequisites_and_Installation)
- [Usage](#Usage)
- [Technical Details](#Technical_Details)
- [API Endpoints](#API_Endpoints)
- [Features](#Features)

## Project_Structure
```Bash
mcpdemocopy/
├── agents/
│   ├── __init__.py              # Agent module initialization
│   ├── ecommerce_agent.py       # Base e-commerce agent class
│   ├── amazon_agent.py          # Amazon-specific implementation
│   ├── flipkart_agent.py        # Flipkart-specific implementation
│   ├── aliexpress_agent.py      # AliExpress-specific implementation
│   └── agent_factory.py         # Agent factory for platform management
├── static/
│   └── index.html               # Web interface for testing
├── app.py                       # Main FastAPI application
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
└── README.md                    # Project documentation
```

## Prerequisites_and_Installation
### Prerequisites
- Python 3.11 or higher
- pip package manager
- Playwright browsers

### Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/mcpdemocopy.git
cd mcpdemocopy
```
2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Install Playwright browsers:
```bash
playwright install
```

## Usage
### Server Startup
Start the FastAPI server:
```bash
python app.py
```
The server will start on `http://localhost:8000`

### Web Interface
Access the web interface for testing:
```bash
# Open in browser
http://localhost:8000
```

### API Usage
Use the REST API endpoints for programmatic access:
```bash
# Search products
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"platform": "amazon", "query": "laptop"}'

# Get product details
curl -X POST http://localhost:8000/product \
  -H "Content-Type: application/json" \
  -d '{"platform": "amazon", "product_id": "B0CRDCW3Q3"}'
```

## Technical_Details
### Browser Automation
The system uses Playwright for browser automation:
- Headless browser control
- Session management and cookie persistence
- Cross-platform compatibility
- Automated form filling and navigation

### E-commerce Platform Integration
- **Amazon**: Product search, details, cart operations
- **Flipkart**: Indian e-commerce platform support
- **AliExpress**: International marketplace integration

### Architecture Pattern
- **Factory Pattern**: AgentFactory manages platform-specific agents
- **Strategy Pattern**: Different agents implement the same interface
- **Abstract Base Class**: EcommerceAgent defines common interface

## API_Endpoints
### Search Products
```http
POST /search
{
    "platform": "amazon|flipkart|aliexpress",
    "query": "search query",
    "filters": {
        "min_price": 100,
        "max_price": 1000
    }
}
```

### Get Product Details
```http
POST /product
{
    "platform": "amazon|flipkart|aliexpress",
    "product_id": "product_id"
}
```

### Add to Cart
```http
POST /cart/add
{
    "platform": "amazon|flipkart|aliexpress",
    "product_id": "product_id",
    "quantity": 1
}
```

### Place Order
```http
POST /order
{
    "platform": "amazon|flipkart|aliexpress",
    "shipping_address": {
        "full_name": "John Doe",
        "address_line1": "123 Main St",
        "city": "City",
        "state": "State",
        "postal_code": "12345",
        "phone": "1234567890"
    },
    "payment_info": {
        "method": "card",
        "card_number": "4111111111111111",
        "expiry_month": "12",
        "expiry_year": "2025",
        "cvv": "123"
    }
}
```

## Features
### Core Functionality
- ✅ Multi-platform e-commerce integration
- ✅ Product search with price filters
- ✅ Detailed product information retrieval
- ✅ Shopping cart management
- ✅ Order placement with shipping and payment
- ✅ Session management and cookie persistence

### Technical Features
- ✅ FastAPI RESTful API
- ✅ Playwright browser automation
- ✅ Pydantic data validation
- ✅ Comprehensive error handling
- ✅ Web interface for testing
- ✅ Cross-platform compatibility

### Security & Reliability
- ✅ Input validation on all endpoints
- ✅ Safe browser interactions
- ✅ Session isolation per platform
- ✅ Comprehensive logging
- ✅ Graceful error handling
