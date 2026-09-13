"""Pydantic request models for API v1."""

from pydantic import BaseModel, Field


class FlowRequest(BaseModel):
    from_wallet: str = Field(..., alias="from")
    to: str
    amount: float

    model_config = {"populate_by_name": True}


class HashRequest(BaseModel):
    input: str


class SignVerifyRequest(BaseModel):
    wallet: str
    message: str
    signature: str
