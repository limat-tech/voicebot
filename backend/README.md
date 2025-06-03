# Backend - Flask Application

## Setup Instructions

1. Create virtual environment
2. Install dependencies
3. Set up PostgreSQL database
4. Run migrations
5. Start development server

## API Endpoints

Base URL: `http://127.0.0.1:5000/api` (during development)

## Authentication Endpoints (`/auth`)

### 1. User Registration

*   **Endpoint:** `POST /auth/register`
*   **Description:** Registers a new customer.
*   **Request Body (JSON):**
    ```
    {
        "name": "string (required)",
        "email": "string (required, unique email)",
        "password": "string (required)",
        "phone_number": "string (optional)",
        "preferred_language": "string (optional, defaults to 'en')"
    }
    ```
*   **Example Request Body:**
    ```
    {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "securepassword123",
        "phone_number": "555-0100",
        "preferred_language": "en"
    }
    ```
*   **Responses:**
    *   **Success (201 Created):**
        ```
        {
            "message": "User created successfully",
            "customer_id": 123 
        }
        ```
    *   **Error (400 Bad Request - Missing Fields):**
        ```
        {
            "error": "Name, email, and password are required" 
        }
        ```
    *   **Error (400 Bad Request - Email Exists):**
        ```
        {
            "error": "Email already registered"
        }
        ```
    *   **Error (400 Bad Request - Not JSON):**
        ```
        {
            "error": "Request body must be JSON"
        }
        ```
    *   **Error (500 Internal Server Error - DB Issue):**
        ```
        {
            "error": "An error occurred while creating the user."
        }
        ```

---

## Product Endpoints (`/products`)

### 1. List All Active Products

*   **Endpoint:** `GET /products`
*   **Description:** Retrieves a list of all active products.
*   **Query Parameters:** None
*   **Responses:**
    *   **Success (200 OK):**
        ```
        {
            "products": [
                {
                    "product_id": 1,
                    "name_en": "Red Apple",
                    "name_ar": "تفاح أحمر",
                    "description_en": "Fresh and juicy red apples.",
                    "description_ar": "تفاح أحمر طازج وعصيري.",
                    "price": 5.99,
                    "category_id": 1,
                    "brand": "FarmFresh",
                    "stock_quantity": 100,
                    "unit_type": "kg",
                    "image_url": "https://example.com/images/red_apple.jpg"
                },
                // ... more products
            ]
        }
        ```
    *   **Error (500 Internal Server Error):**
        ```
        {
            "error": "An error occurred while fetching products."
        }
        ```

### 2. Search Products

*   **Endpoint:** `GET /products/search`
*   **Description:** Searches for active products based on a query string in either English or Arabic.
*   **Query Parameters:**
    *   `q` (string, required): The search term.
    *   `language` (string, optional, defaults to 'en'): The language to search in ('en' or 'ar').
*   **Example URL:** `http://localhost:5000/api/products/search?q=apple&language=en`
*   **Responses:**
    *   **Success (200 OK):** (Similar structure to List All Products, but filtered)
        ```
        {
            "products": [
                // ... matching products
            ]
        }
        ```
    *   **Error (400 Bad Request - Missing Query Parameter):**
        ```
        {
            "error": "Search query parameter 'q' is required."
        }
        ```
    *   **Error (500 Internal Server Error):**
        ```
        {
            "error": "An error occurred during product search."
        }
        ```
---

## Cart Endpoints (`/cart`)

### 1. Add Item to Cart

*   **Endpoint:** `POST /cart/add`
*   **Description:** Adds a product to the authenticated user's cart or updates quantity if already present.
*   **Authentication:** Required (JWT)
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
    *   `Content-Type: application/json`
*   **Request Body (JSON):**
    ```
    {
        "product_id": "integer (required)",
        "quantity": "integer (optional, defaults to 1)"
    }
    ```
*   **Example Request Body:**
    ```
    {
        "product_id": 1,
        "quantity": 2
    }
    ```
