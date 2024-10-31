import logging
from decimal import Decimal
from typing import Dict, List

logger = logging.getLogger(__name__)

class RateCalculator:
    """
    Rate calculator that processes time-of-use rates against load curves
    to calculate more accurate electricity costs
    """
    
    def __init__(self):
        # Standard load curve (percentage of daily usage per hour)
        self.load_curve = [
            3.5, 2.8, 2.5, 2.3, 2.2, 2.3,  # 12am - 5am
            2.8, 3.8, 4.5, 4.8, 4.7, 4.6,  # 6am - 11am
            4.5, 4.4, 4.3, 4.2, 4.3, 4.6,  # 12pm - 5pm
            5.0, 5.2, 5.0, 4.7, 4.3, 3.9   # 6pm - 11pm
        ]
        # Validate load curve sums to approximately 100%
        total = sum(self.load_curve)
        if not 99.5 <= total <= 100.5:
            logger.warning(f"Load curve percentages sum to {total}, not 100")
            # Normalize to ensure exactly 100%
            self.load_curve = [x * (100/total) for x in self.load_curve]

    def calculate_daily_cost(self, 
                           rate_structure: List[List[Dict]], 
                           weekday_schedule: List[List[int]], 
                           daily_consumption_kwh: float) -> float:
        """
        Calculate daily electricity cost based on TOU rates and load curve
        
        Args:
            rate_structure: List of rate periods, each containing tiers with rates
            weekday_schedule: Hour-by-hour schedule of which rate period applies
            daily_consumption_kwh: Total daily consumption in kWh
        
        Returns:
            float: Total daily cost in dollars
        """
        try:
            hourly_consumption = [
                (percentage/100) * daily_consumption_kwh 
                for percentage in self.load_curve
            ]
            
            daily_cost = 0.0
            
            for hour in range(24):
                # Get the rate period for this hour
                period_index = weekday_schedule[hour // 24][hour % 24]
                
                # Get the rate structure for this period
                period_rates = rate_structure[period_index]
                
                # Find applicable tier and rate based on consumption
                rate = self._get_applicable_rate(period_rates, hourly_consumption[hour])
                
                # Calculate cost for this hour
                hourly_cost = hourly_consumption[hour] * rate
                daily_cost += hourly_cost
                
            return daily_cost

        except Exception as e:
            logger.error(f"Error calculating daily cost: {str(e)}")
            return 0.0

    def _get_applicable_rate(self, 
                           period_rates: List[Dict], 
                           consumption: float) -> float:
        """
        Determine which tier's rate applies based on consumption
        
        Args:
            period_rates: List of tier dictionaries with max usage and rates
            consumption: Consumption value to check against tiers
        
        Returns:
            float: Applicable rate in dollars per kWh
        """
        try:
            for tier in period_rates:
                max_usage = tier.get('max', float('inf'))
                if consumption <= max_usage:
                    rate = tier.get('rate', 0)
                    return float(rate) if isinstance(rate, (int, float, Decimal)) else 0.0
            
            # If no tier matches (shouldn't happen with proper rate structure)
            return float(period_rates[-1]['rate'])

        except Exception as e:
            logger.error(f"Error getting applicable rate: {str(e)}")
            return 0.0

    def calculate_average_rate(self, 
                             rate_structure: List[List[Dict]], 
                             weekday_schedule: List[List[int]], 
                             daily_consumption_kwh: float) -> float:
        """
        Calculate effective average rate per kWh based on load curve and TOU rates
        
        Args:
            rate_structure: List of rate periods, each containing tiers with rates
            weekday_schedule: Hour-by-hour schedule of which rate period applies
            daily_consumption_kwh: Total daily consumption in kWh
            
        Returns:
            float: Average rate in cents per kWh
        """
        try:
            daily_cost = self.calculate_daily_cost(
                rate_structure, 
                weekday_schedule, 
                daily_consumption_kwh
            )
            
            average_rate = (daily_cost / daily_consumption_kwh) * 100  # Convert to cents/kWh
            return round(average_rate, 2)

        except Exception as e:
            logger.error(f"Error calculating average rate: {str(e)}")
            return 0.0

    def calculate_yearly_cost(self, 
                            rate_info: Dict, 
                            yearly_consumption: float, 
                            escalator: float = 2.0) -> List[float]:
        """
        Calculate projected yearly costs including fixed charges and escalation
        
        Args:
            rate_info: Dictionary containing rate structure and schedule
            yearly_consumption: Total yearly consumption in kWh
            escalator: Annual percentage increase in rates
            
        Returns:
            List[float]: Projected costs for next 20 years
        """
        try:
            daily_consumption = yearly_consumption / 365
            
            # Calculate base daily cost using TOU rates
            daily_cost = self.calculate_daily_cost(
                rate_info['energyratestructure'],
                rate_info['energyweekdayschedule'],
                daily_consumption
            )
            
            # Add fixed charges
            fixed_charge = self._calculate_annual_fixed_charge(
                float(rate_info['fixedchargefirstmeter']),
                rate_info['fixedchargeunits']
            )
            
            yearly_base_cost = (daily_cost * 365) + fixed_charge
            
            # Project costs with escalator
            yearly_costs = []
            current_cost = yearly_base_cost
            
            for _ in range(20):
                yearly_costs.append(round(current_cost, 2))
                current_cost *= (1 + (escalator / 100))
                
            return yearly_costs

        except Exception as e:
            logger.error(f"Error calculating yearly costs: {str(e)}")
            return [0] * 20

    def _calculate_annual_fixed_charge(self, charge: float, units: str) -> float:
        """Convert fixed charges to annual amount based on units"""
        if units == '$/month':
            return charge * 12
        elif units == '$/day':
            return charge * 365
        return charge