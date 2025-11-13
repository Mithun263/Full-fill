from sqlalchemy import Column, Integer, String, Float
from app.database.storage import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Float)
