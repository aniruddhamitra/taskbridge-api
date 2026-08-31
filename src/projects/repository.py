from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ProjectRepository(ABC):
    @abstractmethod
    def create(self, project: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, project_id: str, organisation_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def list_by_team(self, organisation_id: str, team_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update(self, project_id: str, organisation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: str, organisation_id: str) -> None:
        raise NotImplementedError


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self):
        self._projects: Dict[str, Dict[str, Any]] = {}

    def create(self, project: Dict[str, Any]) -> Dict[str, Any]:
        self._projects[project['id']] = project
        return project

    def get_by_id(self, project_id: str, organisation_id: str) -> Optional[Dict[str, Any]]:
        project = self._projects.get(project_id)
        if project and project['organisation_id'] == organisation_id:
            return project
        return None

    def list_by_team(self, organisation_id: str, team_id: str) -> List[Dict[str, Any]]:
        return [
            p for p in self._projects.values()
            if p['organisation_id'] == organisation_id and p['team_id'] == team_id
        ]

    def update(self, project_id: str, organisation_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        project = self.get_by_id(project_id, organisation_id)
        if not project:
            raise KeyError('Project not found for organisation')
        project.update(updates)
        return project

    def delete(self, project_id: str, organisation_id: str) -> None:
        project = self.get_by_id(project_id, organisation_id)
        if not project:
            raise KeyError('Project not found for organisation')
        del self._projects[project_id]
