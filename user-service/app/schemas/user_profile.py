from typing import Optional
from datetime import date
import uuid

from pydantic import BaseModel


# Shared properties
class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


# Properties to receive via API on creation
class UserProfileCreate(UserProfileBase):
    user_id: uuid.UUID
    first_name: str
    last_name: str


# Properties to receive via API on update
class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileInDBBase(UserProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {
        "from_attributes": True
    }


# Additional properties to return via API
class UserProfile(UserProfileInDBBase):
    pass