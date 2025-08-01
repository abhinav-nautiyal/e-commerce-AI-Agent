# E-commerce MCP Server

A FastAPI-based server that provides a unified interface for interacting with multiple e-commerce platforms (Amazon and Flipkart) through browser automation.

## Features

- Search products across multiple e-commerce platforms
- Get detailed product information
- Add products to cart
- Place orders with shipping and payment information
- Session management and cookie persistence
- Automated browser interaction using Playwright

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Search Products
```http
POST /search
{
    "platform": "amazon|flipkart",
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
    "platform": "amazon|flipkart",
    "product_id": "product_id"
}
```

### Add to Cart
```http
POST /cart/add
{
    "platform": "amazon|flipkart",
    "product_id": "product_id",
    "quantity": 1
}
```

### Place Order
```http
POST /order
{
    "platform": "amazon|flipkart",
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

## Error Handling

The server returns appropriate HTTP status codes and error messages:

- 200: Successful operation
- 400: Invalid request parameters
- 500: Server error or e-commerce platform error

## Security Considerations

- The server uses session management to maintain login state
- Sensitive information (cookies, payment details) is not persisted
- Browser automation is done in headless mode
- Input validation is performed on all endpoints

## Development

The codebase is organized as follows:

- `app.py`: Main FastAPI application and API endpoints
- `agents/`: E-commerce platform-specific implementations
  - `ecommerce_agent.py`: Base agent class
  - `amazon_agent.py`: Amazon-specific implementation
  - `flipkart_agent.py`: Flipkart-specific implementation
  - `agent_factory.py`: Factory class for managing agents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
