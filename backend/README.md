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

(To be documented as we build)
