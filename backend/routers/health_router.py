from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from services import health_infrastructure_service

router = APIRouter()

class HealthCapacityRequest(BaseModel):
    lat: float = Field(..., description="Latitude do centro da análise")
    lon: float = Field(..., description="Longitude do centro da análise")
    radius_km: float = Field(default=50, description="Raio da região em km")

class HealthFacilitiesMapRequest(BaseModel):
    bbox: Tuple[float, float, float, float] = Field(..., description="Bounding box (min_lon, min_lat, max_lon, max_lat)")

@router.post("/capacity-analysis", summary="Análise de capacidade de infraestrutura de saúde")
def get_health_capacity_analysis(request: HealthCapacityRequest) -> Dict:
    """
    Obtém análise completa de capacidade de infraestrutura de saúde.
    
    Inclui:
    - Capacidade hospitalar atual
    - Ocupação de leitos
    - Equipamentos disponíveis
    - Capacidade para emergências
    - Avaliação de vulnerabilidade
    - Recomendações de mitigação
    """
    try:
        capacity_analysis = health_infrastructure_service.get_health_capacity_by_region(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km
        )
        
        return capacity_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de capacidade de saúde: {str(e)}")

@router.get("/capacity-analysis", summary="Análise de capacidade de infraestrutura de saúde (GET)")
def get_health_capacity_analysis_get(
    lat: float = Query(..., description="Latitude do centro da análise"),
    lon: float = Query(..., description="Longitude do centro da análise"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém análise completa de capacidade de infraestrutura de saúde.
    """
    try:
        capacity_analysis = health_infrastructure_service.get_health_capacity_by_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        return capacity_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de capacidade de saúde: {str(e)}")

@router.post("/facilities-map", summary="Mapa de instalações de saúde")
def get_health_facilities_map(request: HealthFacilitiesMapRequest) -> Dict:
    """
    Gera mapa de instalações de saúde para uma área específica.
    
    Inclui:
    - Hospitais e suas capacidades
    - Clínicas e especialidades
    - Farmácias e medicamentos de emergência
    - Estatísticas de distribuição
    """
    try:
        facilities_map = health_infrastructure_service.get_health_facilities_map(
            bbox=request.bbox
        )
        
        return facilities_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mapa de instalações: {str(e)}")

@router.get("/facilities-map", summary="Mapa de instalações de saúde (GET)")
def get_health_facilities_map_get(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima")
) -> Dict:
    """
    Gera mapa de instalações de saúde para uma área específica.
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        facilities_map = health_infrastructure_service.get_health_facilities_map(
            bbox=bbox
        )
        
        return facilities_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mapa de instalações: {str(e)}")

@router.get("/emergency-response-time", summary="Tempo de resposta de emergência")
def get_emergency_response_time(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    emergency_type: str = Query(default="medical", description="Tipo de emergência (medical, fire, police)")
) -> Dict:
    """
    Calcula tempo de resposta de emergência para uma localização.
    
    Considera:
    - Fatores de localização
    - Tráfego e condições de estrada
    - Disponibilidade de recursos
    - Nível de resposta
    """
    try:
        response_time = health_infrastructure_service.get_emergency_response_time(
            lat=lat,
            lon=lon,
            emergency_type=emergency_type
        )
        
        return response_time
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular tempo de resposta: {str(e)}")

@router.get("/hospital-capacity", summary="Capacidade hospitalar em tempo real")
def get_hospital_capacity(
    lat: float = Query(..., description="Latitude do centro"),
    lon: float = Query(..., description="Longitude do centro"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém capacidade hospitalar em tempo real.
    
    Inclui:
    - Leitos disponíveis
    - Ocupação atual
    - Leitos de UTI
    - Ventiladores disponíveis
    - Salas de cirurgia
    - Ambulâncias
    """
    try:
        capacity_data = health_infrastructure_service.get_health_capacity_by_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        if not capacity_data.get("success"):
            return capacity_data
        
        # Extrair dados específicos de capacidade hospitalar
        hospital_data = capacity_data.get("health_infrastructure", {}).get("hospitals", {})
        current_occupancy = capacity_data.get("current_occupancy", {}).get("hospitals", {})
        emergency_capacity = capacity_data.get("emergency_capacity", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "hospital_capacity": {
                "total_hospitals": hospital_data.get("count", 0),
                "total_beds": hospital_data.get("total_beds", 0),
                "available_beds": current_occupancy.get("available_beds", 0),
                "occupied_beds": current_occupancy.get("occupied_beds", 0),
                "occupancy_rate": current_occupancy.get("bed_occupancy_rate", 0),
                "icu_beds": {
                    "total": hospital_data.get("icu_beds", 0),
                    "available": emergency_capacity.get("hospitalization", {}).get("icu_beds_available", 0),
                    "occupancy_rate": current_occupancy.get("icu_occupancy_rate", 0)
                },
                "emergency_beds": {
                    "total": hospital_data.get("emergency_beds", 0),
                    "available": emergency_capacity.get("immediate_care", {}).get("emergency_beds_available", 0),
                    "occupancy_rate": current_occupancy.get("emergency_occupancy_rate", 0)
                },
                "ventilators": {
                    "total": hospital_data.get("ventilators", 0),
                    "available": emergency_capacity.get("hospitalization", {}).get("ventilators_available", 0)
                },
                "surgery_rooms": hospital_data.get("surgery_rooms", 0),
                "ambulances": {
                    "total": hospital_data.get("ambulances", 0),
                    "available": emergency_capacity.get("immediate_care", {}).get("ambulances_available", 0)
                }
            },
            "capacity_assessment": emergency_capacity.get("overall_capacity_assessment", {}),
            "timestamp": capacity_data.get("data_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter capacidade hospitalar: {str(e)}")

@router.get("/medical-evacuation-capacity", summary="Capacidade de evacuação médica")
def get_medical_evacuation_capacity(
    lat: float = Query(..., description="Latitude do centro"),
    lon: float = Query(..., description="Longitude do centro"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém capacidade de evacuação médica para emergências.
    
    Inclui:
    - Capacidade de evacuação médica
    - Cuidados críticos disponíveis
    - Equipamentos especializados
    - Tempo de resposta
    - Recomendações
    """
    try:
        capacity_data = health_infrastructure_service.get_health_capacity_by_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        if not capacity_data.get("success"):
            return capacity_data
        
        # Extrair dados de evacuação médica
        evacuation_capacity = capacity_data.get("emergency_capacity", {}).get("evacuation_medical", {})
        vulnerability_assessment = capacity_data.get("vulnerability_assessment", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "medical_evacuation_capacity": evacuation_capacity,
            "vulnerability_assessment": vulnerability_assessment,
            "recommendations": capacity_data.get("emergency_capacity", {}).get("overall_capacity_assessment", {}).get("recommendations", []),
            "timestamp": capacity_data.get("data_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter capacidade de evacuação médica: {str(e)}")

@router.get("/health-statistics", summary="Estatísticas de saúde globais")
def get_health_statistics() -> Dict:
    """
    Obtém estatísticas globais de infraestrutura de saúde.
    
    Inclui padrões de:
    - Capacidade hospitalar por região
    - Distribuição de especialidades
    - Equipamentos médicos
    - Tempos de resposta
    """
    try:
        # Obter dados simulados
        health_data = health_infrastructure_service.simulated_health_data
        
        global_stats = {
            "hospital_capacity": {
                "global_beds_per_1000": health_data["hospitals"]["capacity_per_1000"],
                "specialties_available": health_data["hospitals"]["specialties"],
                "equipment_per_hospital": health_data["hospitals"]["equipment_per_hospital"]
            },
            "clinic_capacity": {
                "global_capacity_per_1000": health_data["clinics"]["capacity_per_1000"],
                "clinic_types": health_data["clinics"]["types"]
            },
            "emergency_services": {
                "global_response_time_minutes": health_data["emergency_services"]["response_time_minutes"],
                "ambulances_per_100k": health_data["emergency_services"]["ambulances_per_100k"],
                "paramedics_per_100k": health_data["emergency_services"]["paramedics_per_100k"]
            },
            "pharmaceutical": {
                "pharmacies_per_1000": health_data["pharmaceutical"]["pharmacies_per_1000"],
                "emergency_medications": health_data["pharmaceutical"]["emergency_medications"]
            }
        }
        
        return {
            "success": True,
            "global_health_statistics": global_stats,
            "data_source": "Simulated Global Health Infrastructure",
            "note": "Dados simulados para demonstração. Em produção, usar dados reais de saúde pública.",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas de saúde: {str(e)}")