import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CostCalculator:
    """Handles cost calculations based on rates and consumption"""
    def calculate_yearly_cost(self, rate_info: Dict, consumption: float, escalator: float) -> List[float]:
        try:
            base_rate = rate_info['avg_rate']
            fixed_charge = self._calculate_annual_fixed_charge(
                float(rate_info['fixedchargefirstmeter']),
                rate_info['fixedchargeunits']
            )

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

    def _calculate_annual_fixed_charge(self, charge: float, units: str) -> float:
        if units == '$/month':
            return charge * 12
        elif units == '$/day':
            return charge * 365
        return charge
