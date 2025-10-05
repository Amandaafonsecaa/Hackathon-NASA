from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Literal
from services import physics_service

router = APIRouter()

class SimulationInput(BaseModel):
    diameter_m: float = Field(
        ..., 
        json_schema_extra={'example': 100},
        description="Diâmetro do asteroide em metros."
    )
    velocity_kms: float = Field(
        ..., 
        json_schema_extra={'example': 17},
        description="Velocidade do asteroide em km/s."
    )
    impact_angle_deg: float = Field(
        ..., 
        json_schema_extra={'example': 45},
        description="Ângulo de impacto em graus (90 = vertical)."
    )
    target_type: Literal["solo", "rocha", "oceano"] = Field(
        ..., 
        json_schema_extra={'example': "rocha"},
        description="Tipo de terreno no local do impacto."
    )

@router.post("/", summary="Executar simulação de impacto completa")
def simulate_full_impact(input_data: SimulationInput):
    """
    Calcula todos os efeitos de um impacto de asteroide (cratera, fireball,
    onda de choque, vento e terremoto) e retorna um relatório unificado.
    """
    full_report = physics_service.calculate_all_impact_effects(
        diameter_m=input_data.diameter_m,
        velocity_kms=input_data.velocity_kms,
        impact_angle_deg=input_data.impact_angle_deg,
        tipo_terreno=input_data.target_type
    )
    return full_report