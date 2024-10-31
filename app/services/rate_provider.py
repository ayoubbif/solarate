from abc import ABC, abstractmethod
import logging
from typing import Dict, List
import requests

logger = logging.getLogger(__name__)

class RateDataProvider(ABC):
    """Abstract interface for rate data providers"""
    @abstractmethod
    def get_utility_rates(self, address: str) -> List[Dict]:
        pass

class OpenEIRateProvider(RateDataProvider):
    """Implementation of RateDataProvider for OpenEI API"""
    OPENEI_BASE_URL = "https://api.openei.org/utility_rates"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            logger.error("OPENEI_API_KEY not configured")

    def get_utility_rates(self, address: str) -> List[Dict]:
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
                return response.json()
            raise requests.RequestException(f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching utility rates: {str(e)}")
            raise