from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime


class AccountListSchema(BaseModel):
    accounts: list[AccountPublicSchema]
    total: int
