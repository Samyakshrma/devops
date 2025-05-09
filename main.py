from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import uvicorn
import os
from typing import Optional  # Import Optional for type hints

# Load environment variables
load_dotenv()

# Database setup (Neon DB connection)
DATABASE_URL = "postgresql://neondb_owner:npg_wRf52TnHZqyz@ep-tight-glitter-a4rv8r0o-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Updated to use new SQLAlchemy 2.0 location
Base = declarative_base()

# Database model
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model with corrected type hints
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None  # Using Optional instead of |

class ItemResponse(ItemCreate):
    id: int

    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hellothere"}

@app.post("/save/", response_model=ItemResponse)
async def save_item(item: ItemCreate):
    db = SessionLocal()
    try:
        db_item = Item(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/items/", response_model=list[ItemResponse])
async def get_items():
    db = SessionLocal()
    try:
        items = db.query(Item).all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)