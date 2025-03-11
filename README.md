# ShareFoods Backend

This is the backend service for ShareFoods, an AI-powered food logistics optimization platform that connects food donors with recipients and optimizes food distribution.

## Features

- User Authentication and Authorization
- Food Listings Management
- Real-time Notifications
- WebSocket Support for Real-time Updates
- S3 Integration for File Storage
- AI-powered Logistics Optimization
- Trade Management System
- Task Management for Volunteers
- Admin Dashboard

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn main:app --reload
```

## API Documentation

Once the server is running, visit `/docs` for the complete API documentation.

## Testing

Run the tests using:
```bash
pytest
```

## Architecture

The application follows a clean architecture pattern:
- `/models` - Database models
- `/schemas` - Pydantic schemas for request/response validation
- `/routers` - API route handlers
- `/services` - Business logic and external service integrations

## Features Detail

### Authentication
- JWT-based authentication
- Role-based access control
- Secure password hashing

### Real-time Updates
- WebSocket support for instant notifications
- Chat functionality
- Live status updates

### AI Integration
- Smart matching algorithm for food distribution
- Route optimization for deliveries
- Demand prediction

### Storage
- S3 integration for file storage
- Presigned URLs for secure access
- Efficient file management

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT License