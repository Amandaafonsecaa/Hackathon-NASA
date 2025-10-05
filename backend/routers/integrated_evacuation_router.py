"""
Router para análise integrada de evacuação inteligente.
Endpoint principal que combina todos os componentes de IA.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import asyncio
from services.integrated_evacuation_service import integrated_evacuation_service, EvacuationScenario
import time

router = APIRouter()

class EvacuationPoint(BaseModel):
    """Ponto de evacuação."""
    id: str = Field(..., description="ID único do ponto")
    name: str = Field(..., description="Nome do ponto")
    type: str = Field(default="shelter", description="Tipo (shelter, hospital, safe_zone)")
    capacity: int = Field(..., description="Capacidade de pessoas")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")

class PopulationArea(BaseModel):
    """Área populacional."""
    id: str = Field(..., description="ID único da área")
    name: str = Field(..., description="Nome da área")
    population: int = Field(..., description="População da área")
    latitude: float = Field(..., description="Latitude central")
    longitude: float = Field(..., description="Longitude central")
    priority: int = Field(default=1, description="Prioridade (1=alta, 2=média, 3=baixa)")

class IntegratedEvacuationRequest(BaseModel):
    """Request para análise integrada de evacuação."""
    # Parâmetros do asteroide
    impact_latitude: float = Field(..., description="Latitude do ponto de impacto")
    impact_longitude: float = Field(..., description="Longitude do ponto de impacto")
    asteroid_diameter_m: float = Field(..., description="Diâmetro do asteroide em metros")
    asteroid_velocity_kms: float = Field(..., description="Velocidade do asteroide em km/s")
    impact_angle_deg: float = Field(default=45, description="Ângulo de impacto em graus")
    terrain_type: str = Field(default="rock", description="Tipo de terreno (rock, soil, ocean)")
    
    # Condições meteorológicas
    wind_speed_ms: float = Field(default=10, description="Velocidade do vento em m/s")
    wind_direction_deg: float = Field(default=0, description="Direção do vento em graus")
    
    # Parâmetros de evacuação
    evacuation_radius_km: float = Field(default=20, description="Raio da área de evacuação em km")
    population_areas: List[PopulationArea] = Field(..., description="Áreas populacionais para evacuação")
    evacuation_points: List[EvacuationPoint] = Field(..., description="Pontos de evacuação disponíveis")
    
    # Configurações opcionais
    enable_ml_predictions: bool = Field(default=True, description="Habilitar predições ML")
    enable_rl_control: bool = Field(default=True, description="Habilitar controle RL")
    enable_realtime_updates: bool = Field(default=True, description="Habilitar atualizações em tempo real")

class ScenarioUpdateRequest(BaseModel):
    """Request para atualização de cenário."""
    scenario_id: str = Field(..., description="ID do cenário a ser atualizado")
    new_risk_zones: Optional[Dict] = Field(None, description="Novas zonas de risco")
    weather_update: Optional[Dict] = Field(None, description="Atualização meteorológica")
    traffic_incidents: Optional[List[Dict]] = Field(None, description="Novos incidentes de trânsito")

@router.post("/analyze", summary="Análise completa de evacuação inteligente")
async def run_integrated_evacuation_analysis(request: IntegratedEvacuationRequest) -> Dict:
    """
    Executa análise completa de evacuação usando IA para evitar congestionamento.
    
    Esta é a API principal que combina todos os componentes:
    
    🧭 **Routing AI**: Calcula rotas de evacuação seguras usando otimização
    🌍 **Predictive AI**: Estima risco populacional e tempo de viagem
    🚦 **Decision AI**: Otimiza sinais semafóricos e distribuição de tráfego
    
    **Pipeline de Processamento:**
    1. Simulação de impacto físico (cratera, ondas de choque, etc.)
    2. Geração de zonas de risco GeoJSON
    3. Carregamento de rede viária real (OSMnx)
    4. Aplicação de penalidades para zonas de risco
    5. Geração de matriz de demanda origem-destino
    6. Assignment iterativo (Frank-Wolfe) para distribuir tráfego
    7. Treinamento e aplicação de modelo ML para previsão
    8. Configuração de controladores RL para semáforos
    9. Ativação de WebSocket para atualizações em tempo real
    
    **Resultado:**
    - Rotas de evacuação otimizadas sem congestionamento
    - Previsões de tempo de viagem baseadas em ML
    - Controle inteligente de semáforos
    - Atualizações em tempo real via WebSocket
    """
    try:
        # Converter request para cenário
        scenario = EvacuationScenario(
            impact_lat=request.impact_latitude,
            impact_lon=request.impact_longitude,
            asteroid_diameter_m=request.asteroid_diameter_m,
            asteroid_velocity_kms=request.asteroid_velocity_kms,
            impact_angle_deg=request.impact_angle_deg,
            terrain_type=request.terrain_type,
            wind_speed_ms=request.wind_speed_ms,
            wind_direction_deg=request.wind_direction_deg,
            evacuation_radius_km=request.evacuation_radius_km,
            population_data={
                "areas": [
                    {
                        "id": area.id,
                        "name": area.name,
                        "population": area.population,
                        "latitude": area.latitude,
                        "longitude": area.longitude,
                        "priority": area.priority
                    }
                    for area in request.population_areas
                ]
            },
            evacuation_points=[
                {
                    "id": point.id,
                    "name": point.name,
                    "type": point.type,
                    "capacity": point.capacity,
                    "latitude": point.latitude,
                    "longitude": point.longitude
                }
                for point in request.evacuation_points
            ]
        )
        
        # Executar análise completa
        result = await integrated_evacuation_service.run_complete_evacuation_analysis(scenario)
        
        return {
            "success": True,
            "scenario_id": result.realtime_updates["scenario_id"],
            "execution_time_seconds": result.execution_time,
            "timestamp": result.timestamp,
            
            # Resultados da simulação física
            "impact_simulation": {
                "energy_megatons": result.physics_results["energia"]["equivalente_tnt_megatons"],
                "crater_diameter_km": result.physics_results["cratera"]["diametro_final_km"],
                "is_airburst": result.physics_results["fireball"]["is_airburst"],
                "tsunami_generated": result.physics_results["tsunami"]["tsunami_generated"],
                "thermal_radius_km": result.physics_results["thermal"]["raio_queimadura_km"],
                "blast_radius_km": result.physics_results["blast"]["raio_destruicao_km"]
            },
            
            # Zonas de risco geradas
            "risk_zones": {
                "geojson": result.risk_zones,
                "total_zones": len(result.risk_zones.get("features", [])),
                "risk_types": list(set(
                    feature["properties"].get("zone_type", "unknown")
                    for feature in result.risk_zones.get("features", [])
                ))
            },
            
            # Análise de demanda e tráfego
            "traffic_analysis": {
                "network_stats": result.traffic_assignment.get("network_stats", {}),
                "demand_stats": {
                    "total_od_pairs": result.demand_matrix.get("total_od_pairs", 0),
                    "total_demand": result.demand_matrix.get("total_demand", 0)
                },
                "assignment_results": {
                    "iterations": result.traffic_assignment.get("iterations", 0),
                    "converged": result.traffic_assignment.get("converged", False),
                    "final_gap": result.traffic_assignment.get("final_gap", 0),
                    "bottlenecks": result.traffic_assignment.get("statistics", {}).get("bottleneck_count", 0)
                }
            },
            
            # Rotas de evacuação otimizadas
            "evacuation_routes": {
                "total_od_pairs": result.evacuation_routes.get("total_od_pairs", 0),
                "routes_per_pair": result.evacuation_routes.get("routes_per_pair", 0),
                "routes": result.evacuation_routes.get("routes", {})
            },
            
            # Predições ML
            "ml_predictions": result.ml_predictions,
            
            # Controladores RL
            "rl_controllers": {
                "total_intersections": len(result.rl_controls),
                "intersections": result.rl_controls
            },
            
            # Sistema de tempo real
            "realtime_system": result.realtime_updates,
            
            # Recomendações finais
            "recommendations": {
                "evacuation_strategy": "Rotas distribuídas para evitar congestionamento",
                "staggering_recommended": result.traffic_assignment.get("statistics", {}).get("bottleneck_count", 0) > 3,
                "critical_bottlenecks": [
                    bottleneck for bottleneck in 
                    result.traffic_assignment.get("statistics", {}).get("bottlenecks", [])
                    if bottleneck.get("utilization", 0) > 0.9
                ],
                "estimated_evacuation_time": f"{result.demand_matrix.get('total_demand', 0) * 2 / 60:.1f} horas"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise integrada: {str(e)}")

@router.post("/update-scenario", summary="Atualizar cenário em tempo real")
async def update_evacuation_scenario(request: ScenarioUpdateRequest) -> Dict:
    """
    Atualiza cenário de evacuação em tempo real com novas informações.
    
    Permite:
    - Adicionar novas zonas de risco (incêndios, bloqueios)
    - Atualizar condições meteorológicas
    - Reportar incidentes de trânsito
    - Reotimizar rotas automaticamente
    """
    try:
        updates = {}
        
        if request.new_risk_zones:
            updates["new_risk_zones"] = request.new_risk_zones
        
        if request.weather_update:
            updates["weather_update"] = request.weather_update
        
        if request.traffic_incidents:
            updates["traffic_incidents"] = request.traffic_incidents
        
        # Atualizar cenário
        await integrated_evacuation_service.update_scenario_realtime(
            scenario_id=request.scenario_id,
            updates=updates
        )
        
        return {
            "success": True,
            "scenario_id": request.scenario_id,
            "updates_applied": list(updates.keys()),
            "timestamp": time.time(),
            "message": "Cenário atualizado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cenário: {str(e)}")

@router.get("/scenario/{scenario_id}/status", summary="Status de cenário específico")
def get_scenario_status(scenario_id: str) -> Dict:
    """
    Retorna status detalhado de um cenário de evacuação.
    """
    try:
        status = integrated_evacuation_service.get_scenario_status(scenario_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.get("/scenarios", summary="Listar cenários ativos")
def list_active_scenarios() -> Dict:
    """
    Lista todos os cenários de evacuação ativos.
    """
    try:
        scenarios = integrated_evacuation_service.list_active_scenarios()
        return scenarios
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar cenários: {str(e)}")

@router.post("/stop-broadcast", summary="Parar sistema de tempo real")
async def stop_realtime_system() -> Dict:
    """
    Para o sistema de broadcast em tempo real.
    """
    try:
        await integrated_evacuation_service.stop_realtime_broadcast()
        
        return {
            "success": True,
            "message": "Sistema de tempo real parado",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar sistema: {str(e)}")

@router.get("/health", summary="Verificar saúde do sistema integrado")
def health_check() -> Dict:
    """
    Verifica saúde de todos os componentes do sistema integrado.
    """
    try:
        from services import traffic_ai_service, coordination_system, realtime_service
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "traffic_ai_service": {
                    "network_loaded": traffic_ai_service.graph is not None,
                    "demand_loaded": bool(traffic_ai_service.demand_matrix),
                    "ml_model_loaded": traffic_ai_service.ml_model is not None
                },
                "coordination_system": {
                    "intersections_count": len(coordination_system.intersections),
                    "active": True
                },
                "realtime_service": {
                    "broadcasting": realtime_service.is_running,
                    "active_connections": len(realtime_service.manager.active_connections),
                    "update_interval": realtime_service.update_interval
                },
                "integrated_service": {
                    "active_scenarios": len(integrated_evacuation_service.active_scenarios),
                    "broadcasting": integrated_evacuation_service.is_broadcasting
                }
            }
        }
        
        # Verificar se todos os componentes estão funcionais
        all_healthy = (
            health_status["components"]["traffic_ai_service"]["network_loaded"] and
            health_status["components"]["coordination_system"]["active"] and
            health_status["components"]["realtime_service"]["broadcasting"]
        )
        
        if not all_healthy:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }

@router.get("/capabilities", summary="Capacidades do sistema de IA")
def get_system_capabilities() -> Dict:
    """
    Retorna descrição das capacidades do sistema de IA para evacuação.
    """
    return {
        "success": True,
        "system_name": "Cosmos Sentinel - IA para Evacuação Inteligente",
        "version": "1.0.0",
        "description": "Sistema integrado de IA para evacuação sem congestionamento",
        
        "ai_components": {
            "routing_ai": {
                "name": "Routing AI",
                "description": "Calcula rotas de evacuação seguras usando dados geográficos e simulações",
                "capabilities": [
                    "Grafo viário com capacidade dinâmica",
                    "Função BPR para modelagem de congestionamento",
                    "Assignment iterativo Frank-Wolfe",
                    "Evitação de zonas de risco",
                    "K-rotas alternativas"
                ],
                "algorithms": ["Dijkstra", "A*", "Frank-Wolfe", "BPR"]
            },
            
            "predictive_ai": {
                "name": "Predictive AI", 
                "description": "Estima risco populacional combinando dados da NASA, USGS e WorldPop",
                "capabilities": [
                    "Previsão de tempo de viagem com ML",
                    "Modelo Gradient Boosting",
                    "Integração meteorológica (MERRA-2, GPM, TEMPO)",
                    "Análise de densidade populacional",
                    "Estimativa de capacidade de abrigos"
                ],
                "models": ["GradientBoostingRegressor", "RandomForestRegressor"]
            },
            
            "decision_ai": {
                "name": "Decision AI",
                "description": "Sugere melhor estratégia de mitigação baseada em energia, tempo e localização",
                "capabilities": [
                    "Controle RL de semáforos (DQN)",
                    "Otimização de offset entre interseções",
                    "Coordenção multi-intersecção",
                    "Adaptação a condições em tempo real",
                    "Minimização de tempo médio e pico de carga"
                ],
                "algorithms": ["Deep Q-Network (DQN)", "Policy Gradient"]
            }
        },
        
        "data_sources": {
            "nasa": ["NEOs", "MERRA-2", "GPM", "TEMPO"],
            "usgs": ["Elevação", "Geologia", "Hidrologia"],
            "openstreetmap": ["Rede viária", "Pontos de interesse"],
            "worldpop": ["Densidade populacional", "Demografia"]
        },
        
        "apis": {
            "rest": "/api/v1/evacuation-ai/*",
            "websocket": "/api/v1/ws/*",
            "documentation": "/docs"
        },
        
        "performance": {
            "network_loading": "< 30s para área de 20km",
            "assignment_convergence": "< 50 iterações",
            "ml_prediction": "< 100ms",
            "realtime_updates": "5s intervalo",
            "websocket_latency": "< 50ms"
        }
    }
