from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List
from services import geojson_service, physics_service

router = APIRouter()

class ImpactCoordinates(BaseModel):
    latitude: float = Field(..., description="Latitude do ponto de impacto")
    longitude: float = Field(..., description="Longitude do ponto de impacto")

class SimulationWithLocation(BaseModel):
    latitude: float = Field(..., description="Latitude do ponto de impacto")
    longitude: float = Field(..., description="Longitude do ponto de impacto")
    diameter_m: float = Field(..., description="Diâmetro do asteroide em metros")
    velocity_kms: float = Field(..., description="Velocidade do asteroide em km/s")
    impact_angle_deg: float = Field(..., description="Ângulo de impacto em graus")
    target_type: str = Field(..., description="Tipo de terreno (solo, rocha, oceano)")
    wind_speed_ms: float = Field(default=10, description="Velocidade do vento em m/s")
    wind_direction_deg: float = Field(default=0, description="Direção do vento em graus")

@router.post("/risk-zones", summary="Gerar zonas de risco GeoJSON")
def generate_risk_zones_geojson(simulation_data: SimulationWithLocation) -> Dict:
    """
    Gera todas as zonas de risco em formato GeoJSON baseadas na simulação de impacto.
    
    Retorna polígonos para:
    - Zona da cratera
    - Zonas de queimadura térmica
    - Zonas de sobrepressão (onda de choque)
    - Zona de tremor sísmico
    - Zona de tsunami (se aplicável)
    - Zona de dispersão atmosférica (se aplicável)
    """
    try:
        # Executar simulação física
        physics_results = physics_service.calculate_all_impact_effects(
            diameter_m=simulation_data.diameter_m,
            velocity_kms=simulation_data.velocity_kms,
            impact_angle_deg=simulation_data.impact_angle_deg,
            tipo_terreno=simulation_data.target_type,
            wind_speed_ms=simulation_data.wind_speed_ms,
            wind_direction_deg=simulation_data.wind_direction_deg
        )
        
        # Gerar zonas de risco GeoJSON
        risk_zones = geojson_service.generate_impact_risk_zones(
            impact_lat=simulation_data.latitude,
            impact_lon=simulation_data.longitude,
            physics_results=physics_results
        )
        
        return {
            "success": True,
            "impact_coordinates": [simulation_data.longitude, simulation_data.latitude],
            "simulation_summary": {
                "energy_megatons": physics_results["energia"]["equivalente_tnt_megatons"],
                "crater_diameter_km": physics_results["cratera"]["diametro_final_km"],
                "earthquake_magnitude": physics_results["terremoto"]["magnitude_richter"],
                "is_airburst": physics_results["fireball"]["is_airburst"],
                "tsunami_generated": physics_results["tsunami"]["tsunami_generated"]
            },
            "geojson": risk_zones
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar zonas de risco: {str(e)}")

@router.post("/evacuation-zones", summary="Gerar zonas de evacuação GeoJSON")
def generate_evacuation_zones_geojson(simulation_data: SimulationWithLocation, buffer_km: float = 5.0) -> Dict:
    """
    Gera zonas de evacuação em formato GeoJSON baseadas nas zonas de risco.
    
    Args:
        simulation_data: Dados da simulação de impacto
        buffer_km: Buffer adicional em km para evacuação (padrão: 5.0 km)
    """
    try:
        # Executar simulação física
        physics_results = physics_service.calculate_all_impact_effects(
            diameter_m=simulation_data.diameter_m,
            velocity_kms=simulation_data.velocity_kms,
            impact_angle_deg=simulation_data.impact_angle_deg,
            tipo_terreno=simulation_data.target_type,
            wind_speed_ms=simulation_data.wind_speed_ms,
            wind_direction_deg=simulation_data.wind_direction_deg
        )
        
        # Gerar zonas de risco primeiro
        risk_zones = geojson_service.generate_impact_risk_zones(
            impact_lat=simulation_data.latitude,
            impact_lon=simulation_data.longitude,
            physics_results=physics_results
        )
        
        # Gerar zonas de evacuação baseadas nas zonas de risco
        evacuation_zones = geojson_service.generate_evacuation_zones(
            risk_zones_geojson=risk_zones,
            buffer_km=buffer_km
        )
        
        return {
            "success": True,
            "impact_coordinates": [simulation_data.longitude, simulation_data.latitude],
            "buffer_km": buffer_km,
            "risk_zones_count": len(risk_zones["features"]),
            "evacuation_zones_count": len(evacuation_zones["features"]),
            "risk_zones_geojson": risk_zones,
            "evacuation_zones_geojson": evacuation_zones
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar zonas de evacuação: {str(e)}")

@router.get("/zone-types", summary="Listar tipos de zonas de risco disponíveis")
def get_zone_types() -> Dict:
    """
    Retorna informações sobre todos os tipos de zonas de risco que podem ser geradas.
    """
    zone_types = {
        "crater": {
            "name": "Zona da Cratera",
            "description": "Área diretamente afetada pela cratera de impacto",
            "risk_level": "critical",
            "color": "#8B0000"
        },
        "thermal_burn": {
            "name": "Zonas de Queimadura Térmica",
            "description": "Áreas afetadas pela radiação térmica do fireball",
            "risk_levels": ["high", "moderate", "low"],
            "colors": ["#FF4500", "#FF8C00", "#FFA500"]
        },
        "blast_overpressure": {
            "name": "Zonas de Sobrepressão",
            "description": "Áreas afetadas pela onda de choque",
            "risk_levels": ["critical", "high", "moderate"],
            "colors": ["#DC143C", "#FF6347", "#FFB6C1"]
        },
        "seismic_shaking": {
            "name": "Zona de Tremor Sísmico",
            "description": "Área onde o tremor do impacto será sentido",
            "risk_level": "moderate",
            "color": "#8B4513"
        },
        "tsunami_impact": {
            "name": "Zona de Impacto do Tsunami",
            "description": "Área afetada pelo tsunami (impactos oceânicos)",
            "risk_level": "critical",
            "color": "#0066CC"
        },
        "atmospheric_plume": {
            "name": "Pluma de Poluentes Atmosféricos",
            "description": "Área de dispersão de poluentes após airburst",
            "risk_level": "moderate",
            "color": "#9370DB"
        },
        "evacuation": {
            "name": "Zona de Evacuação",
            "description": "Área recomendada para evacuação com buffer de segurança",
            "risk_level": "evacuation",
            "color": "#FFD700"
        }
    }
    
    return {
        "success": True,
        "total_zone_types": len(zone_types),
        "zone_types": zone_types
    }
