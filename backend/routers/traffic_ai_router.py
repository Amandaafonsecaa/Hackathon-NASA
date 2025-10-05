"""
Router para APIs de IA de tráfego e evacuação inteligente.
Implementa endpoints para otimização de rotas, previsão ML e controle RL.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
import asyncio
from services import traffic_ai_service, traffic_assignment
from services.traffic_ai_service import TrafficAIService
from services.traffic_assignment import TrafficCoordinationSystem, IntersectionState, TrafficLightAction
import numpy as np
import time

router = APIRouter()

# Instâncias dos serviços
traffic_service = TrafficAIService()
coordination_system = TrafficCoordinationSystem()

class DemandRequest(BaseModel):
    """Request para definir matriz de demanda."""
    origins: List[Dict] = Field(..., description="Lista de origens com coordenadas e população")
    destinations: List[Dict] = Field(..., description="Lista de destinos com coordenadas e capacidade")

class AssignmentRequest(BaseModel):
    """Request para assignment de tráfego."""
    center_latitude: float = Field(..., description="Latitude do centro da área")
    center_longitude: float = Field(..., description="Longitude do centro da área")
    radius_km: float = Field(default=10, description="Raio da área em km")
    risk_zones_geojson: Optional[Dict] = Field(None, description="GeoJSON com zonas de risco")
    risk_penalty_multiplier: float = Field(default=10.0, description="Multiplicador de penalidade para zonas de risco")
    max_iterations: int = Field(default=50, description="Número máximo de iterações")
    convergence_threshold: float = Field(default=0.001, description="Threshold de convergência")

class MLPredictionRequest(BaseModel):
    """Request para predição ML de tempo de viagem."""
    features: Dict = Field(..., description="Features para predição (hora, chuva, visibilidade, etc.)")

class TrafficStateUpdate(BaseModel):
    """Update de estado de tráfego para RL."""
    intersection_id: str = Field(..., description="ID da interseção")
    queue_lengths: List[float] = Field(..., description="Comprimento das filas por direção")
    flow_rates: List[float] = Field(..., description="Taxa de fluxo por direção")
    waiting_times: List[float] = Field(..., description="Tempos de espera médios")
    phase_duration: float = Field(..., description="Duração da fase atual")
    time_of_day: float = Field(..., description="Hora do dia (0-24)")
    weather_condition: int = Field(..., description="Condição meteorológica (0-3)")

@router.post("/demand", summary="Definir matriz de demanda origem-destino")
def set_demand_matrix(request: DemandRequest) -> Dict:
    """
    Define matriz de demanda para evacuação baseada em origens e destinos.
    
    O sistema:
    1. Mapeia origens e destinos para nós da rede viária
    2. Calcula demanda proporcional à população e capacidade
    3. Gera matriz OD para assignment posterior
    """
    try:
        # Gerar matriz de demanda
        result = traffic_service.generate_demand_matrix(
            origins=request.origins,
            destinations=request.destinations
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "Matriz de demanda definida com sucesso",
            "demand_stats": {
                "total_od_pairs": result["total_od_pairs"],
                "total_demand": result["total_demand"]
            },
            "demand_matrix": result["demand_matrix"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao definir matriz de demanda: {str(e)}")

@router.post("/assign", summary="Executar assignment de tráfego com otimização")
def execute_traffic_assignment(request: AssignmentRequest) -> Dict:
    """
    Executa assignment iterativo (Frank-Wolfe) para otimizar distribuição de tráfego.
    
    O sistema:
    1. Carrega rede viária da área especificada
    2. Aplica zonas de risco com penalidades
    3. Executa algoritmo Frank-Wolfe para equilibrar fluxos
    4. Retorna rotas balanceadas e métricas de performance
    """
    try:
        # Carregar rede viária
        network_result = traffic_service.load_road_network(
            center_point=(request.center_latitude, request.center_longitude),
            radius_km=request.radius_km
        )
        
        if not network_result["success"]:
            raise HTTPException(status_code=500, detail=network_result["error"])
        
        # Aplicar zonas de risco se fornecidas
        if request.risk_zones_geojson:
            risk_result = traffic_service.apply_risk_zones(
                risk_zones_geojson=request.risk_zones_geojson,
                penalty_multiplier=request.risk_penalty_multiplier
            )
            
            if not risk_result["success"]:
                raise HTTPException(status_code=500, detail=risk_result["error"])
        
        # Configurar parâmetros de assignment
        traffic_service.max_iterations = request.max_iterations
        traffic_service.convergence_threshold = request.convergence_threshold
        
        # Executar assignment Frank-Wolfe
        assignment_result = traffic_service.frank_wolfe_assignment()
        
        if not assignment_result["success"]:
            raise HTTPException(status_code=500, detail=assignment_result["error"])
        
        # Gerar rotas de evacuação
        routes_result = traffic_service.get_evacuation_routes(k_routes=3)
        
        return {
            "success": True,
            "network_stats": network_result["stats"],
            "assignment_results": {
                "iterations": assignment_result["iterations"],
                "final_gap": assignment_result["final_gap"],
                "converged": assignment_result["converged"],
                "statistics": assignment_result["statistics"]
            },
            "evacuation_routes": routes_result if routes_result["success"] else None,
            "risk_penalty_applied": request.risk_zones_geojson is not None,
            "penalized_edges": risk_result.get("penalized_edges", 0) if request.risk_zones_geojson else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no assignment de tráfego: {str(e)}")

@router.get("/status", summary="Obter status e telemetria do sistema de tráfego")
def get_traffic_status() -> Dict:
    """
    Retorna telemetria em tempo real do sistema de tráfego.
    
    Inclui:
    - Arestas mais carregadas (gargalos)
    - Métricas de performance
    - Recomendações de staggering (evacuação escalonada)
    """
    try:
        status = {
            "system_status": "operational",
            "timestamp": time.time(),
            "network_loaded": traffic_service.graph is not None,
            "demand_matrix_loaded": bool(traffic_service.demand_matrix),
            "ml_model_loaded": traffic_service.ml_model is not None
        }
        
        if traffic_service.graph:
            status["network_info"] = {
                "nodes": traffic_service.graph.number_of_nodes(),
                "edges": traffic_service.graph.number_of_edges()
            }
        
        if traffic_service.demand_matrix:
            status["demand_info"] = {
                "total_od_pairs": len(traffic_service.demand_matrix),
                "total_demand": sum(od.demand for od in traffic_service.demand_matrix.values())
            }
        
        # Identificar gargalos (simulado)
        bottlenecks = []
        if hasattr(traffic_service, 'edge_flows') and traffic_service.edge_flows:
            for edge_id, flow in traffic_service.edge_flows.items():
                if edge_id in traffic_service.edge_properties:
                    capacity = traffic_service.edge_properties[edge_id].capacity_vph
                    utilization = flow / capacity if capacity > 0 else 0
                    
                    if utilization > 0.8:
                        bottlenecks.append({
                            "edge_id": str(edge_id),
                            "utilization": utilization,
                            "flow": flow,
                            "capacity": capacity,
                            "severity": "high" if utilization > 0.95 else "medium"
                        })
        
        status["bottlenecks"] = bottlenecks
        status["bottleneck_count"] = len(bottlenecks)
        
        # Recomendações de staggering
        recommendations = []
        if len(bottlenecks) > 5:
            recommendations.append({
                "type": "staggering",
                "message": "Muitos gargalos detectados. Recomenda-se evacuação escalonada.",
                "suggested_stagger_minutes": 30
            })
        
        if any(b["severity"] == "high" for b in bottlenecks):
            recommendations.append({
                "type": "rerouting",
                "message": "Gargalos críticos detectados. Redirecionamento necessário.",
                "priority": "high"
            })
        
        status["recommendations"] = recommendations
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.post("/replan", summary="Replanejar evacuação com novas condições")
def replan_evacuation(
    new_risk_zones: Optional[Dict] = None,
    weather_update: Optional[Dict] = None,
    incident_update: Optional[Dict] = None,
    replan_radius_km: float = Query(default=15, description="Raio para replanejamento")
) -> Dict:
    """
    Replaneja evacuação com base em novas condições.
    
    Parâmetros:
    - new_risk_zones: Novas zonas de risco (incêndios, bloqueios)
    - weather_update: Atualização meteorológica (chuva, vento, visibilidade)
    - incident_update: Incidentes de trânsito ou bloqueios
    """
    try:
        replan_results = {
            "success": True,
            "replan_timestamp": time.time(),
            "updates_applied": []
        }
        
        # Aplicar novas zonas de risco
        if new_risk_zones:
            risk_result = traffic_service.apply_risk_zones(
                risk_zones_geojson=new_risk_zones,
                penalty_multiplier=15.0  # Penalidade mais alta para novos riscos
            )
            
            if risk_result["success"]:
                replan_results["updates_applied"].append({
                    "type": "risk_zones",
                    "penalized_edges": risk_result["penalized_edges"]
                })
        
        # Atualizar modelo ML com condições meteorológicas
        if weather_update and traffic_service.ml_model:
            # Simular atualização de condições meteorológicas
            replan_results["updates_applied"].append({
                "type": "weather_update",
                "conditions": weather_update
            })
        
        # Aplicar incidentes de trânsito
        if incident_update:
            # Simular bloqueios ou redução de capacidade
            replan_results["updates_applied"].append({
                "type": "incident_update",
                "affected_edges": incident_update.get("affected_edges", [])
            })
        
        # Reexecutar assignment com warm-start
        if traffic_service.demand_matrix:
            assignment_result = traffic_service.frank_wolfe_assignment()
            
            if assignment_result["success"]:
                replan_results["new_assignment"] = {
                    "iterations": assignment_result["iterations"],
                    "converged": assignment_result["converged"],
                    "statistics": assignment_result["statistics"]
                }
                
                # Gerar novas rotas
                routes_result = traffic_service.get_evacuation_routes(k_routes=3)
                replan_results["new_routes"] = routes_result
        
        return replan_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no replanejamento: {str(e)}")

@router.post("/ml/predict", summary="Predição ML de tempo de viagem")
def predict_travel_time(request: MLPredictionRequest) -> Dict:
    """
    Prediz tempo de viagem usando modelo ML treinado.
    
    Features esperadas:
    - hour: Hora do dia (0-23)
    - rainfall: Chuva em mm/h
    - visibility: Visibilidade em km
    - wind_speed: Velocidade do vento em m/s
    - grade: Inclinação da via em %
    - surface_type: Tipo de superfície (0=asfalto, 1=concreto, 2=cascalho)
    - lanes: Número de faixas
    """
    try:
        # Treinar modelo se não estiver carregado
        if traffic_service.ml_model is None:
            train_result = traffic_service.train_ml_model(synthetic_data=True)
            if not train_result["success"]:
                raise HTTPException(status_code=500, detail="Erro ao treinar modelo ML")
        
        # Fazer predição
        predicted_time = traffic_service.predict_travel_time(request.features)
        
        return {
            "success": True,
            "predicted_travel_time_seconds": predicted_time,
            "predicted_travel_time_minutes": predicted_time / 60,
            "features_used": request.features,
            "model_info": {
                "type": "GradientBoostingRegressor",
                "features_count": len(request.features)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição ML: {str(e)}")

@router.post("/ml/train", summary="Treinar modelo ML com dados sintéticos")
def train_ml_model(synthetic_data: bool = Query(default=True, description="Usar dados sintéticos")) -> Dict:
    """
    Treina modelo ML para previsão de tempo de viagem.
    """
    try:
        result = traffic_service.train_ml_model(synthetic_data=synthetic_data)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no treinamento ML: {str(e)}")

@router.post("/rl/intersection/add", summary="Adicionar interseção para controle RL")
def add_intersection(
    intersection_id: str = Query(..., description="ID único da interseção"),
    latitude: float = Query(..., description="Latitude da interseção"),
    longitude: float = Query(..., description="Longitude da interseção"),
    num_directions: int = Query(default=4, description="Número de direções")
) -> Dict:
    """
    Adiciona nova interseção ao sistema de controle RL.
    """
    try:
        coordination_system.add_intersection(
            intersection_id=intersection_id,
            position=(latitude, longitude)
        )
        
        return {
            "success": True,
            "intersection_id": intersection_id,
            "position": [longitude, latitude],
            "num_directions": num_directions,
            "controller_initialized": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar interseção: {str(e)}")

@router.post("/rl/intersection/update", summary="Atualizar estado de interseção")
def update_intersection_state(request: TrafficStateUpdate) -> Dict:
    """
    Atualiza estado de uma interseção para controle RL.
    """
    try:
        # Criar estado da interseção
        state = IntersectionState(
            queue_lengths=request.queue_lengths,
            flow_rates=request.flow_rates,
            waiting_times=request.waiting_times,
            phase_duration=request.phase_duration,
            time_of_day=request.time_of_day,
            weather_condition=request.weather_condition
        )
        
        # Atualizar estado no sistema de coordenação
        coordination_system.update_intersection_state(
            intersection_id=request.intersection_id,
            state=state
        )
        
        # Obter ação otimizada
        action = coordination_system.get_coordinated_actions(
            intersection_id=request.intersection_id,
            state=state
        )
        
        return {
            "success": True,
            "intersection_id": request.intersection_id,
            "recommended_action": {
                "phase": action.phase,
                "duration_seconds": action.duration,
                "offset_seconds": action.offset
            },
            "state_updated": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar estado: {str(e)}")

@router.post("/rl/simulate", summary="Simular cenário de tráfego para treinamento")
def simulate_traffic_scenario(
    duration_minutes: int = Query(default=60, description="Duração da simulação em minutos")
) -> Dict:
    """
    Simula cenário de tráfego para treinamento dos controladores RL.
    """
    try:
        results = coordination_system.simulate_traffic_scenario(duration_minutes)
        
        return {
            "success": True,
            "simulation_duration_minutes": duration_minutes,
            "intersections_trained": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na simulação: {str(e)}")

@router.get("/rl/intersections", summary="Listar interseções controladas por RL")
def list_intersections() -> Dict:
    """
    Retorna lista de interseções controladas pelo sistema RL.
    """
    try:
        intersections = list(coordination_system.intersections.keys())
        
        return {
            "success": True,
            "total_intersections": len(intersections),
            "intersections": intersections
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar interseções: {str(e)}")

@router.get("/network/load", summary="Carregar rede viária de uma área")
def load_road_network(
    center_latitude: float = Query(..., description="Latitude do centro"),
    center_longitude: float = Query(..., description="Longitude do centro"),
    radius_km: float = Query(default=10, description="Raio em km")
) -> Dict:
    """
    Carrega rede viária de uma área específica usando OSMnx.
    """
    try:
        result = traffic_service.load_road_network(
            center_point=(center_latitude, center_longitude),
            radius_km=radius_km
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar rede: {str(e)}")

@router.get("/network/info", summary="Informações sobre a rede carregada")
def get_network_info() -> Dict:
    """
    Retorna informações sobre a rede viária carregada.
    """
    try:
        if traffic_service.graph is None:
            return {
                "success": False,
                "message": "Nenhuma rede carregada"
            }
        
        return {
            "success": True,
            "network_stats": {
                "nodes": traffic_service.graph.number_of_nodes(),
                "edges": traffic_service.graph.number_of_edges(),
                "edge_properties_count": len(traffic_service.edge_properties)
            },
            "parameters": {
                "bpr_alpha": traffic_service.bpr_alpha,
                "bpr_beta": traffic_service.bpr_beta,
                "convergence_threshold": traffic_service.convergence_threshold,
                "max_iterations": traffic_service.max_iterations
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações: {str(e)}")

@router.get("/health", summary="Verificar saúde do sistema")
def health_check() -> Dict:
    """
    Verifica saúde geral do sistema de IA de tráfego.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "traffic_service": {
                    "network_loaded": traffic_service.graph is not None,
                    "demand_loaded": bool(traffic_service.demand_matrix),
                    "ml_model_loaded": traffic_service.ml_model is not None
                },
                "coordination_system": {
                    "intersections_count": len(coordination_system.intersections),
                    "active": True
                }
            }
        }
        
        # Verificar se todos os componentes estão funcionais
        all_healthy = (
            health_status["components"]["traffic_service"]["network_loaded"] and
            health_status["components"]["coordination_system"]["active"]
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
