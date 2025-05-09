from pydantic import BaseModel, Field

class CreateOrderInput(BaseModel):
    order_details: str = Field(..., description="Order details in JSON format.")

class CheckInventoryInput(BaseModel):
    product: str = Field(..., description="Name of the product (e.g., 'iPhone 15 Pro Max')")
    storage: str = Field(None, description="Storage capacity (e.g., '256GB')")
    color: str = Field(None, description="Color of the product (e.g., 'Titan tự nhiên')")