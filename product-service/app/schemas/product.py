from typing import List, Optional
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.category import Category


# Shared properties
class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    name: str
    price: Decimal = Field(..., ge=0)
    sku: str
    category_ids: List[uuid.UUID] = []


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    category_ids: Optional[List[uuid.UUID]] = None


class ProductInDBBase(ProductBase):
    id: uuid.UUID
    name: str
    price: Decimal
    stock: int
    sku: str

    model_config = {
        "from_attributes": True
    }


# Additional properties to return via API
class Product(ProductInDBBase):
    categories: List[Category] = []