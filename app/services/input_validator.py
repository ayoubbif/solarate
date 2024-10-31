from typing import Dict, Optional

class InputValidator:
    """Validates user input for rate calculations"""
    @staticmethod
    def validate_input(address: str, consumption: float, escalator: float) -> Optional[Dict]:
        if not address:
            return {'error': 'Address is required'}
        if not 1000 <= consumption <= 10000:
            return {'error': 'Consumption must be between 1000 and 10000 kWh'}
        if not 4 <= escalator <= 10:
            return {'error': 'Escalator must be between 4% and 10%'}
        return None
