# Donation Tracker API Documentation

## Overview

The Donation Tracker API is a comprehensive RESTful API built with Flask that demonstrates multiple design patterns and provides a complete donation management system. The API supports user management, campaign creation, donation processing with multiple payment methods, and administrative functions.

## Design Patterns Implemented

### 1. Factory Pattern
- **Location**: `app/services/user_factory.py`
- **Purpose**: Creates different types of users (Donor, Admin) based on user type
- **Usage**: User registration endpoint uses UserFactory to create appropriate user instances

### 2. Singleton Pattern
- **Location**: `app/services/database_manager.py`
- **Purpose**: Ensures single database connection instance throughout the application
- **Features**: Thread-safe implementation with connection reuse

### 3. Repository Pattern
- **Location**: `app/services/repositories.py`
- **Purpose**: Abstracts data access layer for Users, Campaigns, and Donations
- **Benefits**: Separation of concerns, easy testing, database independence

### 4. Strategy Pattern
- **Location**: `app/services/strategy.py`
- **Purpose**: Implements different sorting algorithms and payment processing methods
- **Strategies**:
  - Sorting: Amount, Date, Progress, Deadline, Popularity
  - Payment: Credit Card, PayPal, Bank Transfer

### 5. Observer Pattern
- **Location**: `app/services/observer.py`
- **Purpose**: Event notification system for campaign updates and donations

### 6. Facade Pattern
- **Location**: `app/services/facade.py`
- **Purpose**: Simplified interface for complex operations

### 7. Proxy Pattern
- **Location**: `app/services/proxy.py`
- **Purpose**: Authentication proxy and caching layer

### 8. Chain of Responsibility Pattern
- **Location**: `app/services/chain_of_responsibility.py`
- **Purpose**: Request processing pipeline with validation and authorization

## Base URL

```
http://127.0.0.1:5005/api
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user using the Factory pattern.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "user_type": "donor",
  "phone_number": "+1-555-0123",
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "USA"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "607f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com",
    "user_type": "donor",
    "created_at": "2023-10-01T12:00:00Z"
  }
}
```

