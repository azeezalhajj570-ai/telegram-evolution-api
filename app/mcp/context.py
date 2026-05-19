from contextvars import ContextVar
from typing import Optional

_current_instance_id: ContextVar[Optional[str]] = ContextVar("current_instance_id", default=None)


def set_current_instance(instance_id: Optional[str]):
    if instance_id is None:
        _current_instance_id.set(None)
    else:
        _current_instance_id.set(instance_id)


def get_current_instance() -> Optional[str]:
    return _current_instance_id.get()


def resolve_instance_id(instance_id: Optional[str] = None) -> Optional[str]:
    if instance_id:
        return instance_id
    return get_current_instance()
