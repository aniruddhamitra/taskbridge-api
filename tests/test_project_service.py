import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.projects.service import ProjectService


def test_project_created_for_org_and_team():
    service = ProjectService()
    project = service.create_project(
        organisation_id='org-1',
        team_id='team-1',
        name='Alpha',
        status='ACTIVE',
        owner_user_id='user-1',
        members=['user-1', 'user-2', 'user-3'],
    )
    assert project['organisation_id'] == 'org-1'
    assert project['team_id'] == 'team-1'
    assert project['name'] == 'Alpha'


def test_project_status_update_requires_valid_transition():
    service = ProjectService()
    project = service.create_project(
        organisation_id='org-1',
        team_id='team-1',
        name='Alpha',
        status='ACTIVE',
        owner_user_id='user-1',
        members=['user-1', 'user-2'],
    )

    updated = service.update_status(
        organisation_id='org-1',
        project_id=project['id'],
        new_status='ARCHIVED',
        actor_user_id='user-1',
    )
    assert updated['status'] == 'ARCHIVED'

    try:
        service.update_status(
            organisation_id='org-1',
            project_id=project['id'],
            new_status='INVALID',
            actor_user_id='user-1',
        )
        raise AssertionError('Expected validation failure')
    except ValueError:
        pass


def test_project_service_restricts_access_to_org():
    service = ProjectService()
    project = service.create_project(
        organisation_id='org-1',
        team_id='team-1',
        name='Alpha',
        status='ACTIVE',
        owner_user_id='user-1',
        members=['user-1', 'user-2'],
    )

    try:
        service.get_project_by_id('org-2', project['id'], 'user-4')
        raise AssertionError('Expected org isolation failure')
    except PermissionError:
        pass
