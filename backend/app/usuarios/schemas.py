from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AdminResponse(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}
