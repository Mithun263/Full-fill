import csv
import os
import json
import requests
import asyncio
from typing import List, Dict
from sqlalchemy import text, select
from app.celery_app import celery
from app.database.storage import AsyncSessionLocal
from app.models.product_model import Product
from app.models.webhook_model import Webhook
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

def set_progress(job_id: str, percent: float, message: str = ""):
    """Stores job progress info in Redis."""
    r.set(f"job:{job_id}", json.dumps({"progress": percent, "message": message}))

@celery.task(bind=True)
def import_csv_task(self, job_id: str, filepath: str):
    """Main CSV import task triggered by Celery."""
    total = 0
    with open(filepath, "r", encoding="utf-8") as f:
        total = sum(1 for _ in f) - 1

    if total <= 0:
        set_progress(job_id, 100, "No data found")
        return {"status": "no_rows"}

    set_progress(job_id, 0, "Starting import...")

    batch, count = [], 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row.get("sku", "").strip()
            if not sku:
                continue
            batch.append({
                "sku": sku,
                "name": row.get("name"),
                "description": row.get("description"),
                "price": float(row["price"]) if row.get("price") else None,
                "active": True
            })
            count += 1
            if len(batch) >= 1000:
                asyncio.run(bulk_upsert_async(batch))
                batch.clear()
                pct = round((count / total) * 100, 2)
                set_progress(job_id, pct, f"Processed {count}/{total}")

        if batch:
            asyncio.run(bulk_upsert_async(batch))
    set_progress(job_id, 100, "Import complete")
    asyncio.run(trigger_webhooks_async("import_complete", {"job_id": job_id}))
    return {"status": "done", "rows": total}

async def bulk_upsert_async(rows: List[Dict]):
    """Asynchronously insert or update products in bulk."""
    async with AsyncSessionLocal() as session:
        for item in rows:
            stmt = text("""
                INSERT INTO products (sku, name, description, price, active)
                VALUES (:sku, :name, :description, :price, :active)
                ON CONFLICT (sku)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    price = EXCLUDED.price,
                    active = EXCLUDED.active;
            """)
            await session.execute(stmt, item)
        await session.commit()

async def trigger_webhooks_async(event: str, payload: Dict):
    """Asynchronously trigger webhooks when an import completes."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Webhook).where(Webhook.event == event, Webhook.active == True)
        )
        hooks = result.scalars().all()
        for h in hooks:
            try:
                requests.post(h.url, json=payload, timeout=5)
            except Exception:
                pass
