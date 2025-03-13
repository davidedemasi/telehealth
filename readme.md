# Telehealth Patient Management API

This repository contains a Flask-based REST API for managing patient records with asynchronous background task processing using Celery and Redis.

## Features

- RESTful API for patient management (CRUD operations)
- Token-based authentication
- Asynchronous task processing with Celery and Redis
- Comprehensive test suite

## Technology Stack

- **Flask**: Web framework
- **SQLAlchemy**: ORM for database interactions
- **Celery**: Asynchronous task queue
- **Redis**: Message broker for Celery tasks
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL compatible)

## Project Structure

```
telehealth-api/
├── app.py            # Main Flask application
├── models.py         # Database models
├── tasks.py          # Celery tasks definition
├── auth.py           # Authentication module
├── requirements.txt  # Dependencies
├── tests/            # Test directory
│   └── test_api.py   # API tests
└── README.md         # Documentation
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis server
- Virtual environment (recommended)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/telehealth-api.git
cd telehealth-api
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the Redis server:

```bash
redis-server
```

5. Start the Celery worker:

```bash
celery -A tasks worker --loglevel=info
```

6. Run the Flask application:

```bash
python app.py
```

### Running Tests

```bash
pytest tests/
```

## API Documentation

### Authentication

All endpoints require token-based authentication. Include the following header in all requests:

```
Authorization: Bearer secret-token-123
```

### Endpoints

#### Create a Patient

```
POST /patients
```

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "123-456-7890"
}
```

**Response:**

```json
{
  "message": "Patient created successfully",
  "patient": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "123-456-7890",
    "created_at": "2023-09-01T12:00:00",
    "updated_at": "2023-09-01T12:00:00"
  }
}
```

#### Get Patient by ID

```
GET /patients/<patient_id>
```

**Response:**

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "123-456-7890",
  "created_at": "2023-09-01T12:00:00",
  "updated_at": "2023-09-01T12:00:00"
}
```

#### Update Patient

```
PUT /patients/<patient_id>
```

**Request Body:**

```json
{
  "name": "John Smith",
  "phone": "987-654-3210"
}
```

**Response:**

```json
{
  "message": "Patient updated successfully",
  "patient": {
    "id": 1,
    "name": "John Smith",
    "email": "john.doe@example.com",
    "phone": "987-654-3210",
    "created_at": "2023-09-01T12:00:00",
    "updated_at": "2023-09-01T13:30:00"
  }
}
```

#### Delete Patient

```
DELETE /patients/<patient_id>
```

**Response:**

```json
{
  "message": "Patient deleted successfully"
}
```

#### Get All Patients

```
GET /patients
```

**Response:**

```json
{
  "total": 2,
  "pages": 1,
  "current_page": 1,
  "patients": [
    {
      "id": 1,
      "name": "John Smith",
      "email": "john.doe@example.com",
      "phone": "987-654-3210",
      "created_at": "2023-09-01T12:00:00",
      "updated_at": "2023-09-01T13:30:00"
    },
    {
      "id": 2,
      "name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone": "555-123-4567",
      "created_at": "2023-09-01T14:00:00",
      "updated_at": "2023-09-01T14:00:00"
    }
  ]
}
```

## Design Decisions

### Database Model

The `Patient` model includes the following fields:
- `id`: Primary key
- `name`: Patient's full name
- `email`: Patient's email (unique)
- `phone`: Patient's phone number
- `created_at` and `updated_at`: Timestamps for audit purposes

### Authentication

The application uses a simple token-based authentication mechanism. In a production environment, you would want to implement a more robust solution like JWT.

### Celery and Redis Integration

The application uses Celery with Redis as the message broker to handle asynchronous tasks. When a patient is created or updated, a notification task is triggered.

Key aspects of the Celery integration:
- Task retries with exponential backoff
- Simulated failure rate of 25% to test resilience
- Task status tracking via Redis backend

The `send_notification` task simulates sending an email or SMS to the patient. In a real-world scenario, this would integrate with actual email or SMS providers.

### Error Handling

The API includes comprehensive error handling with appropriate HTTP status codes:
- 400: Bad Request (missing required fields)
- 401: Unauthorized (missing or invalid token)
- 404: Not Found (patient not found)
- 409: Conflict (duplicate email)
- 500: Server Error (unexpected exceptions)

## Future Improvements

- Implement more robust authentication (JWT)
- Add rate limiting
- Expand test coverage
- Add logging and monitoring
- Implement database migrations
- Add API documentation with Swagger/OpenAPI
