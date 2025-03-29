from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base


# Association table for many-to-many relationship
product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", UUID(as_uuid=True), ForeignKey("product.id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("category.id"), primary_key=True),
)


class Category(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    products = relationship("Product", secondary=product_category, back_populates="categories")