from fastapi.testclient import TestClient
from main import app, SessionLocal, Item
import uuid

client = TestClient(app)

def setup_module():
    """Create a test item with unique name"""
    test_name = f"test-{uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    try:
        db_item = Item(name=test_name, description="pytest")
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        yield db_item
    finally:
        # Cleanup
        db.query(Item).filter(Item.name == test_name).delete()
        db.commit()
        db.close()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hellothere"}

def test_create_and_read_item():
    test_name = f"test-{uuid.uuid4().hex[:8]}"
    
    # Test creation
    create_response = client.post(
        "/save/",
        json={"name": test_name, "description": "pytest"}
    )
    assert create_response.status_code == 200
    
    # Test reading
    read_response = client.get("/items/")
    assert read_response.status_code == 200
    assert any(item["name"] == test_name for item in read_response.json())
    
    # Cleanup (in case test fails)
    db = SessionLocal()
    db.query(Item).filter(Item.name == test_name).delete()
    db.commit()
    db.close()