from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from app.database.storage import AsyncSessionLocal
from app.models.webhook_model import Webhook
from app.schemas import WebhookIn, WebhookOut
import requests

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/", response_model=WebhookOut)
async def create_webhook(payload: WebhookIn):
    async with AsyncSessionLocal() as session:
        wh = Webhook(url=str(payload.url), event=payload.event, active=payload.active)
        session.add(wh)
        await session.commit()
        await session.refresh(wh)
        return wh

@router.get("/")
async def list_webhooks():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Webhook))
        return res.scalars().all()

@router.post("/{wh_id}/test")
async def test_webhook(wh_id: int):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Webhook).where(Webhook.id == wh_id))
        wh = res.scalar_one_or_none()
        if not wh:
            raise HTTPException(404, "Webhook not found")
        try:
            resp = requests.post(wh.url, json={"event": "test", "msg": "Hello from server"})
            return {"status_code": resp.status_code, "text": resp.text}
        except Exception as e:
            raise HTTPException(500, str(e))