*   **Success Response (200 OK):**
    ```
    {
        "msg": "'Red Apples' (Qty: 2 requested) processed for cart.",
        "cart_item_details": {
            "cart_item_id": 5,
            "product_id": 1,
            "product_name": "Red Apples",
            "updated_quantity_in_cart": 2,
            "cart_id": 3
        }
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (e.g., Missing `product_id`, invalid `quantity`, insufficient stock):
        ```
        { "msg": "Product ID is required." }
        // or
        { "msg": "Insufficient stock for 'Product Name'." }
        ```
    *   `401 Unauthorized`: Token issues.
    *   `404 Not Found` (e.g., Product not found):
        ```
        { "msg": "Product with ID X not found." }
        ```
    *   `500 Internal Server Error`.

### 2. View Cart

*   **Endpoint:** `GET /cart`
*   **Description:** Retrieves the contents of the authenticated user's shopping cart.
*   **Authentication:** Required (JWT)
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
*   **Success Response (200 OK - Cart with items):**
    ```
    {
        "cart_id": 3,
        "customer_id": 1,
        "items": [
            {
                "cart_item_id": 5,
                "product_id": 1,
                "name_en": "Red Apples",
                "name_ar": "تفاح أحمر",
                "price_per_unit": 5.99,
                "quantity": 2,
                "unit_type": "kg",
                "image_url": "https://example.com/images/red_apple.jpg",
                "subtotal": 11.98
            }
            // ... more items
        ],
        "total_price": 11.98
    }
    ```
*   **Success Response (200 OK - Empty Cart):**
    ```
    {
        "cart_id": 3, // Or null
        "msg": "Your shopping cart is empty.",
        "items": [],
        "total_price": 0.0
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Token issues.
    *   `500 Internal Server Error`.

### 3. Update Cart Item Quantity

*   **Endpoint:** `PUT /cart/items/<int:cart_item_id>`
*   **Description:** Updates the quantity of a specific item in the cart. If quantity is 0, the item is removed.
*   **Authentication:** Required (JWT)
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
    *   `Content-Type: application/json`
*   **Request Body (JSON):**
    ```
    {
        "quantity": "integer (required, new desired quantity, >= 0)"
    }
    ```
*   **Example Request Body (Set quantity to 1):**
    ```
    {
        "quantity": 1
    }
    ```
*   **Success Response (200 OK - Quantity Updated):**
    ```
    {
        "msg": "Quantity for cart item ID 5 updated to 1.",
        "cart_item_details": {
            "cart_item_id": 5,
            "product_id": 1,
            "product_name": "Red Apples",
            "new_quantity": 1,
            "cart_id": 3
        }
    }
    ```
*   **Success Response (200 OK - Item Removed due to Quantity 0):**
    ```
    {
        "msg": "Cart item with ID 5 removed as quantity set to 0."
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (e.g., Missing/invalid `quantity`, insufficient stock).
    *   `401 Unauthorized`: Token issues.
    *   `403 Forbidden`: Item not in user's cart.
    *   `404 Not Found`: `cart_item_id` not found.
    *   `500 Internal Server Error`.

### 4. Remove Item from Cart

*   **Endpoint:** `DELETE /cart/items/<int:cart_item_id>`
*   **Description:** Completely removes a specific item from the authenticated user's cart.
*   **Authentication:** Required (JWT)
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
*   **Success Response (200 OK):**
    ```
    {
        "msg": "Cart item with ID 5 removed successfully."
    }
    ```
*   **Error Responses:**
    *   `401 Unauthorized`: Token issues.
    *   `403 Forbidden`: Item not in user's cart.
    *   `404 Not Found`: `cart_item_id` not found.
    *   `500 Internal Server Error`.

### 5. Checkout (Place Order)

*   **Endpoint:** `POST /cart/checkout`
*   **Description:** Converts the user's cart into an order, updates stock, and clears the cart.
*   **Authentication:** Required (JWT)
*   **Request Headers:**
    *   `Authorization: Bearer <access_token>`
    *   `Content-Type: application/json` (Body can be empty `{}` for this version)
*   **Request Body (JSON):**
    ```
    {} // Empty for now
    ```
*   **Success Response (201 Created):**
    ```
    {
        "msg": "Order placed successfully!",
        "order_id": 101,
        "total_amount": 55.99,
        "status": "pending"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request` (e.g., Cart empty, insufficient stock during final check).
        ```
        { "msg": "Your shopping cart is empty. Cannot proceed to checkout." }
        // or
        { "msg": "Checkout process failed.", "error_details": "Insufficient stock for 'Product Name'." }
        ```
    *   `401 Unauthorized`: Token issues.
    *   `500 Internal Server Error`.

---

### Next Steps: Order Endpoints

Future development will include endpoints for:

*   Listing a user's order history.
*   Retrieving details for a specific order.
