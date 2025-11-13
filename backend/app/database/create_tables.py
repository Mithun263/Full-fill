import asyncio
from app.database.storage import engine, Base
from app.models.product_model import Product

async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ All tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_all_tables())
