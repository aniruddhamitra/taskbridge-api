import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class NotificationAuditService:
    def __init__(self):
        self.audit_entries: List[Dict[str, Any]] = []
        self.notifications: List[Dict[str, Any]] = []

    def create_audit_entry(
        self,
        organisation_id: str,
        project_id: str,
        actor_user_id: str,
        actor_ip: str,
        event_type: str,
        entity_type: str,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        entry = {
            'id': str(uuid.uuid4()),
            'organisation_id': organisation_id,
            'project_id': project_id,
            'entity_type': entity_type,
            'entity_id': entity_id or project_id,
            'actor_user_id': actor_user_id,
            'actor_ip': actor_ip,
            'event_type': event_type,
            'previous_state': previous_state,
            'new_state': new_state,
            'timestamp': (timestamp or datetime.utcnow()).isoformat() if hasattr(timestamp or datetime.utcnow(), 'isoformat') else str(timestamp or datetime.utcnow()),
            'immutable': True,
        }
        self.audit_entries.append(entry)
        return entry

    def delete_audit_entry(self, organisation_id: str, audit_id: str) -> None:
        entry = next((e for e in self.audit_entries if e['id'] == audit_id and e['organisation_id'] == organisation_id), None)
        if entry is None:
            raise PermissionError('Audit entry not found or cannot be modified')
        raise PermissionError('Audit entries are immutable and cannot be deleted')

    def handle_project_event(self, project: Dict[str, Any], event_type: str, actor_user_id: str, state_change: Dict[str, Any]) -> List[Dict[str, Any]]:
        previous = {k: project.get(k) for k in ('id', 'organisation_id', 'team_id', 'status', 'name')}
        new_state = {**previous, **state_change}
        self.create_audit_entry(
            organisation_id=project['organisation_id'],
            project_id=project['id'],
            actor_user_id=actor_user_id,
            actor_ip='0.0.0.0',
            event_type=event_type,
            entity_type='project',
            previous_state=previous,
            new_state=new_state,
        )
        notifications = []
        for recipient in project.get('members', []):
            notification = {
                'id': str(uuid.uuid4()),
                'organisation_id': project['organisation_id'],
                'recipient_user_id': recipient,
                'project_id': project['id'],
                'event_type': event_type,
                'message': f'Project {project["id"]} changed: {event_type}',
                'read_status': False,
                'created_at': datetime.utcnow().isoformat(),
            }
            self.notifications.append(notification)
            notifications.append(notification)
        return notifications

    def get_audit_history(self, organisation_id: str, project_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if organisation_id is None:
            raise PermissionError('Organisation is required')
        entries = [e for e in self.audit_entries if e['organisation_id'] == organisation_id and e['project_id'] == project_id]
        if event_type:
            entries = [e for e in entries if e['event_type'] == event_type]
        if from_date:
            entries = [e for e in entries if e['timestamp'] >= from_date]
        if to_date:
            entries = [e for e in entries if e['timestamp'] <= to_date]
        return entries

    def get_unread_notifications(self, organisation_id: str, user_id: str) -> List[Dict[str, Any]]:
        return [
            n for n in self.notifications
            if n['organisation_id'] == organisation_id and n['recipient_user_id'] == user_id and not n['read_status']
        ]

    def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read_status'] = True
                return notification
        raise KeyError('Notification not found')
