from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from services import health_monitoring_service, air_quality_service, atmospheric_service

router = APIRouter()

class HealthMonitoringRequest(BaseModel):
    impact_latitude: float = Field(..., description="Latitude do ponto de impacto")
    impact_longitude: float = Field(..., description="Longitude do ponto de impacto")
    diameter_m: float = Field(..., description="Diâmetro do asteroide em metros")
    velocity_kms: float = Field(..., description="Velocidade do asteroide em km/s")
    impact_angle_deg: float = Field(default=45, description="Ângulo de impacto em graus")
    target_type: str = Field(default="rocha", description="Tipo de terreno (solo, rocha, oceano)")
    wind_speed_ms: float = Field(default=10, description="Velocidade do vento em m/s")
    wind_direction_deg: float = Field(default=0, description="Direção do vento em graus")
    time_since_impact_hours: float = Field(default=0, description="Tempo desde o impacto em horas")

@router.post("/monitor-post-impact", summary="Monitorar condições de saúde pós-impacto")
def monitor_post_impact_health(request: HealthMonitoringRequest) -> Dict:
    """
    Monitora condições de saúde pós-impacto de asteroide.
    
    Analisa:
    - Impacto na qualidade do ar
    - Riscos à saúde por grupo populacional
    - Alertas de saúde
    - Recomendações de saúde
    - População afetada
    """
    try:
        # Executar simulação de impacto
        from services import physics_service
        impact_data = physics_service.calculate_all_impact_effects(
            diameter_m=request.diameter_m,
            velocity_kms=request.velocity_kms,
            impact_angle_deg=request.impact_angle_deg,
            tipo_terreno=request.target_type,
            wind_speed_ms=request.wind_speed_ms,
            wind_direction_deg=request.wind_direction_deg
        )
        
        # Obter dados de qualidade do ar
        air_quality_data = air_quality_service.get_airnow_data(
            request.impact_latitude, 
            request.impact_longitude
        )
        
        # Executar monitoramento de saúde
        health_monitoring = health_monitoring_service.monitor_post_impact_health(
            impact_coordinates=(request.impact_latitude, request.impact_longitude),
            impact_data=impact_data,
            air_quality_data=air_quality_data.get("data", {}),
            time_since_impact_hours=request.time_since_impact_hours
        )
        
        return health_monitoring
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no monitoramento de saúde: {str(e)}")

@router.get("/air-quality/current", summary="Obter qualidade do ar atual")
def get_current_air_quality(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de qualidade do ar atual para uma localização.
    """
    try:
        air_quality_data = air_quality_service.get_airnow_data(latitude, longitude, date)
        return air_quality_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter qualidade do ar: {str(e)}")

@router.get("/air-quality/validate", summary="Validar dados de qualidade do ar")
def validate_air_quality_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Valida dados de qualidade do ar comparando múltiplas fontes.
    """
    try:
        validation_result = air_quality_service.validate_air_quality_data(latitude, longitude, date)
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na validação de dados: {str(e)}")

@router.get("/atmospheric/conditions", summary="Obter condições atmosféricas")
def get_atmospheric_conditions(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém condições atmosféricas (vento, temperatura, pressão) para uma localização.
    """
    try:
        atmospheric_data = atmospheric_service.get_merra2_data(latitude, longitude, date)
        return atmospheric_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter condições atmosféricas: {str(e)}")

@router.get("/atmospheric/precipitation", summary="Obter dados de precipitação")
def get_precipitation_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de precipitação para uma localização.
    """
    try:
        precipitation_data = atmospheric_service.get_gpm_precipitation(latitude, longitude, date)
        return precipitation_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de precipitação: {str(e)}")

@router.get("/atmospheric/dispersion", summary="Analisar condições de dispersão atmosférica")
def analyze_dispersion_conditions(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Analisa condições atmosféricas para modelagem de dispersão de poluentes.
    """
    try:
        dispersion_analysis = atmospheric_service.get_atmospheric_dispersion_conditions(
            latitude, longitude, date
        )
        return dispersion_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de dispersão: {str(e)}")

@router.get("/health-thresholds", summary="Obter limiares de saúde")
def get_health_thresholds() -> Dict:
    """
    Retorna limiares de saúde para diferentes poluentes.
    """
    try:
        thresholds = health_monitoring_service.health_thresholds
        sensitive_groups = health_monitoring_service.sensitive_groups
        
        return {
            "success": True,
            "health_thresholds": thresholds,
            "sensitive_groups": sensitive_groups,
            "description": "Limiares baseados em padrões internacionais de qualidade do ar"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter limiares de saúde: {str(e)}")

@router.get("/health-alerts/types", summary="Listar tipos de alertas de saúde")
def get_health_alert_types() -> Dict:
    """
    Retorna informações sobre os tipos de alertas de saúde disponíveis.
    """
    alert_types = {
        "EMERGENCY": {
            "name": "Alerta de Emergência",
            "priority": "HIGH",
            "description": "Condições perigosas que requerem ação imediata",
            "trigger_conditions": ["AQI > 200", "Poluentes críticos", "Exposição prolongada"]
        },
        "SENSITIVE_GROUPS": {
            "name": "Alerta para Grupos Sensíveis",
            "priority": "MEDIUM",
            "description": "Alertas específicos para grupos vulneráveis",
            "trigger_conditions": ["AQI > 150", "Poluentes moderados", "Grupos de risco"]
        },
        "IMMEDIATE_POST_IMPACT": {
            "name": "Período Crítico Pós-Impacto",
            "priority": "HIGH",
            "description": "Primeiras horas após o impacto são críticas",
            "trigger_conditions": ["< 6 horas pós-impacto", "Concentração máxima de poluentes"]
        }
    }
    
    return {
        "success": True,
        "total_alert_types": len(alert_types),
        "alert_types": alert_types
    }

@router.post("/health-recommendations", summary="Gerar recomendações de saúde")
def generate_health_recommendations(
    aqi_level: float = Query(..., description="Nível de AQI"),
    population_type: str = Query(default="general", description="Tipo de população (general, sensitive)"),
    time_exposed_hours: float = Query(default=1, description="Tempo de exposição em horas")
) -> Dict:
    """
    Gera recomendações de saúde baseadas em níveis de poluição e exposição.
    """
    try:
        # Simular dados de poluentes baseados no AQI
        pollutants = {
            "PM2_5": {"value": aqi_level * 0.35, "unit": "μg/m³"},
            "PM10": {"value": aqi_level * 0.5, "unit": "μg/m³"},
            "NO2": {"value": aqi_level * 0.2, "unit": "ppb"},
            "O3": {"value": aqi_level * 0.7, "unit": "ppb"}
        }
        
        # Calcular AQI
        new_aqi = {"value": aqi_level, "category": "Unknown"}
        
        # Avaliar riscos
        health_risks = health_monitoring_service._assess_health_risks({"new_aqi": new_aqi})
        
        # Gerar recomendações
        health_recommendations = health_monitoring_service._generate_health_recommendations(
            health_risks, {}, time_exposed_hours
        )
        
        return {
            "success": True,
            "aqi_level": aqi_level,
            "population_type": population_type,
            "time_exposed_hours": time_exposed_hours,
            "health_risks": health_risks,
            "recommendations": health_recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")
