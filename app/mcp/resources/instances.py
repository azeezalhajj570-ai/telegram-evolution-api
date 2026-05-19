import uuid

from mcp.server.fastmcp import FastMCP

from app.db.database import async_session
from app.db.repositories import InstanceRepository


def register_instance_resources(mcp: FastMCP):
    @mcp.resource(
        uri="telegram://instances",
        name="All Instances",
        description="List of all Telegram instances with their status and connection state",
        mime_type="application/json",
    )
    async def instances_list() -> str:
        async with async_session() as db:
            repo = InstanceRepository(db)
            instances = await repo.get_all()
            import json
            return json.dumps([
                {
                    "id": str(inst.id),
                    "name": inst.name,
                    "phone_number": inst.phone_number,
                    "status": inst.status,
                    "created_at": inst.created_at.isoformat() if inst.created_at else None,
                }
                for inst in instances
            ])

    @mcp.resource(
        uri="telegram://instances/{instance_id}",
        name="Single Instance",
        description="Detailed information about a specific Telegram instance",
        mime_type="application/json",
    )
    async def instance_detail(instance_id: str) -> str:
        async with async_session() as db:
            repo = InstanceRepository(db)
            inst = await repo.get(uuid.UUID(instance_id))
            import json
            if not inst:
                return json.dumps({"error": "Instance not found"})
            return json.dumps({
                "id": str(inst.id),
                "name": inst.name,
                "phone_number": inst.phone_number,
                "status": inst.status,
                "has_session": bool(inst.session_encrypted),
                "created_at": inst.created_at.isoformat() if inst.created_at else None,
                "updated_at": inst.updated_at.isoformat() if inst.updated_at else None,
            })
