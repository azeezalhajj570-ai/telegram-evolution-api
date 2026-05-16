from pydantic import BaseModel, Field


class SendCodeRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+[1-9]\d{6,14}$")


class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=16)


class TwoFARequest(BaseModel):
    password: str = Field(..., min_length=1)


class AuthStatusResponse(BaseModel):
    status: str
    twofa_required: bool = False
