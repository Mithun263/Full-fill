from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from app.database.storage import AsyncSessionLocal
from app.models.product_model import Product
import csv
import io
import logging

router = APIRouter(prefix="/products", tags=["Products"])

logger = logging.getLogger(__name__)


# ---------------------------
# List Products
# ---------------------------
@router.get("/all", response_model=list[dict])
async def list_products():
    """Return all products (for demo — you can later paginate this)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "description": p.description,
                "price": p.price,
            }
            for p in products
        ]


# ---------------------------
# Upload CSV (deduplicated, safe batch insert)
# ---------------------------
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV with deduplication and bulk upsert per 1000 rows."""
    try:
        # ✅ Read and decode CSV
        contents = await file.read()
        decoded = contents.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(decoded))

        required_fields = {"name", "sku", "description"}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain {required_fields}",
            )

        valid_columns = {"name", "sku", "description", "price"}
        batch = []
        batch_size = 1000
        total_inserted = 0
        seen_skus = set()  # ✅ Track SKUs globally in this import

        async with AsyncSessionLocal() as session:
            async with session.begin():
                for row in reader:
                    clean_data = {
                        k: v.strip() for k, v in row.items() if k in valid_columns and v
                    }
                    sku = clean_data.get("sku")

                    if not sku or sku in seen_skus:
                        # skip duplicates within file
                        continue
                    seen_skus.add(sku)

                    # Convert price safely
                    if "price" in clean_data:
                        try:
                            clean_data["price"] = float(clean_data["price"])
                        except ValueError:
                            clean_data["price"] = None

                    batch.append(clean_data)

                    # Process each batch safely
                    if len(batch) >= batch_size:
                        await bulk_upsert_async(session, batch)
                        total_inserted += len(batch)
                        batch.clear()

                # Final small batch
                if batch:
                    await bulk_upsert_async(session, batch)
                    total_inserted += len(batch)

        logger.info(f"✅ Imported {total_inserted} products")
        return {"status": "done", "rows_imported": total_inserted}

    except Exception as e:
        logger.exception("CSV upload failed")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process CSV: {str(e)}",
        ) from e


# ---------------------------
# Bulk UPSERT Helper (deduplicated per batch)
# ---------------------------
async def bulk_upsert_async(session, rows):
    """Perform batch UPSERT into Postgres, deduplicated by SKU."""
    if not rows:
        return

    # ✅ Deduplicate SKUs within this batch
    unique_rows = list({row["sku"]: row for row in rows}.values())

    stmt = insert(Product).values(unique_rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["sku"],
        set_={
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
            "price": stmt.excluded.price,
        },
    )
    await session.execute(stmt)
