# Vocery - Voice-Assisted Grocery Shopping Backend

This repository contains the backend services for the Vocery application, a bilingual (English and Arabic) voice-assisted grocery shopping platform[1]. The backend is built using Flask and powers the core e-commerce functionalities, including user management, product catalog, shopping cart, orders, and the AI pipeline for voice command processing[2].

## System Architecture

The backend system is composed of several key services working together[2]:
*   **Flask Application**: The main web server that provides the RESTful API for all e-commerce operations. It handles business logic and communicates with the database and other AI services.
*   **PostgreSQL Database**: The relational database used to store all application data, including customer information, products, carts, and orders[3].
*   **Rasa NLU**: Used for Natural Language Understanding. Two separate Rasa servers are run to handle intent and entity recognition for English and Arabic commands[2].
*   **Coqui TTS**: The Text-to-Speech engine responsible for converting textual responses from the server into audible speech for the user[2].

## Setup Instructions

These instructions will guide you through setting up the backend services on a Windows machine.

### 1. Prerequisites
Before you begin, ensure you have the following installed:
*   Python 3.8+
*   PostgreSQL
*   Git

### 2. Clone the Repository
Start by cloning the project repository to your local machine.
```bash
git clone 
cd backend
```

### 3. Create and Configure Virtual Environments
This project requires two separate Python virtual environments to manage dependencies without conflicts. One is for the main Flask application (`.venv`), and the other is specifically for the Coqui TTS service (`tts-env`), which has a large and distinct set of libraries.

**What is a virtual environment?** It's an isolated Python environment that allows you to install packages for a specific project without affecting other projects or your system's global Python installation. It's a standard practice in professional development to ensure consistency and avoid dependency issues.

**a. Main Application Environment**
```powershell
# Create the virtual environment for the Flask API
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate

# Install the required packages from requirements-API.txt
pip install -r requirements-API.txt
```

**b. Text-to-Speech (TTS) Environment**
Open a **new, separate terminal** for this step.
```powershell
# Create the virtual environment for the TTS service
python -m venv tts-env

# Activate the TTS virtual environment
.\tts-env\Scripts\activate

# Install the required packages from requirements-tts.txt
pip install -r requirements-tts.txt
```
**Note:** You will now have two terminals open. Keep the first one (`.venv` activated) for running the Flask server and Rasa models, and the second one (`tts-env` activated) for running the TTS server.

### 4. Set Up PostgreSQL Database
You need to create a database and a user for the application.
```sql
-- Connect to PostgreSQL using psql or a GUI tool like pgAdmin
CREATE DATABASE vocery;
CREATE USER vocery_user WITH PASSWORD 'your_secure_password';
ALTER ROLE vocery_user SET client_encoding TO 'utf8';
ALTER ROLE vocery_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vocery_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE vocery TO vocery_user;
```

### 5. Configure Environment Variables
The application uses a `.env` file to manage secret keys and configuration settings. Create a file named `.env` in the `backend` directory.

```
# .env file

# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-strong-secret-key
JWT_SECRET_KEY=your-super-strong-jwt-secret-key

# Database Configuration
DATABASE_URL="postgresql://vocery_user:your_secure_password@localhost:5432/vocery"

# AI Services URLs
RASASERVERURL_EN="http://localhost:5005"
RASASERVERURL_AR="http://localhost:5006"
TTSSERVERURL="http://localhost:5002"

# File Storage Configuration
UPLOAD_FOLDER=app/uploads
TTS_OUTPUT_DIR=app/tts_output
```

### 6. Run Database Migrations
In the terminal with the `.venv` environment activated, run the following commands to set up your database schema.
```powershell
# (if .venv is not active) .\.venv\Scripts\activate
flask db upgrade
```
This command applies all the database migrations, creating the necessary tables like `customers`, `products`, etc.

### 7. Start the Development Servers
To run the full backend, you must start all four services. Each command should be run in a separate terminal window.

**a. Start the Coqui TTS Server**
*   Terminal: TTS
*   Active Environment: `tts-env`
```powershell
# Activate the environment if needed
# .\tts-env\Scripts\activate

tts-server --model_name "tts_models/multilingual/multi-dataset/xtts_v2" --port 5002
```

**b. Start the Rasa English NLU Server**
*   Terminal: Main App
*   Active Environment: `.venv`
```powershell
# Activate the environment if needed
# .\.venv\Scripts\activate

rasa run --enable-api --cors "*" -m models\nlu-en.tar.gz --port 5005
```

**c. Start the Rasa Arabic NLU Server**
*   Terminal: Main App (New Terminal)
*   Active Environment: `.venv`
```powershell
# Activate the environment if needed
# .\.venv\Scripts\activate

rasa run --enable-api --cors "*" -m models\nlu-ar.tar.gz --port 5006
```

**d. Start the Flask Development Server**
*   Terminal: Main App (New Terminal)
*   Active Environment: `.venv`
```powershell
# Activate the environment if needed
# .\.venv\Scripts\activate

python run.py
```
Your entire backend is now running and ready to accept requests at `http://127.0.0.1:5000`.

## API Endpoints

Base URL: `http://127.0.0.1:5000/api`

### Authentication Endpoints (`/auth`)

#### 1. User Registration
*   **Endpoint:** `POST /auth/register`
*   **Description:** Registers a new customer.
*   **Request Body (JSON):**
    ```json
    {
        "name": "string (required)",
        "email": "string (required, unique email)",
        "password": "string (required)",
        "phone_number": "string (optional)",
        "preferred_language": "string (optional, defaults to 'en')"
    }
    ```
