import logging
from typing import Dict, List
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from ..services.rate_provider import OpenEIRateProvider
from ..services.rate_processor import RateProcessor
from ..services.rate_calculator import RateCalculator
from ..services.input_validator import InputValidator
from ..repositories.project_repository import ProjectRepository

logger = logging.getLogger(__name__)

class UtilityRateView(APIView):
    """
    API View for handling utility rate calculations
    """
    def __init__(self):
        super().__init__()
        self.rate_provider = OpenEIRateProvider(settings.OPENEI_API_KEY)
        self.rate_processor = RateProcessor()
        self.rate_calculator = RateCalculator()
        self.validator = InputValidator()
        self.project_repository = ProjectRepository()

    def post(self, request):
        """
        Handle POST requests for utility rate calculations
        Incorporates time-of-use rates and load curve analysis
        """
        try:
            # Extract and validate input
            address = request.data.get('address')
            yearly_consumption = float(request.data.get('consumption', 0))
            daily_consumption = yearly_consumption / 365
            escalator = float(request.data.get('escalator', 4))
            selected_rate = request.data.get('selected_rate')

            # Validate input
            validation_error = self.validator.validate_input(
                address, yearly_consumption, escalator
            )
            if validation_error:
                return Response(
                    validation_error,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch and process rates
            raw_rates = self.rate_provider.get_utility_rates(address)
            rates = self.rate_processor.process_rate_data(raw_rates)

            if not rates:
                return Response(
                    {'error': 'No utility rates found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Select appropriate rate plan
            most_likely_rate = next(
                (r for r in rates if r['is_default']),
                rates[0]
            )
            current_rate = next(
                (r for r in rates if r['label'] == selected_rate),
                most_likely_rate
            ) if selected_rate else most_likely_rate

            # Calculate costs using enhanced calculator
            yearly_costs = self.rate_calculator.calculate_yearly_cost(
                current_rate,
                yearly_consumption,
                escalator
            )

            # Calculate average rate using load curve
            effective_rate = self.rate_calculator.calculate_average_rate(
                current_rate['energyratestructure'],
                current_rate['energyweekdayschedule'],
                daily_consumption
            )

            # Calculate daily cost breakdown
            daily_cost = self.rate_calculator.calculate_daily_cost(
                current_rate['energyratestructure'],
                current_rate['energyweekdayschedule'],
                daily_consumption
            )

            # Add enhanced rate information to each rate option
            rates_with_analysis = self._add_rate_analysis(
                rates,
                daily_consumption
            )

            # Save project with enhanced details
            self.project_repository.save_project(
                request.user,
                address,
                yearly_consumption,
                escalator,
                current_rate,
                yearly_costs[0]
            )

            return Response({
                'rates': rates_with_analysis,
                'most_likely_rate': most_likely_rate,
                'selected_rate': current_rate,
                'yearly_costs': yearly_costs,
                'first_year_cost': yearly_costs[0],
                'effective_rate': effective_rate,
                'daily_cost': daily_cost,
                'load_curve': self.rate_calculator.load_curve
            })

        except Exception as e:
            logger.error(
                f"Error processing request: {str(e)}",
                exc_info=True
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _add_rate_analysis(
        self,
        rates: List[Dict],
        daily_consumption: float
    ) -> List[Dict]:
        """
        Add detailed rate analysis to each rate option
        """
        try:
            analyzed_rates = []
            for rate in rates:
                rate_copy = rate.copy()
                
                # Calculate effective rate for this plan
                effective_rate = self.rate_calculator.calculate_average_rate(
                    rate['energyratestructure'],
                    rate['energyweekdayschedule'],
                    daily_consumption
                )
                
                # Calculate daily cost for this plan
                daily_cost = self.rate_calculator.calculate_daily_cost(
                    rate['energyratestructure'],
                    rate['energyweekdayschedule'],
                    daily_consumption
                )
                
                rate_copy.update({
                    'effective_rate': effective_rate,
                    'daily_cost': daily_cost
                })
                analyzed_rates.append(rate_copy)
                
            return analyzed_rates
            
        except Exception as e:
            logger.error(
                f"Error adding rate analysis: {str(e)}",
                exc_info=True
            )
            return rates