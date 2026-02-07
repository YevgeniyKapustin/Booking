from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["admin@booking.com"])
    password: str = Field(min_length=8, examples=["12345678"])
    phone_number: str = Field(examples=["+79991234567"])
    full_name: str = Field(examples=["Admin User"])


class UserLogin(BaseModel):
    email: EmailStr = Field(examples=["admin@booking.com"])
    password: str = Field(min_length=8, examples=["12345678"])


class UserRead(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    full_name: str


class Token(BaseModel):
    access_token: str = Field(
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjk5"
            "OTk5OTk5fQ.k5p9Z0pQmFQyCthdxn8t2aY3bY2tI3oUsy1B3uDgT5M"
        ]
    )
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
