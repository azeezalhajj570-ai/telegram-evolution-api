from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Instance as InstanceModel
from app.db.repositories import InstanceRepository, WebhookRepository
from app.schemas.instances import InstanceCreate, InstanceListResponse, InstanceResponse, InstanceStatusResponse
from app.security.api_keys import require_api_key

router = APIRouter(prefix="/instances", tags=["Instances"], dependencies=[Depends(require_api_key)])


def _to_response(inst: InstanceModel) -> dict:
    return {
        "id": str(inst.id),
        "name": inst.name,
        "phone_number": inst.phone_number,
        "status": inst.status,
        "created_at": inst.created_at,
        "updated_at": inst.updated_at,
    }


@router.post("", response_model=InstanceResponse, status_code=201)
async def create_instance(body: InstanceCreate, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.create(body.name)
    return InstanceResponse(**_to_response(inst))


@router.get("", response_model=InstanceListResponse)
async def list_instances(db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    instances = await repo.get_all()
    return InstanceListResponse(instances=[InstanceResponse(**_to_response(i)) for i in instances])


@router.get("/{instance_id}", response_model=InstanceResponse)
async def get_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return InstanceResponse(**_to_response(inst))


@router.get("/{instance_id}/status", response_model=InstanceStatusResponse)
async def get_instance_status(instance_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    repo = InstanceRepository(db)
    wh_repo = WebhookRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    wh = await wh_repo.get_by_instance(UUID(instance_id))
    resp = InstanceStatusResponse(**_to_response(inst))
    resp.has_webhook = wh is not None
    return resp


@router.delete("/{instance_id}", status_code=204)
async def delete_instance(instance_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    from app.services.telegram_manager import client_manager
    repo = InstanceRepository(db)
    uid = UUID(instance_id)
    await client_manager.stop_client(instance_id)
    deleted = await repo.delete(uid)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
