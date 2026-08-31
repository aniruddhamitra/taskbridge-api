from typing import Any, Dict, List, Optional


class Project:
    def __init__(
        self,
        id: str,
        organisation_id: str,
        team_id: str,
        name: str,
        status: str,
        owner_user_id: str,
        members: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.organisation_id = organisation_id
        self.team_id = team_id
        self.name = name
        self.status = status
        self.owner_user_id = owner_user_id
        self.members = members or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'organisation_id': self.organisation_id,
            'team_id': self.team_id,
            'name': self.name,
            'status': self.status,
            'owner_user_id': self.owner_user_id,
            'members': self.members,
            'metadata': self.metadata,
        }
