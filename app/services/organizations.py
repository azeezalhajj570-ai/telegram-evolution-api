import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AuditLogEntry,
    Organization,
    OrganizationMember,
    ScopedApiKey,
    UsageCounter,
)
from app.security.api_keys import hash_api_key


async def create_organization(db: AsyncSession, name: str, owner_id: str) -> dict:
    org = Organization(id=uuid.uuid4(), name=name, owner_id=uuid.UUID(owner_id))
    db.add(org)
    member = OrganizationMember(
        id=uuid.uuid4(), organization_id=org.id, user_id=uuid.UUID(owner_id), role="owner"
    )
    db.add(member)
    await db.flush()
    return {"id": str(org.id), "name": org.name}


async def get_organization(db: AsyncSession, org_id: str) -> dict:
    org = await db.get(Organization, uuid.UUID(org_id))
    if not org:
        raise ValueError("Organization not found")
    return {"id": str(org.id), "name": org.name}


async def add_member(db: AsyncSession, org_id: str, user_id: str, role: str = "viewer") -> dict:
    member = OrganizationMember(
        id=uuid.uuid4(), organization_id=uuid.UUID(org_id), user_id=uuid.UUID(user_id), role=role
    )
    db.add(member)
    await db.flush()
    return {"id": str(member.id), "user_id": user_id, "role": role}


async def remove_member(db: AsyncSession, org_id: str, user_id: str) -> None:
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == uuid.UUID(org_id),
            OrganizationMember.user_id == uuid.UUID(user_id),
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise ValueError("Member not found")
    await db.delete(member)


async def create_api_key(db: AsyncSession, org_id: str, name: str, scopes: list) -> str:
    from app.security.api_keys import generate_api_key

    token = generate_api_key()
    api_key = ScopedApiKey(
        id=uuid.uuid4(),
        organization_id=uuid.UUID(org_id),
        name=name,
        key_hash=hash_api_key(token),
        scopes=scopes,
    )
    db.add(api_key)
    await db.flush()
    return token


async def delete_api_key(db: AsyncSession, org_id: str, key_id: str) -> None:
    result = await db.execute(
        select(ScopedApiKey).where(
            ScopedApiKey.id == uuid.UUID(key_id),
            ScopedApiKey.organization_id == uuid.UUID(org_id),
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise ValueError("API key not found")
    await db.delete(key)


async def log_audit(db: AsyncSession, org_id: str, actor_id: str, action: str, resource_type: str, resource_id: str = None, details: dict = None):
    uid = uuid.uuid5(uuid.NAMESPACE_DNS, actor_id) if not _is_uuid(actor_id) else uuid.UUID(actor_id)
    entry = AuditLogEntry(
        id=uuid.uuid4(),
        organization_id=uuid.UUID(org_id),
        actor_id=uid,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    db.add(entry)


def _is_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except (ValueError, AttributeError):
        return False
