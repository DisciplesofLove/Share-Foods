import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.listings import FoodListing, FoodCategory, ListingStatus
from ..models.users import User, UserType
from ..schemas.listings import ListingCreate, ListingUpdate
from ..main import app

def test_create_listing(test_db: Session, test_client: TestClient, test_user_token: str):
    # Create test listing data
    listing_data = {
        "title": "Fresh Vegetables",
        "description": "Assorted fresh vegetables",
        "category": FoodCategory.PRODUCE,
        "quantity": 10,
        "expiration_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "pickup_location": "123 Test St",
        "is_donation": True
    }
    
    response = test_client.post(
        "/listings/",
        json=listing_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == listing_data["title"]
    assert data["owner_id"] is not None
    assert data["status"] == ListingStatus.AVAILABLE

def test_get_listings(test_db: Session, test_client: TestClient):
    response = test_client.get("/listings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_listing(test_db: Session, test_client: TestClient, test_user_token: str, test_listing: FoodListing):
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    
    response = test_client.put(
        f"/listings/{test_listing.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

def test_delete_listing(test_db: Session, test_client: TestClient, test_user_token: str, test_listing: FoodListing):
    response = test_client.delete(
        f"/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 204
    
    # Verify listing is deleted
    listing = test_db.query(FoodListing).filter(FoodListing.id == test_listing.id).first()
    assert listing is None

def test_unauthorized_update(test_db: Session, test_client: TestClient, other_user_token: str, test_listing: FoodListing):
    update_data = {"title": "Unauthorized Update"}
    
    response = test_client.put(
        f"/listings/{test_listing.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    
    assert response.status_code == 403

def test_get_recommendations(test_db: Session, test_client: TestClient, test_user_token: str):
    response = test_client.get(
        "/listings/recommendations",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)