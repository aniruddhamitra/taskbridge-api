import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.notifications.service import NotificationAuditService


def test_notification_service_dispatches_to_all_team_members():
    service = NotificationAuditService()
    project = {
        'id': 'proj-1',
        'organisation_id': 'org-1',
        'team_id': 'team-1',
        'name': 'Alpha',
        'status': 'ACTIVE',
        'members': ['user-1', 'user-2', 'user-3'],
    }
    notifications = service.handle_project_event(project, 'MILESTONE_UPDATED', 'user-1', {'status': 'ACTIVE'})
    assert len(notifications) == 3
    assert {n['recipient_user_id'] for n in notifications} == {'user-1', 'user-2', 'user-3'}


def test_audit_entry_created_on_update():
    service = NotificationAuditService()
    project = {'id': 'proj-1', 'organisation_id': 'org-1', 'team_id': 'team-1', 'status': 'ACTIVE', 'members': ['user-1']}
    audit = service.create_audit_entry(
        organisation_id='org-1',
        project_id='proj-1',
        actor_user_id='user-1',
        actor_ip='10.0.0.5',
        event_type='MILESTONE_UPDATED',
        entity_type='project',
        previous_state={'status': 'ACTIVE'},
        new_state={'status': 'ARCHIVED'},
    )
    assert audit['event_type'] == 'MILESTONE_UPDATED'
    assert audit['new_state']['status'] == 'ARCHIVED'


def test_audit_entry_is_immutable():
    service = NotificationAuditService()
    audit = service.create_audit_entry(
        organisation_id='org-1',
        project_id='proj-1',
        actor_user_id='user-1',
        actor_ip='10.0.0.5',
        event_type='MILESTONE_CREATED',
        entity_type='project',
        previous_state={},
        new_state={'status': 'ACTIVE'},
    )
    try:
        service.delete_audit_entry('org-1', audit['id'])
        raise AssertionError('Expected immutability failure')
    except PermissionError:
        pass


def test_audit_history_filters_by_date_range():
    service = NotificationAuditService()
    now = datetime.utcnow()
    service.create_audit_entry('org-1', 'proj-1', 'user-1', '10.0.0.5', 'MILESTONE_UPDATED', 'project', {'status': 'ACTIVE'}, {'status': 'ARCHIVED'}, timestamp=now - timedelta(days=2))
    service.create_audit_entry('org-1', 'proj-1', 'user-1', '10.0.0.5', 'MILESTONE_UPDATED', 'project', {'status': 'ARCHIVED'}, {'status': 'CLOSED'}, timestamp=now - timedelta(days=1))

    entries = service.get_audit_history('org-1', 'proj-1', from_date=(now - timedelta(days=1, hours=2)).isoformat(), to_date=now.isoformat())
    assert len(entries) == 1
    assert entries[0]['new_state']['status'] == 'CLOSED'


def test_audit_history_filters_by_event_type():
    service = NotificationAuditService()
    service.create_audit_entry('org-1', 'proj-1', 'user-1', '10.0.0.5', 'MILESTONE_CREATED', 'project', {}, {'status': 'ACTIVE'})
    service.create_audit_entry('org-1', 'proj-1', 'user-1', '10.0.0.5', 'MILESTONE_UPDATED', 'project', {'status': 'ACTIVE'}, {'status': 'ARCHIVED'})

    entries = service.get_audit_history('org-1', 'proj-1', event_type='MILESTONE_UPDATED')
    assert len(entries) == 1
    assert entries[0]['event_type'] == 'MILESTONE_UPDATED'


def test_unauthorised_user_cannot_access_another_org_audit_log():
    service = NotificationAuditService()
    service.create_audit_entry('org-1', 'proj-1', 'user-1', '10.0.0.5', 'MILESTONE_UPDATED', 'project', {'status': 'ACTIVE'}, {'status': 'ARCHIVED'})

    try:
        service.get_audit_history('org-2', 'proj-1')
        raise AssertionError('Expected org isolation failure')
    except PermissionError:
        pass