#### POST /api/auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "user_id": "607f1f77bcf86cd799439011",
      "username": "john_doe",
      "email": "john@example.com",
      "user_type": "donor"
    }
  }
}
```

#### GET /api/auth/profile
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

#### POST /api/auth/logout
Logout and invalidate token (requires authentication).

### Campaign Endpoints

#### GET /api/campaigns
Retrieve campaigns with Repository pattern and Strategy pattern for sorting.

**Query Parameters:**
- `page` (int): Page number for pagination (default: 1)
- `limit` (int): Number of campaigns per page (default: 10)
- `sort` (string): Sort strategy - date, amount, progress, deadline, popularity
- `status` (string): Filter by status - active, completed, cancelled

**Example:**
```
GET /api/campaigns?page=1&limit=10&sort=amount&status=active
```

#### GET /api/campaigns/{id}
Get specific campaign details.

#### POST /api/campaigns
Create new campaign (requires authentication).

**Request Body:**
```json
{
  "title": "Help Build Clean Water Wells",
  "description": "Providing clean water access to rural communities...",
  "goal_amount": 50000.00,
  "deadline": "2024-12-31T23:59:59Z",
  "category": "humanitarian",
  "location": {
    "country": "Kenya",
    "region": "Western Province",
    "coordinates": {
      "latitude": -0.0236,
      "longitude": 37.9062
    }
  },
  "images": [
    "https://example.com/campaign-image-1.jpg"
  ],
  "tags": ["water", "humanitarian", "development"]
}
```

#### PUT /api/campaigns/{id}
Update existing campaign (requires authentication).

#### DELETE /api/campaigns/{id}
Delete campaign (admin only).

#### GET /api/campaigns/search
Search campaigns with filters.

**Query Parameters:**
- `q` (string): Search query
- `category` (string): Campaign category
- `min_amount` (float): Minimum goal amount
- `max_amount` (float): Maximum goal amount

### Donation Endpoints

#### POST /api/donations
Process donation using Strategy pattern for different payment methods.

**Credit Card Payment:**
```json
{
  "campaign_id": "607f1f77bcf86cd799439012",
  "amount": 100.00,
  "payment_method": "credit_card",
  "payment_details": {
    "card_number": "4111111111111111",
    "expiry_month": "12",
    "expiry_year": "2025",
    "cvv": "123",
    "cardholder_name": "John Doe"
  },
  "anonymous": false,
  "message": "Happy to support this great cause!"
}
```

**PayPal Payment:**
```json
{
  "campaign_id": "607f1f77bcf86cd799439012",
  "amount": 250.00,
  "payment_method": "paypal",
  "payment_details": {
    "paypal_email": "john@example.com",
    "paypal_token": "EC-123456789"
  },
  "anonymous": false,
  "message": "Keep up the great work!"
}
```

**Bank Transfer Payment:**
```json
{
  "campaign_id": "607f1f77bcf86cd799439012",
  "amount": 500.00,
  "payment_method": "bank_transfer",
  "payment_details": {
    "bank_name": "Chase Bank",
    "account_number": "****1234",
    "routing_number": "021000021",
    "account_holder": "John Doe"
  },
  "anonymous": true,
  "message": "Anonymous donation"
}
```

#### GET /api/donations/user
Get all donations made by the current user (requires authentication).

#### GET /api/donations/campaign/{campaign_id}
Get all donations for a specific campaign.

### Admin Endpoints

#### GET /api/admin/users
Get all users (admin only).

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Users per page
- `user_type` (string): Filter by user type (all, donor, admin)

#### GET /api/admin/stats
Get system statistics and analytics (admin only).

#### PATCH /api/admin/users/{user_id}/status
Update user account status (admin only).

**Request Body:**
```json
{
  "status": "suspended",
  "reason": "Policy violation"
}
```

### Design Pattern Testing Endpoints

#### POST /api/test/factory
Test UserFactory pattern by creating different user types.

#### GET /api/test/singleton
Test DatabaseManager singleton pattern.

#### GET /api/test/strategy/sort
Test different sorting strategies for campaigns.

**Query Parameters:**
- `strategy` (string): Sorting strategy - amount, date, progress, deadline, popularity
- `order` (string): Sort order - asc, desc

#### GET /api/test/repository/campaigns
Test CampaignRepository pattern operations.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "data": null
}
```

### Common HTTP Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (creation)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute per IP address
- 1000 requests per hour per authenticated user

## Data Models

### User Model
```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "user_type": "donor|admin",
  "phone_number": "string",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Campaign Model
```json
{
  "campaign_id": "string",
  "title": "string",
  "description": "string",
  "goal_amount": "float",
  "current_amount": "float",
  "deadline": "datetime",
  "status": "active|completed|cancelled",
  "category": "string",
  "creator_id": "string",
  "location": {
    "country": "string",
    "region": "string",
    "coordinates": {
      "latitude": "float",
      "longitude": "float"
    }
  },
  "images": ["string"],
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Donation Model
```json
{
  "donation_id": "string",
  "campaign_id": "string",
  "donor_id": "string",
  "amount": "float",
  "payment_method": "credit_card|paypal|bank_transfer",
  "transaction_id": "string",
  "status": "pending|completed|failed",
  "anonymous": "boolean",
  "message": "string",
  "created_at": "datetime"
}
```

## Environment Variables

The application requires the following environment variables:

```bash
# Database Configuration
MONGO_URI=mongodb://localhost:27017/donation_tracker
DB_NAME=donation_tracker

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_flask_secret_key

# Payment Gateway Configuration
STRIPE_SECRET_KEY=sk_test_...
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
```

## Testing with Postman

1. Import the collection: `postman/Donation_Tracker_API.postman_collection.json`
2. Import the environment: `postman/Donation_Tracker.postman_environment.json`
3. Set up environment variables (base_url, test credentials)
4. Run the collection to test all endpoints

The collection includes:
- Pre-request scripts for dynamic data generation
- Test scripts for response validation
- Automatic token extraction and storage
- Environment variable management

## Performance Considerations

- Database indexes on frequently queried fields
- Connection pooling with MongoDB
- Response caching for static data
- Pagination for large datasets
- Async processing for email notifications

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Rate limiting
- Secure headers