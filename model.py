from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: int | str
    discount: int | str
    description: str