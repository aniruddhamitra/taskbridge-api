import uuid
from typing import Any, Dict, List

from src.projects.repository import InMemoryProjectRepository


VALID_STATUSES = {'ACTIVE', 'ARCHIVED', 'CLOSED'}


class ProjectService:
    def __init__(self, repository=None):
        self.repository = repository or InMemoryProjectRepository()

    def _validate_project_payload(self, organisation_id: str, team_id: str, name: str, status: str, owner_user_id: str, members: List[str]):
        if not organisation_id or not team_id or not name or not owner_user_id:
            raise ValueError('organisation_id, team_id, name, and owner_user_id are required')
        if status not in VALID_STATUSES:
            raise ValueError(f'Invalid status: {status}')
        if not isinstance(members, list):
            raise ValueError('members must be a list of user IDs')

    def create_project(
        self,
        organisation_id: str,
        team_id: str,
        name: str,
        status: str,
        owner_user_id: str,
        members: List[str],
    ) -> Dict[str, Any]:
        self._validate_project_payload(organisation_id, team_id, name, status, owner_user_id, members)
        project = {
            'id': str(uuid.uuid4()),
            'organisation_id': organisation_id,
            'team_id': team_id,
            'name': name,
            'status': status,
            'owner_user_id': owner_user_id,
            'members': list(dict.fromkeys(members)),
            'metadata': {},
        }
        return self.repository.create(project)

    def get_project_by_id(self, organisation_id: str, project_id: str, actor_user_id: str) -> Dict[str, Any]:
        project = self.repository.get_by_id(project_id, organisation_id)
        if not project:
            raise PermissionError('Project not found or user is not a member of the organisation')
        if actor_user_id not in project['members'] and actor_user_id != project['owner_user_id']:
            raise PermissionError('User does not have access to this project')
        return project

    def get_projects_by_team(self, organisation_id: str, team_id: str, actor_user_id: str) -> List[Dict[str, Any]]:
        projects = self.repository.list_by_team(organisation_id, team_id)
        return [p for p in projects if actor_user_id in p['members'] or actor_user_id == p['owner_user_id']]

    def update_status(
        self,
        organisation_id: str,
        project_id: str,
        new_status: str,
        actor_user_id: str,
    ) -> Dict[str, Any]:
        if new_status not in VALID_STATUSES:
            raise ValueError(f'Invalid status: {new_status}')
        project = self.repository.get_by_id(project_id, organisation_id)
        if not project:
            raise PermissionError('Project not found for organisation')
        if actor_user_id not in project['members'] and actor_user_id != project['owner_user_id']:
            raise PermissionError('User cannot update this project')
        previous = dict(project)
        project['status'] = new_status
        updated = self.repository.update(project_id, organisation_id, {'status': new_status})
        return updated

    def delete_project(self, organisation_id: str, project_id: str, actor_user_id: str) -> None:
        project = self.repository.get_by_id(project_id, organisation_id)
        if not project:
            raise PermissionError('Project not found for organisation')
        if actor_user_id not in project['members'] and actor_user_id != project['owner_user_id']:
            raise PermissionError('User cannot delete this project')
        self.repository.delete(project_id, organisation_id)

    def as_controller_response(self, project: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'id': project['id'],
            'organisation_id': project['organisation_id'],
            'team_id': project['team_id'],
            'name': project['name'],
            'status': project['status'],
            'owner_user_id': project['owner_user_id'],
            'members': project['members'],
        }
