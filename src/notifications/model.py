from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AuditEntry:
    id: str
    organisation_id: str
    project_id: str
    entity_type: str
    entity_id: str
    actor_user_id: str
    actor_ip: str
    event_type: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    timestamp: datetime
    immutable: bool = True


@dataclass
class NotificationRecord:
    id: str
    organisation_id: str
    recipient_user_id: str
    project_id: str
    event_type: str
    message: str
    read_status: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
