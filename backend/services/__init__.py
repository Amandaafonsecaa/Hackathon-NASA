# Importações básicas dos serviços
from .population_service import population_service
from .health_infrastructure_service import health_infrastructure_service
from .civil_defense_service import civil_defense_service

__all__ = [
    'population_service',
    'health_infrastructure_service', 
    'civil_defense_service'
]