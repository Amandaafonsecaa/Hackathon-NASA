from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from services import evacuation_service, physics_service, geojson_service

router = APIRouter()

class EvacuationPoint(BaseModel):
    name: str = Field(..., description="Nome do ponto de evacuação")
    type: str = Field(default="shelter", description="Tipo (shelter, hospital, safe_zone)")
    capacity: int = Field(default=100, description="Capacidade de pessoas")
    latitude: float = Field(..., description="Latitude do ponto")
    longitude: float = Field(..., description="Longitude do ponto")

class EvacuationRequest(BaseModel):
    impact_latitude: float = Field(..., description="Latitude do ponto de impacto")
    impact_longitude: float = Field(..., description="Longitude do ponto de impacto")
    diameter_m: float = Field(..., description="Diâmetro do asteroide em metros")
    velocity_kms: float = Field(..., description="Velocidade do asteroide em km/s")
    impact_angle_deg: float = Field(default=45, description="Ângulo de impacto em graus")
    target_type: str = Field(default="rocha", description="Tipo de terreno (solo, rocha, oceano)")
    wind_speed_ms: float = Field(default=10, description="Velocidade do vento em m/s")
    wind_direction_deg: float = Field(default=0, description="Direção do vento em graus")
    evacuation_points: List[EvacuationPoint] = Field(..., description="Lista de pontos de evacuação")
    transport_mode: str = Field(default="car", description="Modo de transporte (car, ambulance, pedestrian)")
    buffer_km: float = Field(default=5.0, description="Buffer adicional em km para evitar zonas de risco")

