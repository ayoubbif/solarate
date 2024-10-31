import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from ..services.rate_provider import OpenEIRateProvider
from ..services.rate_processor import RateProcessor
from ..services.cost_calculator import CostCalculator
from ..services.input_validator import InputValidator
from ..repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

class UtilityRateView(APIView):
    """API View for handling utility rate calculations"""
    def __init__(self):
        super().__init__()
        self.rate_provider = OpenEIRateProvider(settings.OPENEI_API_KEY)
        self.rate_processor = RateProcessor()
        self.cost_calculator = CostCalculator()
        self.validator = InputValidator()
        self.project_repository = ProjectRepository()

    def post(self, request):
        try:
            # Extract and validate input
            address = request.data.get('address')
            consumption = float(request.data.get('consumption', 0))
            escalator = float(request.data.get('escalator', 4))
            selected_rate = request.data.get('selected_rate')

            validation_error = self.validator.validate_input(address, consumption, escalator)
            if validation_error:
                return Response(validation_error, status=status.HTTP_400_BAD_REQUEST)

            # Fetch and process rates
            raw_rates = self.rate_provider.get_utility_rates(address)
            rates = self.rate_processor.process_rate_data(raw_rates)
            
            if not rates:
                return Response({'error': 'No utility rates found'}, 
                              status=status.HTTP_404_NOT_FOUND)

            # Select appropriate rate
            most_likely_rate = next((r for r in rates if r['is_default']), rates[0])
            current_rate = next((r for r in rates if r['label'] == selected_rate), 
                              most_likely_rate) if selected_rate else most_likely_rate

            # Calculate costs
            yearly_costs = self.cost_calculator.calculate_yearly_cost(
                current_rate, consumption, escalator
            )

            # Save project
            self.project_repository.save_project(
                request.user, address, consumption, escalator,
                current_rate, yearly_costs[0]
            )

            return Response({
                'rates': rates,
                'most_likely_rate': most_likely_rate,
                'selected_rate': current_rate,
                'yearly_costs': yearly_costs,
                'first_year_cost': yearly_costs[0]
            })

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)