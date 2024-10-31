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
        
        for item in api_data.get('items', []):
            if item.get('enddate') and item['enddate'] < cutoff_date:
                continue

            try:
                avg_rate = self.calculate_rate(item)
                rate_info = self._extract_rate_info(item, avg_rate)
                processed_rates.append(rate_info)
                
            except Exception as e:
                logger.warning(f"Error processing rate {item.get('name')}: {str(e)}")
                continue
                
        return processed_rates

    def _extract_rate_info(self, item: Dict, avg_rate: float) -> Dict:
        return {
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

    def calculate_rate(self, rate_data: Dict) -> float:
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