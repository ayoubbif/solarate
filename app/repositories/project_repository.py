from typing import Dict
from ..models import Project, ProposalUtility

class ProjectRepository:
    """Handles project and proposal persistence"""
    @staticmethod
    def save_project(user, address: str, consumption: float, escalator: float,
                    rate_info: Dict, first_year_cost: float) -> None:
        project = Project.objects.create(
            user=user,
            address=address,
            consumption=consumption,
            percentage=escalator,
            selected_rate=rate_info['name']
        )

        ProposalUtility.objects.create(
            project=project,
            openei_id=rate_info['label'],
            rate_name=rate_info['name'],
            average_rate=rate_info['avg_rate'],
            first_year_cost=first_year_cost,
            pricing_matrix=rate_info.get('energyratestructure'),
        )
