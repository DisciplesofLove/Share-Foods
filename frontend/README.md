# ShareFoods Frontend

This is the frontend application for ShareFoods, built with React.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000

## Docker Setup

The application is containerized and can be run using Docker. To start the entire application stack (frontend, backend, and database):

```bash
docker-compose up
```

This will start:
- Frontend at http://localhost:3000
- Backend API at http://localhost:8000
- PostgreSQL database

## Environment Variables

The following environment variables are used:

- `REACT_APP_API_URL`: The URL of the backend API (default: http://localhost:8000)