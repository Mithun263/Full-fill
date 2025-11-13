import os
import uuid
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.tasks import import_csv_task  # your async import task

router = APIRouter(prefix="/import", tags=["Import"])

# -------------------------------
# Configuration
# -------------------------------
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job storage (job_id -> status dict)
JOB_STATUS = {}

# -------------------------------
# Upload CSV (Async + Chunked)
# -------------------------------
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload large CSV file in chunks and queue for async import."""
    try:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files allowed")

        job_id = str(uuid.uuid4())
        dest = UPLOAD_DIR / f"{job_id}.csv"

        # Stream file to disk (prevents memory overflow)
        try:
            with open(dest, "wb") as f:
                while chunk := await file.read(1024 * 1024):  # 1 MB chunks
                    f.write(chunk)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        # Initialize in-memory progress
        JOB_STATUS[job_id] = {"progress": 0, "message": "Queued for import"}

        # Enqueue Celery task
        import_csv_task.apply_async(args=[job_id, str(dest)], queue="imports")

        return {
            "job_id": job_id,
            "message": "Upload successful — import started",
            "status_url": f"/import/status/{job_id}",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# -------------------------------
# Job Status Endpoint
# -------------------------------
@router.get("/status/{job_id}")
def job_status(job_id: str):
    """Check progress of an import job."""
    data = JOB_STATUS.get(job_id)
    if not data:
        return {"progress": 0, "message": "Queued or unknown job"}
    return data


# -------------------------------
# Helper function to update job progress
# -------------------------------
def set_progress(job_id: str, progress: int, message: str):
    """Update in-memory job progress."""
    if job_id in JOB_STATUS:
        JOB_STATUS[job_id] = {"progress": progress, "message": message}
