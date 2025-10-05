"""
Serviço integrado de evacuação inteligente.
Combina todos os componentes: grafo viário, BPR, ML, RL e WebSocket.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from services.traffic_ai_service import traffic_ai_service
from services.traffic_assignment import coordination_system, IntersectionState
from services.realtime_websocket import realtime_service
from services import evacuation_service, physics_service, geojson_service, population_service

logger = logging.getLogger(__name__)

@dataclass
class EvacuationScenario:
    """Cenário completo de evacuação."""
    impact_lat: float
    impact_lon: float
    asteroid_diameter_m: float
    asteroid_velocity_kms: float
    impact_angle_deg: float
    terrain_type: str
    wind_speed_ms: float
    wind_direction_deg: float
    evacuation_radius_km: float
    population_data: Dict
    evacuation_points: List[Dict]

@dataclass
class EvacuationResult:
    """Resultado completo da análise de evacuação."""
    scenario: EvacuationScenario
    physics_results: Dict
    risk_zones: Dict
    demand_matrix: Dict
    traffic_assignment: Dict
    evacuation_routes: Dict
    ml_predictions: Dict
    rl_controls: Dict
    realtime_updates: Dict
    execution_time: float
    timestamp: float

class IntegratedEvacuationService:
    """Serviço integrado para evacuação inteligente sem congestionamento."""
    
    def __init__(self):
        self.active_scenarios = {}
        self.is_broadcasting = False
        
    async def run_complete_evacuation_analysis(self, scenario: EvacuationScenario) -> EvacuationResult:
        """
        Executa análise completa de evacuação com todos os componentes de IA.
        
        Pipeline:
        1. Simulação de impacto físico
        2. Geração de zonas de risco
        3. Carregamento de rede viária
        4. Geração de matriz de demanda
        5. Assignment de tráfego (Frank-Wolfe)
        6. Predição ML de tempos
        7. Controle RL de semáforos
        8. Ativação de WebSocket em tempo real
        """
        start_time = time.time()
        logger.info(f"Iniciando análise completa de evacuação para ({scenario.impact_lat}, {scenario.impact_lon})")
        
        try:
            # 1. Simulação de impacto físico
            logger.info("Executando simulação de impacto...")
            physics_results = physics_service.calculate_all_impact_effects(
                diameter_m=scenario.asteroid_diameter_m,
                velocity_kms=scenario.asteroid_velocity_kms,
                impact_angle_deg=scenario.impact_angle_deg,
                tipo_terreno=scenario.terrain_type,
                wind_speed_ms=scenario.wind_speed_ms,
                wind_direction_deg=scenario.wind_direction_deg
            )
            
            # 2. Geração de zonas de risco
            logger.info("Gerando zonas de risco...")
            risk_zones = geojson_service.generate_impact_risk_zones(
                impact_lat=scenario.impact_lat,
                impact_lon=scenario.impact_lon,
                physics_results=physics_results
            )
            
            # 3. Carregamento de rede viária
            logger.info("Carregando rede viária...")
            network_result = traffic_ai_service.load_road_network(
                center_point=(scenario.impact_lat, scenario.impact_lon),
                radius_km=scenario.evacuation_radius_km
            )
            
            if not network_result["success"]:
                raise Exception(f"Erro ao carregar rede: {network_result['error']}")
            
            # 4. Aplicar zonas de risco à rede
            logger.info("Aplicando zonas de risco à rede viária...")
            risk_result = traffic_ai_service.apply_risk_zones(
                risk_zones_geojson=risk_zones,
                penalty_multiplier=15.0
            )
            
            # 5. Geração de matriz de demanda
            logger.info("Gerando matriz de demanda...")
            
            # Preparar origens baseadas em densidade populacional
            origins = []
            for area in scenario.population_data.get("areas", []):
                origins.append({
                    "id": area["id"],
                    "latitude": area["latitude"],
                    "longitude": area["longitude"],
                    "population": area["population"],
                    "priority": area.get("priority", 1)
                })
            
            # Preparar destinos (pontos de evacuação)
            destinations = []
            for point in scenario.evacuation_points:
                destinations.append({
                    "id": point["id"],
                    "latitude": point["latitude"],
                    "longitude": point["longitude"],
                    "capacity": point["capacity"],
                    "type": point.get("type", "shelter")
                })
            
            demand_result = traffic_ai_service.generate_demand_matrix(
                origins=origins,
                destinations=destinations
            )
            
            if not demand_result["success"]:
                raise Exception(f"Erro ao gerar matriz de demanda: {demand_result['error']}")
            
            # 6. Assignment de tráfego (Frank-Wolfe)
            logger.info("Executando assignment de tráfego...")
            assignment_result = traffic_ai_service.frank_wolfe_assignment()
            
            if not assignment_result["success"]:
                raise Exception(f"Erro no assignment: {assignment_result['error']}")
            
            # 7. Gerar rotas de evacuação
            logger.info("Gerando rotas de evacuação...")
            routes_result = traffic_ai_service.get_evacuation_routes(k_routes=3)
            
            # 8. Treinar e usar modelo ML
            logger.info("Treinando modelo ML...")
            ml_result = traffic_ai_service.train_ml_model(synthetic_data=True)
            
            # Fazer predições para diferentes cenários meteorológicos
            ml_predictions = {}
            weather_scenarios = [
                {"hour": 8, "rainfall": 0, "visibility": 10, "wind_speed": 5},  # Manhã clara
                {"hour": 14, "rainfall": 2, "visibility": 8, "wind_speed": 10}, # Tarde chuvosa
                {"hour": 20, "rainfall": 5, "visibility": 5, "wind_speed": 15}, # Noite tempestuosa
            ]
            
            for i, weather in enumerate(weather_scenarios):
                predicted_time = traffic_ai_service.predict_travel_time(weather)
                ml_predictions[f"scenario_{i+1}"] = {
                    "weather_conditions": weather,
                    "predicted_travel_time_seconds": predicted_time,
                    "predicted_travel_time_minutes": predicted_time / 60
                }
            
            # 9. Configurar controladores RL
            logger.info("Configurando controladores RL...")
            rl_controls = {}
            
            # Adicionar interseções principais (simulado)
            main_intersections = [
                {"id": "int_001", "lat": scenario.impact_lat + 0.01, "lon": scenario.impact_lon + 0.01},
                {"id": "int_002", "lat": scenario.impact_lat - 0.01, "lon": scenario.impact_lon + 0.01},
                {"id": "int_003", "lat": scenario.impact_lat + 0.01, "lon": scenario.impact_lon - 0.01},
                {"id": "int_004", "lat": scenario.impact_lat - 0.01, "lon": scenario.impact_lon - 0.01},
            ]
            
            for intersection in main_intersections:
                coordination_system.add_intersection(
                    intersection_id=intersection["id"],
                    position=(intersection["lat"], intersection["lon"])
                )
                rl_controls[intersection["id"]] = {
                    "controller_initialized": True,
                    "position": [intersection["lon"], intersection["lat"]]
                }
            
            # 10. Iniciar sistema de tempo real
            logger.info("Iniciando sistema de tempo real...")
            if not realtime_service.is_running:
                asyncio.create_task(realtime_service.start_broadcast_loop())
                self.is_broadcasting = True
            
            # Preparar dados de tempo real
            realtime_updates = {
                "broadcast_active": self.is_broadcasting,
                "update_interval": realtime_service.update_interval,
                "active_connections": len(realtime_service.manager.active_connections),
                "scenario_id": f"evac_{int(time.time())}"
            }
            
            execution_time = time.time() - start_time
            
            # Criar resultado final
            result = EvacuationResult(
                scenario=scenario,
                physics_results=physics_results,
                risk_zones=risk_zones,
                demand_matrix=demand_result,
                traffic_assignment=assignment_result,
                evacuation_routes=routes_result,
                ml_predictions=ml_predictions,
                rl_controls=rl_controls,
                realtime_updates=realtime_updates,
                execution_time=execution_time,
                timestamp=time.time()
            )
            
            # Armazenar cenário ativo
            scenario_id = realtime_updates["scenario_id"]
            self.active_scenarios[scenario_id] = result
            
            logger.info(f"Análise completa finalizada em {execution_time:.2f}s")
            
            # Enviar atualização via WebSocket
            await self._broadcast_analysis_complete(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de evacuação: {e}")
            raise
    
    async def _broadcast_analysis_complete(self, result: EvacuationResult):
        """Envia notificação de conclusão da análise via WebSocket."""
        try:
            from services.realtime_websocket import WebSocketMessage, MessageType
            
            completion_msg = WebSocketMessage(
                message_type=MessageType.SYSTEM_STATUS.value,
                timestamp=time.time(),
                data={
                    "analysis_complete": True,
                    "scenario_id": result.realtime_updates["scenario_id"],
                    "execution_time": result.execution_time,
                    "statistics": {
                        "network_nodes": result.traffic_assignment.get("network_stats", {}).get("nodes", 0),
                        "network_edges": result.traffic_assignment.get("network_stats", {}).get("edges", 0),
                        "total_demand": result.demand_matrix.get("total_demand", 0),
                        "assignment_iterations": result.traffic_assignment.get("iterations", 0),
                        "routes_generated": len(result.evacuation_routes.get("routes", {}))
                    }
                },
                priority="high"
            )
            
            await realtime_service.manager.broadcast(completion_msg)
            
        except Exception as e:
            logger.error(f"Erro ao enviar broadcast: {e}")
    
    async def update_scenario_realtime(self, scenario_id: str, updates: Dict):
        """Atualiza cenário em tempo real com novas informações."""
        if scenario_id not in self.active_scenarios:
            raise ValueError(f"Cenário {scenario_id} não encontrado")
        
        scenario = self.active_scenarios[scenario_id]
        
        try:
            # Verificar se há novas zonas de risco
            if "new_risk_zones" in updates:
                logger.info("Aplicando novas zonas de risco...")
                risk_result = traffic_ai_service.apply_risk_zones(
                    risk_zones_geojson=updates["new_risk_zones"],
                    penalty_multiplier=20.0
                )
                
                # Reexecutar assignment
                assignment_result = traffic_ai_service.frank_wolfe_assignment()
                
                # Atualizar cenário
                scenario.traffic_assignment = assignment_result
            
            # Verificar se há atualizações meteorológicas
            if "weather_update" in updates:
                logger.info("Atualizando condições meteorológicas...")
                weather = updates["weather_update"]
                predicted_time = traffic_ai_service.predict_travel_time(weather)
                
                scenario.ml_predictions["current_conditions"] = {
                    "weather_conditions": weather,
                    "predicted_travel_time_seconds": predicted_time,
                    "predicted_travel_time_minutes": predicted_time / 60,
                    "timestamp": time.time()
                }
            
            # Verificar se há incidentes de trânsito
            if "traffic_incidents" in updates:
                logger.info("Processando incidentes de trânsito...")
                
                for incident in updates["traffic_incidents"]:
                    # Simular impacto no tráfego
                    # TODO: Implementar lógica específica para incidentes
                    pass
            
            # Atualizar timestamp
            scenario.timestamp = time.time()
            
            # Enviar atualização via WebSocket
            await self._broadcast_scenario_update(scenario, updates)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar cenário: {e}")
            raise
    
    async def _broadcast_scenario_update(self, scenario: EvacuationResult, updates: Dict):
        """Envia atualização do cenário via WebSocket."""
        try:
            from services.realtime_websocket import WebSocketMessage, MessageType
            
            update_msg = WebSocketMessage(
                message_type=MessageType.EVACUATION_STATUS.value,
                timestamp=time.time(),
                data={
                    "scenario_id": scenario.realtime_updates["scenario_id"],
                    "update_type": "scenario_modification",
                    "updates_applied": list(updates.keys()),
                    "timestamp": scenario.timestamp,
                    "impact_location": [scenario.scenario.impact_lon, scenario.scenario.impact_lat],
                    "evacuation_radius_km": scenario.scenario.evacuation_radius_km
                },
                priority="normal"
            )
            
            await realtime_service.manager.broadcast(update_msg, "evacuation_status")
            
        except Exception as e:
            logger.error(f"Erro ao enviar atualização: {e}")
    
    def get_scenario_status(self, scenario_id: str) -> Dict:
        """Retorna status atual de um cenário."""
        if scenario_id not in self.active_scenarios:
            return {"success": False, "error": "Cenário não encontrado"}
        
        scenario = self.active_scenarios[scenario_id]
        
        return {
            "success": True,
            "scenario_id": scenario_id,
            "timestamp": scenario.timestamp,
            "execution_time": scenario.execution_time,
            "impact_location": {
                "latitude": scenario.scenario.impact_lat,
                "longitude": scenario.scenario.impact_lon
            },
            "status": {
                "physics_simulation": "completed",
                "risk_zones": "generated",
                "network_loaded": traffic_ai_service.graph is not None,
                "demand_matrix": bool(traffic_ai_service.demand_matrix),
                "traffic_assignment": scenario.traffic_assignment.get("converged", False),
                "ml_model": traffic_ai_service.ml_model is not None,
                "rl_controllers": len(scenario.rl_controls),
                "realtime_broadcast": scenario.realtime_updates["broadcast_active"]
            },
            "statistics": {
                "total_demand": scenario.demand_matrix.get("total_demand", 0),
                "assignment_iterations": scenario.traffic_assignment.get("iterations", 0),
                "routes_count": len(scenario.evacuation_routes.get("routes", {})),
                "bottlenecks": scenario.traffic_assignment.get("statistics", {}).get("bottleneck_count", 0)
            }
        }
    
    def list_active_scenarios(self) -> Dict:
        """Lista todos os cenários ativos."""
        return {
            "success": True,
            "active_scenarios": len(self.active_scenarios),
            "scenarios": [
                {
                    "scenario_id": scenario_id,
                    "timestamp": scenario.timestamp,
                    "impact_location": [scenario.scenario.impact_lon, scenario.scenario.impact_lat],
                    "evacuation_radius_km": scenario.scenario.evacuation_radius_km,
                    "execution_time": scenario.execution_time
                }
                for scenario_id, scenario in self.active_scenarios.items()
            ]
        }
    
    async def stop_realtime_broadcast(self):
        """Para o sistema de broadcast em tempo real."""
        if self.is_broadcasting:
            await realtime_service.stop_broadcast_loop()
            self.is_broadcasting = False
            logger.info("Broadcast em tempo real parado")

# Instância global do serviço integrado
integrated_evacuation_service = IntegratedEvacuationService()
