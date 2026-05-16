from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import AuditLogEntry, OrganizationMember, UsageCounter
from app.security.api_keys import require_api_key
from app.services import organizations as svc

router = APIRouter(prefix="/organizations", tags=["Organizations"], dependencies=[Depends(require_api_key)])


class CreateOrgRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)


class AddMemberRequest(BaseModel):
    user_id: str
    role: str = "viewer"


class CreateApiKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    scopes: list = []


@router.post("", status_code=201)
async def create_organization(body: CreateOrgRequest, db: AsyncSession = Depends(get_db)):
    actor = "00000000-0000-0000-0000-000000000001"
    result = await svc.create_organization(db, body.name, actor)
    await svc.log_audit(db, result["id"], actor, "organization.created", "organization", result["id"])
    await db.commit()
    return result


@router.get("/{org_id}")
async def get_organization(org_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.get_organization(db, org_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{org_id}/members", status_code=201)
async def add_member(org_id: str, body: AddMemberRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await svc.add_member(db, org_id, body.user_id, body.role)
        await svc.log_audit(db, org_id, "admin", "member.added", "member", result["id"])
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{org_id}/members/{user_id}", status_code=204)
async def remove_member(org_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await svc.remove_member(db, org_id, user_id)
        await svc.log_audit(db, org_id, "admin", "member.removed", "member", user_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{org_id}/api-keys", status_code=201)
async def create_api_key(org_id: str, body: CreateApiKeyRequest, db: AsyncSession = Depends(get_db)):
    try:
        token = await svc.create_api_key(db, org_id, body.name, body.scopes)
        await svc.log_audit(db, org_id, "admin", "api_key.created", "api_key")
        await db.commit()
        return {"key": token, "name": body.name, "scopes": body.scopes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{org_id}/api-keys/{key_id}", status_code=204)
async def delete_api_key(org_id: str, key_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await svc.delete_api_key(db, org_id, key_id)
        await svc.log_audit(db, org_id, "admin", "api_key.deleted", "api_key", key_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{org_id}/usage")
async def get_usage(org_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UsageCounter).where(UsageCounter.organization_id == UUID(org_id))
    )
    counters = result.scalars().all()
    return {
        "counters": [
            {
                "metric": c.metric,
                "current_value": c.current_value,
                "limit_value": c.limit_value,
                "period_start": c.period_start.isoformat(),
                "period_end": c.period_end.isoformat(),
            }
            for c in counters
        ]
    }


@router.get("/{org_id}/audit-logs")
async def get_audit_logs(org_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditLogEntry)
        .where(AuditLogEntry.organization_id == UUID(org_id))
        .order_by(AuditLogEntry.created_at.desc())
        .limit(100)
    )
    entries = result.scalars().all()
    return {
        "logs": [
            {
                "id": str(e.id),
                "actor_id": str(e.actor_id),
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ]
    }
