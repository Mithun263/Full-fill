from pydantic import BaseModel, HttpUrl
from typing import Optional

class ProductIn(BaseModel):
    sku: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    active: Optional[bool] = True

class ProductOut(ProductIn):
    id: int

class WebhookIn(BaseModel):
    url: HttpUrl
    event: str
    active: Optional[bool] = True

class WebhookOut(WebhookIn):
    id: int
