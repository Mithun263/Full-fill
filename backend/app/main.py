from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, upload, webhooks
from app.database.storage import Base, engine

app = FastAPI(title="ACME Product Importer")

# Create DB tables on startup (optional if already created manually)
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS for React frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.10:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(products.router)
app.include_router(upload.router)
app.include_router(webhooks.router)

@app.get("/")
def root():
    return {"message": "🚀 FastAPI + PostgreSQL + CSV Upload is running successfully"}
