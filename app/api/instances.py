from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.error_codes import ErrorCodes
from app.core.response import rest_error, rest_success
from app.db.database import get_db
from app.db.models import Instance as InstanceModel
from app.db.repositories import InstanceRepository, WebhookRepository
from app.schemas.instances import InstanceCreate
from app.security.api_keys import require_api_key

router = APIRouter(prefix="/instances", tags=["Instances"], dependencies=[Depends(require_api_key)])


def _to_response(inst: InstanceModel) -> dict:
    return {
        "id": str(inst.id),
        "name": inst.name,
        "phone_number": inst.phone_number,
        "status": inst.status,
        "created_at": inst.created_at.isoformat() if inst.created_at else None,
        "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
    }


@router.post("", status_code=201)
async def create_instance(body: InstanceCreate, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.create(body.name)
    return rest_success(_to_response(inst), "instances.create")


@router.get("")
async def list_instances(db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    instances = await repo.get_all()
    return rest_success([_to_response(i) for i in instances], "instances.list")


@router.get("/{instance_id}")
async def get_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("instances.get", ErrorCodes.NOT_FOUND, "Instance not found"))
    return rest_success(_to_response(inst), "instances.get")


@router.get("/{instance_id}/status")
async def get_instance_status(instance_id: str, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    wh_repo = WebhookRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail=rest_error("instances.status", ErrorCodes.NOT_FOUND, "Instance not found"))
    resp = _to_response(inst)
    wh = await wh_repo.get_by_instance(UUID(instance_id))
    resp["has_webhook"] = wh is not None
    return rest_success(resp, "instances.status")


@router.delete("/{instance_id}", status_code=204)
async def delete_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    from app.services.telegram_manager import client_manager
    repo = InstanceRepository(db)
    uid = UUID(instance_id)
    await client_manager.stop_client(instance_id)
    deleted = await repo.delete(uid)
    if not deleted:
        raise HTTPException(status_code=404, detail=rest_error("instances.delete", ErrorCodes.NOT_FOUND, "Instance not found"))
