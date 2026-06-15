# API Contract v1

## Base URL

/api/v1

---

## Response Format

All APIs return a standardized response structure.

Success Response:

{
  "success": true,
  "message": "Operation successful",
  "data": {}
}

Error Response:

{
  "success": false,
  "message": "Error message"
}

## GET /health

Purpose:
Application health verification.

Response:

Status: 200 OK

{
  "success": true,
  "message": "Application is healthy"
}
## POST /auth/register
{
  "email": "aditya@example.com",
  "password": "StrongPassword123"
}
email
- required
- valid email
- unique

password
- required
- minimum 8 characters

201 Created
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": "uuid",
    "email": "aditya@example.com"
  }
}



409 Conflict
{
  "success": false,
  "message": "User already exists"
}

## POST /auth/login

{
  "email": "aditya@example.com",
  "password": "StrongPassword123"
}
200 OK

{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "<jwt_token>",
    "token_type": "bearer"
  }
}
401 Unauthorized

{
  "success": false,
  "message": "Invalid credentials"
}
## GET /auth/me
Authorization: Bearer <token>
200 OK
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "aditya@example.com"
  }
}
401 Unauthorized
{
  "success": false,
  "message": "Invalid token"
}
## Authentication Flow

User Registers

↓

Password Hashed

↓

Stored In Database

↓

User Logs In

↓

Password Verified

↓

JWT Generated

↓

JWT Returned

↓

JWT Sent In Authorization Header

↓

Protected Route Access