@router.post("/calculate-routes", summary="Calcular rotas de evacuação otimizadas")
def calculate_evacuation_routes(request: EvacuationRequest) -> Dict:
    """
    Calcula rotas de evacuação otimizadas baseadas em simulação de impacto.
    
    O sistema:
    1. Executa simulação de impacto completa
    2. Gera zonas de risco GeoJSON
    3. Calcula rotas otimizadas evitando zonas de risco
    4. Retorna rotas ordenadas por prioridade
    """
    try:
        # Executar simulação de impacto
        physics_results = physics_service.calculate_all_impact_effects(
            diameter_m=request.diameter_m,
            velocity_kms=request.velocity_kms,
            impact_angle_deg=request.impact_angle_deg,
            tipo_terreno=request.target_type,
            wind_speed_ms=request.wind_speed_ms,
            wind_direction_deg=request.wind_direction_deg
        )
        
        # Gerar zonas de risco GeoJSON
        risk_zones = geojson_service.generate_impact_risk_zones(
            impact_lat=request.impact_latitude,
            impact_lon=request.impact_longitude,
            physics_results=physics_results
        )
        
        # Converter pontos de evacuação para formato interno
        evacuation_points = []
        for point in request.evacuation_points:
            evacuation_points.append({
                "name": point.name,
                "type": point.type,
                "capacity": point.capacity,
                "latitude": point.latitude,
                "longitude": point.longitude
            })
        
        # Calcular rotas de evacuação
        evacuation_results = evacuation_service.calculate_evacuation_routes(
            start_lat=request.impact_latitude,
            start_lon=request.impact_longitude,
            risk_zones_geojson=risk_zones,
            evacuation_points=evacuation_points,
            transport_mode=request.transport_mode,
            buffer_km=request.buffer_km
        )
        
        if not evacuation_results["success"]:
            raise HTTPException(status_code=500, detail=evacuation_results["error"])
        
        return {
            "success": True,
            "impact_simulation": {
                "energy_megatons": physics_results["energia"]["equivalente_tnt_megatons"],
                "crater_diameter_km": physics_results["cratera"]["diametro_final_km"],
                "is_airburst": physics_results["fireball"]["is_airburst"],
                "tsunami_generated": physics_results["tsunami"]["tsunami_generated"]
            },
            "risk_zones_geojson": risk_zones,
            "evacuation_analysis": evacuation_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular rotas de evacuação: {str(e)}")

@router.get("/generate-evacuation-grid", summary="Gerar grade de pontos de evacuação")
def generate_evacuation_grid(
    center_latitude: float = Query(..., description="Latitude do centro da área"),
    center_longitude: float = Query(..., description="Longitude do centro da área"),
    radius_km: float = Query(default=20, description="Raio da área em km"),
    grid_size: int = Query(default=5, description="Tamanho da grade (5x5 = 25 pontos)")
) -> Dict:
    """
    Gera uma grade de pontos de evacuação em torno de um ponto central.
    Útil para criar pontos de evacuação automaticamente.
    """
    try:
        evacuation_points = evacuation_service.generate_evacuation_points_grid(
            center_lat=center_latitude,
            center_lon=center_longitude,
            radius_km=radius_km,
            grid_size=grid_size
        )
        
        return {
            "success": True,
            "center_coordinates": [center_longitude, center_latitude],
            "radius_km": radius_km,
            "grid_size": grid_size,
            "total_points": len(evacuation_points),
            "evacuation_points": evacuation_points
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar grade de evacuação: {str(e)}")

@router.get("/transport-modes", summary="Listar modos de transporte disponíveis")
def get_transport_modes() -> Dict:
    """
    Retorna informações sobre os modos de transporte disponíveis para evacuação.
    """
    transport_modes = {
        "car": {
            "name": "Automóvel",
            "speed_kmh": 60,
            "max_distance_km": 100,
            "description": "Evacuação por veículo particular",
            "priority_factors": ["distância", "tempo", "segurança"]
        },
        "ambulance": {
            "name": "Ambulância",
            "speed_kmh": 80,
            "max_distance_km": 50,
            "description": "Evacuação médica prioritária",
            "priority_factors": ["tempo", "distância", "segurança"]
        },
        "pedestrian": {
            "name": "Pedestre",
            "speed_kmh": 5,
            "max_distance_km": 10,
            "description": "Evacuação a pé",
            "priority_factors": ["distância", "segurança", "tempo"]
        }
    }
    
    return {
        "success": True,
        "total_modes": len(transport_modes),
        "transport_modes": transport_modes
    }

@router.get("/evacuation-points/types", summary="Listar tipos de pontos de evacuação")
def get_evacuation_point_types() -> Dict:
    """
    Retorna informações sobre os tipos de pontos de evacuação disponíveis.
    """
    point_types = {
        "shelter": {
            "name": "Abrigo de Emergência",
            "description": "Local seguro para abrigar pessoas durante a crise",
            "typical_capacity": 100,
            "services": ["água", "banheiro", "primeiros socorros"]
        },
        "hospital": {
            "name": "Hospital",
            "description": "Instalação médica para casos críticos",
            "typical_capacity": 500,
            "services": ["emergência médica", "cirurgia", "UTI"]
        },
        "safe_zone": {
            "name": "Zona Segura",
            "description": "Área fora do alcance dos efeitos do impacto",
            "typical_capacity": 1000,
            "services": ["área aberta", "acesso por estrada"]
        },
        "emergency_shelter": {
            "name": "Abrigo de Emergência Temporário",
            "description": "Local temporário para evacuação imediata",
            "typical_capacity": 200,
            "services": ["proteção básica", "água"]
        }
    }
    
    return {
        "success": True,
        "total_types": len(point_types),
        "point_types": point_types
    }

@router.post("/optimize-routes", summary="Otimizar rotas existentes")
def optimize_existing_routes(
    routes: List[Dict],
    optimization_criteria: str = Query(default="balanced", description="Critério de otimização (speed, safety, distance, balanced)")
) -> Dict:
    """
    Otimiza rotas de evacuação existentes baseado em critérios específicos.
    """
    try:
        if not routes:
            raise HTTPException(status_code=400, detail="Nenhuma rota fornecida para otimização")
        
        # Aplicar critério de otimização
        if optimization_criteria == "speed":
            optimized_routes = sorted(routes, key=lambda x: x.get("route", {}).get("estimated_time_hours", float('inf')))
        elif optimization_criteria == "safety":
            optimized_routes = sorted(routes, key=lambda x: x.get("route", {}).get("safety_score", 0), reverse=True)
        elif optimization_criteria == "distance":
            optimized_routes = sorted(routes, key=lambda x: x.get("route", {}).get("distance_km", float('inf')))
        else:  # balanced
            optimized_routes = sorted(routes, key=lambda x: x.get("route", {}).get("priority_score", float('inf')))
        
        return {
            "success": True,
            "optimization_criteria": optimization_criteria,
            "total_routes": len(optimized_routes),
            "optimized_routes": optimized_routes,
            "recommended_route": optimized_routes[0] if optimized_routes else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao otimizar rotas: {str(e)}")
