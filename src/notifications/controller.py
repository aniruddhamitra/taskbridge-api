from typing import Any, Dict, List, Optional

from src.notifications.service import NotificationAuditService


class NotificationController:
    def __init__(self, service: NotificationAuditService):
        self.service = service

    def record_audit(self, organisation_id: str, project_id: str, actor_user_id: str, actor_ip: str, event_type: str, entity_type: str, previous_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
        return self.service.create_audit_entry(
            organisation_id,
            project_id,
            actor_user_id,
            actor_ip,
            event_type,
            entity_type,
            previous_state,
            new_state,
        )

    def get_audit_history(self, organisation_id: str, project_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.service.get_audit_history(organisation_id, project_id, from_date, to_date, event_type)

    def get_notifications(self, organisation_id: str, user_id: str) -> List[Dict[str, Any]]:
        return self.service.get_unread_notifications(organisation_id, user_id)

    def mark_read(self, notification_id: str) -> Dict[str, Any]:
        return self.service.mark_notification_read(notification_id)
