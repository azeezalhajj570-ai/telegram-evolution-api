from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories import InstanceRepository
from app.security.api_keys import require_api_key
from app.services import channels, contacts, groups

router = APIRouter(prefix="/instances/{instance_id}", tags=["Contacts, Groups, Channels"], dependencies=[Depends(require_api_key)])

# ── Contacts ──


class ImportContactRequest(BaseModel):
    phone_number: str
    first_name: str = ""
    last_name: str = ""


@router.get("/contacts")
async def list_contacts(instance_id: str, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        return {"contacts": await contacts.list_contacts(UUID(instance_id))}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/contacts/import", status_code=201)
async def import_contact(instance_id: str, body: ImportContactRequest, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        result = await contacts.import_contact(UUID(instance_id), body.phone_number, body.first_name, body.last_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/contacts/{user_id}", status_code=204)
async def delete_contact(instance_id: str, user_id: int, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        await contacts.delete_contact(UUID(instance_id), user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Groups ──


class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


class AddMemberRequest(BaseModel):
    user_id: int


@router.post("/groups", status_code=201)
async def create_group(instance_id: str, body: CreateGroupRequest, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        result = await groups.create_group(UUID(instance_id), body.name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/groups")
async def list_groups(instance_id: str, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        return {"groups": await groups.list_groups(UUID(instance_id))}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/groups/{group_id}/members", status_code=201)
async def add_member(instance_id: str, group_id: int, body: AddMemberRequest, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        await groups.add_member(UUID(instance_id), group_id, body.user_id)
        return {"status": "added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/groups/{group_id}/members/{user_id}", status_code=204)
async def remove_member(instance_id: str, group_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        await groups.remove_member(UUID(instance_id), group_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Channels ──


class JoinChannelRequest(BaseModel):
    username: str


@router.post("/channels/join", status_code=201)
async def join_channel(instance_id: str, body: JoinChannelRequest, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        result = await channels.join_channel(UUID(instance_id), body.username)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/channels/leave")
async def leave_channel(instance_id: str, channel_id: int, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        await channels.leave_channel(UUID(instance_id), channel_id)
        return {"status": "left"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/channels")
async def list_channels(instance_id: str, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        return {"channels": await channels.list_channels(UUID(instance_id))}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/channels/{channel_id}/messages")
async def get_channel_messages(instance_id: str, channel_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = InstanceRepository(db)
    inst = await repo.get(UUID(instance_id))
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    if inst.status != "connected":
        raise HTTPException(status_code=400, detail="Instance not connected")
    try:
        return {"messages": await channels.get_channel_messages(UUID(instance_id), channel_id, limit)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
