import logging
import requests
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, ProposalUtility
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

logger = logging.getLogger(__name__)

class HomeView(APIView):
    """View for the main calculator page."""
    def get(self, request):
        return render(request, 'index.html')

class UtilityRateView(APIView):    
    """API View for fetching and processing utility rates from OpenEI API."""
    
    OPENEI_BASE_URL = "https://api.openei.org/utility_rates"
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.OPENEI_API_KEY
        if not self.api_key:
            logger.error("OPENEI_API_KEY not configured in settings")
        
        # Load curve data from research paper (24 hours, percentage of daily usage)
        self.load_curve = [
            3.5, 2.8, 2.5, 2.3, 2.2, 2.3,  # 12am - 5am
            2.8, 3.8, 4.5, 4.8, 4.7, 4.6,  # 6am - 11am
            4.5, 4.4, 4.3, 4.2, 4.3, 4.6,  # 12pm - 5pm
            5.0, 5.2, 5.0, 4.7, 4.3, 3.9   # 6pm - 11pm
        ]

    def get_utility_rates(self, address: str) -> List[Dict]:
        """Fetch utility rates from OpenEI API."""
        try:
            params = {
            'api_key': self.api_key,
            'address': address,
            'format': 'json',
            'version': 'latest',
            'approved': 'true',
            'is_default': 'true',
            'limit': 50,
            'detail': 'full'
            }
            
            response = requests.get(
                self.OPENEI_BASE_URL,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self.process_rate_data(data)
            else:
                raise requests.RequestException(f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching utility rates: {str(e)}")
            raise

    def process_rate_data(self, api_data: Dict) -> List[Dict]:
        """Process rate data from OpenEI API response."""
        processed_rates = []
        cutoff_date = datetime(2021, 12, 31).timestamp()
        
        for item in api_data.get('items', []):
            # Skip rates that ended before 2022
            if item.get('enddate') and item['enddate'] < cutoff_date:
                continue

            try:
                avg_rate = self.calculate_rate(item)
                
                rate_info = {
                    'label': item.get('label', ''),
                    'utility': item.get('utility', ''),
                    'name': item.get('name', ''),
                    'is_default': item.get('is_default', True),
                    'approved': item.get('approved', True),
                    'startdate': datetime.fromtimestamp(item['startdate']).strftime('%Y-%m-%d') if item.get('startdate') else '',
                    'avg_rate': avg_rate,
                    'energyratestructure': item.get('energyratestructure', []),
                    'energyweekdayschedule': item.get('energyweekdayschedule', []),
                    'fixedchargefirstmeter': item.get('fixedchargefirstmeter', 0),
                    'fixedchargeunits': item.get('fixedchargeunits', '')
                }
                
                processed_rates.append(rate_info)
                
            except Exception as e:
                logger.warning(f"Error processing rate {item.get('name')}: {str(e)}")
                continue
                
        return processed_rates

    def calculate_rate(self, rate_data: Dict) -> float:
        """Calculate the average rate in cents/kWh."""
        try:
            rate_structure = rate_data.get('energyratestructure', [])
            if not rate_structure:
                return 0.0

            rates = []
            for period in rate_structure:
                for tier in period:
                    rate = tier.get('rate', 0)
                    if isinstance(rate, (int, float, Decimal)):
                        rates.append(float(rate))

            return round(sum(rates) / len(rates), 2) if rates else 0.0

        except Exception as e:
            logger.error(f"Error calculating rate: {str(e)}")
            return 0.0

    def calculate_yearly_cost(self, rate_info: Dict, consumption: float, escalator: float) -> List[float]:
        """Calculate yearly costs for 20 years with escalator."""
        try:
            base_rate = rate_info['avg_rate']
            fixed_charge = float(rate_info['fixedchargefirstmeter'])
            
            if rate_info['fixedchargeunits'] == '$/month':
                fixed_charge *= 12
            elif rate_info['fixedchargeunits'] == '$/day':
                fixed_charge *= 365

            yearly_costs = []
            first_year = (consumption * base_rate / 100) + fixed_charge
            
            current_cost = first_year
            for _ in range(20):
                yearly_costs.append(round(current_cost, 2))
                current_cost *= (1 + (escalator / 100))

            return yearly_costs

        except Exception as e:
            logger.error(f"Error calculating yearly costs: {str(e)}")
            return [0] * 20

    def post(self, request):
        """Handle POST requests for utility rate calculations."""
        try:
            address = request.data.get('address')
            consumption = float(request.data.get('consumption', 0))
            escalator = float(request.data.get('escalator', 4))
            selected_rate = request.data.get('selected_rate')

            if not address:
                return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not 1000 <= consumption <= 10000:
                return Response({'error': 'Consumption must be between 1000 and 10000 kWh'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            if not 4 <= escalator <= 10:
                return Response({'error': 'Escalator must be between 4% and 10%'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            rates = self.get_utility_rates(address)
            if not rates:
                return Response({'error': 'No utility rates found'}, status=status.HTTP_404_NOT_FOUND)

            most_likely_rate = next((r for r in rates if r['is_default']), rates[0])
            current_rate = next((r for r in rates if r['label'] == selected_rate), most_likely_rate) if selected_rate else most_likely_rate
            
            yearly_costs = self.calculate_yearly_cost(current_rate, consumption, escalator)

            project = Project.objects.create(
                user=request.user,
                address=address,
                consumption=consumption,
                percentage=escalator
            )

            ProposalUtility.objects.create(
                project=project,
                openei_id=current_rate['label'],
                rate_name=current_rate['name'],
                average_rate=current_rate['avg_rate'],
                first_year_cost=yearly_costs[0]
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
