from sqlalchemy import Column, String, Numeric, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base_class import Base
from app.models.category import product_category


class Product(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    sku = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    
    categories = relationship("Category", secondary=product_category, back_populates="products")