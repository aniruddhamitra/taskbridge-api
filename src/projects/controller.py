from typing import Any, Dict, List

from src.projects.service import ProjectService


class ProjectController:
    def __init__(self, service: ProjectService):
        self.service = service

    def create(self, organisation_id: str, team_id: str, name: str, status: str, owner_user_id: str, members: List[str]) -> Dict[str, Any]:
        project = self.service.create_project(organisation_id, team_id, name, status, owner_user_id, members)
        return self.service.as_controller_response(project)

    def get_by_id(self, organisation_id: str, project_id: str, actor_user_id: str) -> Dict[str, Any]:
        project = self.service.get_project_by_id(organisation_id, project_id, actor_user_id)
        return self.service.as_controller_response(project)

    def list_by_team(self, organisation_id: str, team_id: str, actor_user_id: str) -> List[Dict[str, Any]]:
        projects = self.service.get_projects_by_team(organisation_id, team_id, actor_user_id)
        return [self.service.as_controller_response(p) for p in projects]

    def update_status(self, organisation_id: str, project_id: str, new_status: str, actor_user_id: str) -> Dict[str, Any]:
        project = self.service.update_status(organisation_id, project_id, new_status, actor_user_id)
        return self.service.as_controller_response(project)

    def delete(self, organisation_id: str, project_id: str, actor_user_id: str) -> Dict[str, str]:
        self.service.delete_project(organisation_id, project_id, actor_user_id)
        return {'status': 'deleted', 'project_id': project_id}
