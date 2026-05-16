from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.schemas.queue import JobQueuedResponse, JobStatusResponse, RateLimitResponse, SendTextQueuedRequest
from app.security.api_keys import require_api_key
from app.services.message_queue import enqueue, get_job
from app.services.rate_limits import check_rate_limit, get_rate_limit_status

router = APIRouter(prefix="/instances/{instance_id}", tags=["Queue"], dependencies=[Depends(require_api_key)])


@router.post("/messages/send-text", response_model=JobQueuedResponse, status_code=202)
async def send_text_queued(instance_id: str, body: SendTextQueuedRequest, db: AsyncSession = Depends(get_db)):
    uid = UUID(instance_id)
    repo = InstanceRepository(db)
    inst = await repo.get(uid)
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")

    allowed, retry_after = await check_rate_limit(instance_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_after_seconds": retry_after},
        )

    job_id = await enqueue(instance_id, "send_text", body.model_dump(), body.idempotency_key)
    return JobQueuedResponse(job_id=job_id)


@router.get("/messages/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(instance_id: str, job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.get("job_id", ""),
        status=job.get("status", "unknown"),
        type=job.get("type", ""),
        attempt_count=int(job.get("attempt_count", 0)),
        message_id=int(job.get("message_id", 0)) or None,
        error=job.get("error") or None,
        created_at=float(job.get("created_at", 0)) or None,
        updated_at=float(job.get("updated_at", 0)) or None,
    )


@router.get("/rate-limit", response_model=RateLimitResponse)
async def get_rate_limit(instance_id: str):
    status_data = await get_rate_limit_status(instance_id)
    return RateLimitResponse(**status_data)
