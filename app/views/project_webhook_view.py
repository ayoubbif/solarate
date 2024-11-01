import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError

from app.models import Project

logger = logging.getLogger(__name__)

class ProjectWebhookHandler:
    """Handles webhook notifications for project events"""

    def __init__(self):
        self.webhook_url = settings.WEBHOOK_URL
        if not self.webhook_url:
            raise ValueError("WEBHOOK_URL setting is not configured")

    def notify(self, event_type, project_data):
        """
        Send webhook notification for project events

        Args:
            event_type (str): Type of event (e.g., 'project.created')
            project_data (dict): Project data to send in webhook
        """
        try:
            payload = {
                'event': event_type,
                'project': project_data
            }

            logger.info(f"Sending webhook to {self.webhook_url} with payload: {payload}")

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            logger.info(f"Webhook response status: {response.status_code}")
            logger.info(f"Webhook response content: {response.text}")

            if not response.ok:
                logger.error(
                    f"Webhook delivery failed: {response.status_code} - {response.text}"
                )

            return response.ok

        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}", exc_info=True)
            return False

class ProjectAPIView(APIView):
    """API endpoint for project operations"""

    def __init__(self):
        super().__init__()
        self.webhook_handler = ProjectWebhookHandler()

    def post(self, request):
        """Handle POST requests for creating projects"""
        try:
            with transaction.atomic():
                # Extract and validate project data from the request
                project_data = {
                    'address': request.data.get('address'),
                    'consumption': float(request.data.get('consumption', 0)),
                    'percentage': float(request.data.get('escalator', 4)),
                    'name': request.data.get('name'),
                    'description': request.data.get('description'),
                }

                # Validate required fields
                required_fields = ['address', 'consumption', 'name', 'percentage']
                missing_fields = [field for field in required_fields if not project_data.get(field)]

                if missing_fields:
                    return Response(
                        {'error': f"Missing required fields: {', '.join(missing_fields)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Create the project record
                project = Project.objects.create(
                    user=request.user,
                    **project_data
                )

                # Send webhook notification
                webhook_success = self.webhook_handler.notify(
                    'project.created',
                    {
                        'id': project.id,
                        'user_id': request.user.id,
                        **project_data
                    }
                )

                if not webhook_success:
                    logger.warning(f"Webhook delivery failed for project {project.id}")

                return Response({
                    'id': project.id,
                    'message': 'Project created successfully',
                    'webhook_delivered': webhook_success
                }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Invalid data', 'details': e.message_dict},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred while creating the project'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
