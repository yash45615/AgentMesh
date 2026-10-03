from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):

    email: EmailStr

    password: str


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


class UserResponse(BaseModel):

    id: int

    email: str

    role: str

    is_active: bool

    model_config = {
        "from_attributes": True,
    }