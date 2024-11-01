from decimal import Decimal
import logging
from typing import Dict, Optional
from django.db import transaction
from ..models import Project, ProposalUtility

logger = logging.getLogger(__name__)

class ProjectRepository:
    """Handles project and proposal persistence"""

    @staticmethod
    @transaction.atomic
    def save_project(user, address: str, consumption: float, escalator: float,
                    rate_info: Dict, first_year_cost: float) -> Optional[Project]:
        """
        Save project and associated utility data atomically
        Returns created project or None if save fails
        """
        try:
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
                average_rate=Decimal(str(rate_info['avg_rate'])),  # Convert to Decimal
                first_year_cost=Decimal(str(first_year_cost)),
                pricing_matrix=rate_info.get('energyratestructure', []),
            )

            return project

        except Exception as e:
            logger.error(f"Error saving project: {str(e)}")
            return None
