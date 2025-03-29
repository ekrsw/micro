from typing import List, Optional
import uuid

from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    name: str


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


class CategoryInDBBase(CategoryBase):
    id: uuid.UUID
    name: str

    model_config = {
        "from_attributes": True
    }


# Additional properties to return via API
class Category(CategoryInDBBase):
    pass


# For return with products
class CategoryWithProducts(CategoryInDBBase):
    products: List["ProductInDB"] = []


from app.schemas.product import ProductInDBBase as ProductInDB
CategoryWithProducts.model_rebuild()