*   **Responses:** Success (`201 Created`), Error (`400 Bad Request`, `500 Internal Server Error`).

#### 2. User Login
*   **Endpoint:** `POST /auth/login`
*   **Description:** Authenticates a user and returns a JSON Web Token (JWT).
*   **Request Body (JSON):**
    ```json
    {
        "email": "string (required)",
        "password": "string (required)"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "access_token": "your.jwt.token"
    }
    ```
*   **Error Responses:** `401 Unauthorized`.

#### 3. Get User Profile
*   **Endpoint:** `GET /auth/profile`
*   **Description:** Retrieves the profile of the currently authenticated user.
*   **Authentication:** Required (JWT).
*   **Success Response (200 OK):**
    ```json
    {
        "customer_id": 1,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone_number": "555-0100",
        "preferred_language": "en"
    }
    ```
*   **Error Responses:** `401 Unauthorized`.

### Product Endpoints (`/products`)

#### 1. List All Active Products
*   **Endpoint:** `GET /products`
*   **Description:** Retrieves a list of all active products with bilingual details.
*   **Success Response (200 OK):**
    ```json
    {
        "products": [
            {
                "product_id": 1,
                "name_en": "Red Apple",
                "name_ar": "تفاح أحمر",
                "price": 5.99,
                "stock_quantity": 100,
                // ... other fields
            }
        ]
    }
    ```
*   **Error Responses:** `500 Internal Server Error`.

#### 2. Search Products
*   **Endpoint:** `GET /products/search`
*   **Description:** Searches products by name in English or Arabic.
*   **Query Parameters:**
    *   `q` (string, required): The search term.
    *   `language` (string, optional, defaults to 'en'): `en` or `ar`.
*   **Example URL:** `http://localhost:5000/api/products/search?q=apple&language=en`
*   **Responses:** Success (`200 OK`), Error (`400 Bad Request`, `500 Internal Server Error`).

### Cart Endpoints (`/cart`)
All cart endpoints require JWT authentication.

#### 1. Add Item to Cart
*   **Endpoint:** `POST /cart/add`
*   **Description:** Adds a product to the cart or updates its quantity.
*   **Responses:** Success (`200 OK`), Error (`400 Bad Request`, `401 Unauthorized`, `404 Not Found`).

#### 2. View Cart
*   **Endpoint:** `GET /cart`
*   **Description:** Retrieves the full contents of the user's cart.
*   **Responses:** Success (`200 OK`), Error (`401 Unauthorized`, `500 Internal Server Error`).

#### 3. Update Cart Item Quantity
*   **Endpoint:** `PUT /cart/items/`
*   **Description:** Updates an item's quantity. Setting quantity to 0 removes the item.
*   **Responses:** Success (`200 OK`), Error (`400`, `401`, `403 Forbidden`, `404`).

#### 4. Remove Item from Cart
*   **Endpoint:** `DELETE /cart/items/`
*   **Description:** Removes an item from the cart entirely.
*   **Responses:** Success (`200 OK`), Error (`401`, `403`, `404`).

#### 5. Checkout
*   **Endpoint:** `POST /cart/checkout`
*   **Description:** Places an order from the cart contents.
*   **Responses:** Success (`201 Created`), Error (`400`, `401`, `500`).

### Order Endpoints (`/orders`)
All order endpoints require JWT authentication.

#### 1. List User's Order History
*   **Endpoint:** `GET /orders`
*   **Description:** Retrieves a list of all past orders for the authenticated user.
*   **Success Response (200 OK):**
    ```json
    {
        "orders": [
            {
                "order_id": 101,
                "order_date": "2025-07-03T18:00:00",
                "status": "completed",
                "total_amount": 55.99
            }
        ]
    }
    ```
*   **Error Responses:** `401 Unauthorized`, `500 Internal Server Error`.

#### 2. Get Specific Order Details
*   **Endpoint:** `GET /orders/`
*   **Description:** Retrieves detailed information for a single order, including all items.
*   **Success Response (200 OK):**
    ```json
    {
        "order_id": 101,
        "order_date": "2025-07-03T18:00:00",
        "status": "completed",
        "total_amount": 55.99,
        "items": [
            {
                "product_name_en": "Red Apple",
                "product_name_ar": "تفاح أحمر",
                "quantity": 2,
                "price_at_purchase": 5.99
            }
        ]
    }
    ```
*   **Error Responses:** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

### Voice Processing Endpoints (`/voice`)
These endpoints manage the core voice interaction pipeline.

#### 1. Process Voice Command
*   **Endpoint:** `POST /voice/process`
*   **Description:** The main endpoint for handling voice commands. It takes an audio file, transcribes it to text (ASR), understands the intent (NLU), executes the required action (e.g., add to cart), generates a text response, and converts that response back to audio (TTS).
*   **Authentication:** Required (JWT).
*   **Request:** `multipart/form-data` with an audio file (`.wav`, `.mp3`).
*   **Success Response (200 OK):**
    ```json
    {
        "nlu_result": {
            "intent": "search_product",
            "confidence": 0.98
        },
        "transcript": "search for apples",
        "response_text": "I found 3 types of apples. Which one would you like?",
        "audio_filename": "response-some-uuid.mp3",
        "detected_language": "en"
    }
    ```
*   **Error Responses:** `400`, `401`, `500`.

#### 2. Retrieve Response Audio
*   **Endpoint:** `GET /voice/audio/`
*   **Description:** Serves the generated audio response file created by the `/voice/process` endpoint. The mobile client calls this to play the response to the user.
*   **Response:** The audio file (`audio/mpeg`).
