from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="ShareFoods API",
             description="AI-Powered Food Logistics Optimization Platform",
             version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to ShareFoods API - Food Logistics Optimization Platform"}

# Include routers
from .routers import users, auth, listings, claims, tasks, admin, trades, websockets

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(claims.router)
app.include_router(tasks.router)
app.include_router(admin.router)
app.include_router(trades.router)

# WebSocket endpoint
app.websocket("/ws/{user_id}")(websockets.websocket_endpoint)

# Add any missing database models
from .models import database
database.Base.metadata.create_all(bind=database.engine)