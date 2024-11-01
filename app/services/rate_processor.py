import logging
from typing import Dict, List
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class RateProcessor:
    """Processes raw rate data into standardized format"""
    def process_rate_data(self, api_data: Dict) -> List[Dict]:
        processed_rates = []
        cutoff_date = datetime(2021, 12, 31).timestamp()

        # Sort items by is_default to ensure default rates appear first
        items = sorted(
            api_data.get('items', []),
            key=lambda x: (not x.get('is_default', False), x.get('startdate', 0))
        )

        for item in items:
            if item.get('enddate') and item['enddate'] < cutoff_date:
                continue

            try:
                avg_rate = self.calculate_rate(item)
                rate_info = self._extract_rate_info(item, avg_rate)

                # Only add valid rates (with required fields)
                if rate_info['label'] and rate_info['name'] and rate_info['utility']:
                    processed_rates.append(rate_info)
                else:
                    logger.warning(f"Skipping rate with missing required fields: {item.get('name')}")

            except Exception as e:
                logger.warning(f"Error processing rate {item.get('name')}: {str(e)}")
                continue

        return processed_rates

    def _extract_rate_info(self, item: Dict, avg_rate: float) -> Dict:
        """Extract and validate rate information from API response"""
        try:
            return {
                'label': item.get('label', '').strip(),
                'utility': item.get('utility', '').strip(),
                'name': item.get('name', '').strip(),
                'is_default': bool(item.get('is_default', False)),  # Explicitly convert to boolean
                'approved': bool(item.get('approved', True)),
                'startdate': datetime.fromtimestamp(item['startdate']).strftime('%Y-%m-%d') if item.get('startdate') else '',
                'avg_rate': avg_rate,
                'energyratestructure': item.get('energyratestructure', []),
                'energyweekdayschedule': item.get('energyweekdayschedule', []),
                'fixedchargefirstmeter': Decimal(str(item.get('fixedchargefirstmeter', 0))),
                'fixedchargeunits': item.get('fixedchargeunits', '')
            }
        except Exception as e:
            logger.error(f"Error extracting rate info: {str(e)}")
            raise

    def calculate_rate(self, rate_data: Dict) -> float:
        """Calculate average rate from rate structure"""
        try:
            rate_structure = rate_data.get('energyratestructure', [])
            if not rate_structure:
                return 0.0

            rates = []
            total_weight = 0

            for period in rate_structure:
                for tier in period:
                    rate = tier.get('rate', 0)
                    max_usage = tier.get('max', 1000)  # Default weight if max not specified

                    if isinstance(rate, (int, float, Decimal)):
                        rates.append((float(rate), max_usage))
                        total_weight += max_usage

            # Calculate weighted average
            if rates and total_weight > 0:
                weighted_sum = sum(rate * weight for rate, weight in rates)
                return round(weighted_sum / total_weight, 4)
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating rate: {str(e)}")
            return 0.0
