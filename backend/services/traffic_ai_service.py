"""
Serviço de IA para evacuação sem congestionamento.
Implementa grafo viário, BPR, assignment iterativo e previsão ML.
"""

import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from shapely.geometry import Point, Polygon, LineString
from scipy.optimize import minimize_scalar
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import math
import time
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

@dataclass
class EdgeProperties:
    """Propriedades de uma aresta do grafo viário."""
    length: float  # metros
    free_speed_ms: float  # m/s
    capacity_vph: float  # veículos por hora
    lanes: int
    highway_type: str
    grade: float  # inclinação em %
    surface: str
    risk_penalty: float = 1.0  # multiplicador de custo para zonas de risco

@dataclass
class DemandOD:
    """Origem-Destino para evacuação."""
    origin_id: str
    destination_id: str
    demand: float  # número de veículos
    priority: int = 1  # 1=alta, 2=média, 3=baixa

class TrafficAIService:
    """Serviço principal de IA para tráfego e evacuação."""
    
    def __init__(self):
        self.graph = None
        self.edge_properties = {}
        self.demand_matrix = {}
        self.ml_model = None
        self.scaler = StandardScaler()
        self.bpr_alpha = 0.15
        self.bpr_beta = 4.0
        self.convergence_threshold = 0.001
        self.max_iterations = 50
        
    def load_road_network(self, center_point: Tuple[float, float], radius_km: float = 10) -> Dict:
        """
        Carrega rede viária usando OSMnx e constrói grafo com propriedades.
        
        Args:
            center_point: (lat, lon) do centro da área
            radius_km: Raio da área a ser carregada
            
        Returns:
            Dicionário com informações do grafo carregado
        """
        try:
            lat, lon = center_point
            
            # Configurar OSMnx
            ox.config(use_cache=True, log_console=False)
            
            # Carregar grafo da rede viária
            print(f"Carregando rede viária para ({lat}, {lon}) com raio {radius_km}km...")
            self.graph = ox.graph_from_point(
                center_point=(lat, lon),
                dist=radius_km * 1000,  # converter para metros
                network_type='drive',  # apenas vias para veículos
                simplify=True
            )
            
            # Adicionar propriedades às arestas
            self._add_edge_properties()
            
            # Estatísticas do grafo
            stats = {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "radius_km": radius_km,
                "center": center_point,
                "loaded_at": time.time()
            }
            
            print(f"Rede carregada: {stats['nodes']} nós, {stats['edges']} arestas")
            return {"success": True, "stats": stats}
            
        except Exception as e:
            return {"success": False, "error": f"Erro ao carregar rede viária: {str(e)}"}
    
    def _add_edge_properties(self):
        """Adiciona propriedades detalhadas às arestas do grafo."""
        for u, v, key, data in self.graph.edges(data=True, keys=True):
            edge_id = (u, v, key)
            
            # Propriedades básicas
            length = data.get('length', 100)  # metros
            highway_type = data.get('highway', 'residential')
            lanes = data.get('lanes', 1)
            
            # Velocidade livre baseada no tipo de via
            speed_limits = {
                'motorway': 120, 'trunk': 100, 'primary': 80, 'secondary': 60,
                'tertiary': 50, 'residential': 30, 'unclassified': 40
            }
            free_speed_kmh = speed_limits.get(highway_type, 50)
            free_speed_ms = free_speed_kmh / 3.6
            
            # Capacidade baseada no tipo de via e número de faixas
            capacity_per_lane = {
                'motorway': 2000, 'trunk': 1800, 'primary': 1500, 'secondary': 1200,
                'tertiary': 1000, 'residential': 800, 'unclassified': 900
            }
            base_capacity = capacity_per_lane.get(highway_type, 1000)
            capacity_vph = base_capacity * lanes
            
            # Inclinação (simulada baseada na elevação se disponível)
            grade = 0.0  # TODO: calcular baseado em dados de elevação
            
            # Superfície
            surface = data.get('surface', 'asphalt')
            
            self.edge_properties[edge_id] = EdgeProperties(
                length=length,
                free_speed_ms=free_speed_ms,
                capacity_vph=capacity_vph,
                lanes=lanes,
                highway_type=highway_type,
                grade=grade,
                surface=surface
            )
    
    def apply_risk_zones(self, risk_zones_geojson: Dict, penalty_multiplier: float = 10.0):
        """
        Aplica penalidades às arestas que cruzam zonas de risco.
        
        Args:
            risk_zones_geojson: GeoJSON com zonas de risco
            penalty_multiplier: Multiplicador de custo para arestas em risco
        """
        try:
            # Criar polígonos de risco
            risk_polygons = []
            for feature in risk_zones_geojson.get("features", []):
                if feature["geometry"]["type"] == "Polygon":
                    coords = feature["geometry"]["coordinates"][0]
                    polygon = Polygon(coords)
                    risk_polygons.append(polygon)
            
            # Verificar cada aresta
            penalized_edges = 0
            for edge_id, props in self.edge_properties.items():
                u, v, key = edge_id
                
                # Coordenadas dos nós
                node_u = self.graph.nodes[u]
                node_v = self.graph.nodes[v]
                
                # Criar linha da aresta
                edge_line = LineString([
                    (node_u['x'], node_u['y']),
                    (node_v['x'], node_v['y'])
                ])
                
                # Verificar se cruza alguma zona de risco
                for risk_polygon in risk_polygons:
                    if edge_line.intersects(risk_polygon):
                        props.risk_penalty = penalty_multiplier
                        penalized_edges += 1
                        break
            
            return {
                "success": True,
                "penalized_edges": penalized_edges,
                "total_edges": len(self.edge_properties),
                "penalty_multiplier": penalty_multiplier
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erro ao aplicar zonas de risco: {str(e)}"}
    
    def calculate_bpr_cost(self, edge_id: Tuple, flow: float) -> float:
        """
        Calcula custo de viagem usando função BPR (Bureau of Public Roads).
        
        Args:
            edge_id: ID da aresta (u, v, key)
            flow: Fluxo atual na aresta (veículos/hora)
            
        Returns:
            Tempo de viagem em segundos
        """
        if edge_id not in self.edge_properties:
            return float('inf')
        
        props = self.edge_properties[edge_id]
        
        # Tempo livre de fluxo
        t0 = props.length / props.free_speed_ms
        
        # Aplicar função BPR
        v_c_ratio = flow / props.capacity_vph if props.capacity_vph > 0 else 0
        t_bpr = t0 * (1 + self.bpr_alpha * (v_c_ratio ** self.bpr_beta))
        
        # Aplicar penalidade de risco
        t_final = t_bpr * props.risk_penalty
        
        return t_final
    
    def generate_demand_matrix(self, origins: List[Dict], destinations: List[Dict]) -> Dict:
        """
        Gera matriz de demanda origem-destino baseada em densidade populacional.
        
        Args:
            origins: Lista de origens com coordenadas e população
            destinations: Lista de destinos com coordenadas e capacidade
            
        Returns:
            Dicionário com matriz de demanda
        """
        try:
            demand_matrix = {}
            total_demand = 0
            
            for origin in origins:
                origin_id = origin['id']
                origin_lat = origin['latitude']
                origin_lon = origin['longitude']
                population = origin.get('population', 1000)
                
                # Encontrar nó mais próximo da origem
                origin_node = self._find_nearest_node(origin_lat, origin_lon)
                
                for destination in destinations:
                    dest_id = destination['id']
                    dest_lat = destination['latitude']
                    dest_lon = destination['longitude']
                    capacity = destination.get('capacity', 500)
                    
                    # Encontrar nó mais próximo do destino
                    dest_node = self._find_nearest_node(dest_lat, dest_lon)
                    
                    # Calcular demanda proporcional à população e capacidade
                    # Simplificação: distribuir população proporcionalmente
                    base_demand = population * 0.3  # 30% da população evacua por carro
                    capacity_factor = capacity / sum(d.get('capacity', 500) for d in destinations)
                    demand = base_demand * capacity_factor
                    
                    demand_matrix[(origin_node, dest_node)] = DemandOD(
                        origin_id=origin_id,
                        destination_id=dest_id,
                        demand=demand,
                        priority=origin.get('priority', 1)
                    )
                    
                    total_demand += demand
            
            self.demand_matrix = demand_matrix
            
            return {
                "success": True,
                "total_od_pairs": len(demand_matrix),
                "total_demand": total_demand,
                "demand_matrix": {
                    str(k): {
                        "origin_id": v.origin_id,
                        "destination_id": v.destination_id,
                        "demand": v.demand,
                        "priority": v.priority
                    } for k, v in demand_matrix.items()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erro ao gerar matriz de demanda: {str(e)}"}
    
    def _find_nearest_node(self, lat: float, lon: float) -> int:
        """Encontra o nó mais próximo de uma coordenada."""
        min_dist = float('inf')
        nearest_node = None
        
        for node_id, node_data in self.graph.nodes(data=True):
            node_lat = node_data['y']
            node_lon = node_data['x']
            
            dist = math.sqrt((lat - node_lat)**2 + (lon - node_lon)**2)
            if dist < min_dist:
                min_dist = dist
                nearest_node = node_id
        
        return nearest_node
    
    def frank_wolfe_assignment(self) -> Dict:
        """
        Executa assignment iterativo usando algoritmo Frank-Wolfe.
        
        Returns:
            Dicionário com resultados do assignment
        """
        try:
            if not self.demand_matrix:
                return {"success": False, "error": "Matriz de demanda não definida"}
            
            # Inicializar fluxos
            edge_flows = {edge_id: 0.0 for edge_id in self.edge_properties.keys()}
            
            # Iterações do Frank-Wolfe
            for iteration in range(self.max_iterations):
                old_flows = edge_flows.copy()
                
                # Calcular custos atuais
                edge_costs = {}
                for edge_id in self.edge_properties.keys():
                    edge_costs[edge_id] = self.calculate_bpr_cost(edge_id, edge_flows[edge_id])
                
                # Atualizar grafo com custos
                for edge_id, cost in edge_costs.items():
                    u, v, key = edge_id
                    self.graph[u][v][key]['cost'] = cost
                
                # Calcular novos fluxos (menor caminho)
                new_flows = {edge_id: 0.0 for edge_id in self.edge_properties.keys()}
                
                for (origin, dest), od_data in self.demand_matrix.items():
                    try:
                        # Encontrar menor caminho
                        path = nx.shortest_path(
                            self.graph, 
                            origin, 
                            dest, 
                            weight='cost'
                        )
                        
                        # Adicionar fluxo às arestas do caminho
                        for i in range(len(path) - 1):
                            edge_id = self._get_edge_id(path[i], path[i+1])
                            if edge_id in new_flows:
                                new_flows[edge_id] += od_data.demand
                                
                    except nx.NetworkXNoPath:
                        print(f"Sem caminho entre {origin} e {dest}")
                        continue
                
                # Line search para encontrar melhor step size
                step_size = self._line_search(old_flows, new_flows)
                
                # Atualizar fluxos
                for edge_id in edge_flows:
                    edge_flows[edge_id] = (
                        (1 - step_size) * old_flows[edge_id] + 
                        step_size * new_flows[edge_id]
                    )
                
                # Verificar convergência
                gap = self._calculate_gap(old_flows, edge_flows)
                print(f"Iteração {iteration + 1}: Gap = {gap:.6f}")
                
                if gap < self.convergence_threshold:
                    print(f"Convergência alcançada na iteração {iteration + 1}")
                    break
            
            # Calcular estatísticas finais
            stats = self._calculate_assignment_stats(edge_flows)
            
            return {
                "success": True,
                "iterations": iteration + 1,
                "final_gap": gap,
                "converged": gap < self.convergence_threshold,
                "edge_flows": {str(k): v for k, v in edge_flows.items()},
                "statistics": stats
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erro no assignment Frank-Wolfe: {str(e)}"}
    
    def _get_edge_id(self, u: int, v: int) -> Tuple:
        """Obtém ID da aresta entre dois nós."""
        for key in self.graph[u][v]:
            return (u, v, key)
        return None
    
    def _line_search(self, old_flows: Dict, new_flows: Dict) -> float:
        """Executa line search para encontrar melhor step size."""
        def objective(alpha):
            total_cost = 0
            for edge_id in old_flows:
                flow = (1 - alpha) * old_flows[edge_id] + alpha * new_flows[edge_id]
                cost = self.calculate_bpr_cost(edge_id, flow)
                total_cost += cost * flow
            return total_cost
        
        result = minimize_scalar(objective, bounds=(0, 1), method='bounded')
        return result.x
    
    def _calculate_gap(self, old_flows: Dict, new_flows: Dict) -> float:
        """Calcula gap relativo para verificar convergência."""
        total_old = sum(abs(f) for f in old_flows.values())
        total_change = sum(abs(new_flows[k] - old_flows[k]) for k in old_flows)
        
        if total_old == 0:
            return 0
        
        return total_change / total_old
    
    def _calculate_assignment_stats(self, edge_flows: Dict) -> Dict:
        """Calcula estatísticas do assignment final."""
        max_flow = max(edge_flows.values()) if edge_flows else 0
        avg_flow = np.mean(list(edge_flows.values())) if edge_flows else 0
        
        # Identificar gargalos (arestas com alta utilização)
        bottlenecks = []
        for edge_id, flow in edge_flows.items():
            if edge_id in self.edge_properties:
                capacity = self.edge_properties[edge_id].capacity_vph
                utilization = flow / capacity if capacity > 0 else 0
                
                if utilization > 0.8:  # 80% de utilização
                    bottlenecks.append({
                        "edge_id": str(edge_id),
                        "flow": flow,
                        "capacity": capacity,
                        "utilization": utilization
                    })
        
        return {
            "max_flow": max_flow,
            "avg_flow": avg_flow,
            "total_flow": sum(edge_flows.values()),
            "bottlenecks": bottlenecks,
            "bottleneck_count": len(bottlenecks)
        }
    
    def train_ml_model(self, synthetic_data: bool = True) -> Dict:
        """
        Treina modelo ML para previsão de tempo de viagem.
        
        Args:
            synthetic_data: Se True, gera dados sintéticos para treinamento
            
        Returns:
            Dicionário com informações do modelo treinado
        """
        try:
            if synthetic_data:
                # Gerar dados sintéticos
                X, y = self._generate_synthetic_training_data()
            else:
                # TODO: Carregar dados históricos reais
                X, y = self._load_historical_data()
            
            # Dividir dados
            split_idx = int(0.8 * len(X))
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo (Gradient Boosting)
            self.ml_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.ml_model.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            train_score = self.ml_model.score(X_train_scaled, y_train)
            test_score = self.ml_model.score(X_test_scaled, y_test)
            
            # Salvar modelo
            model_path = "models/traffic_ml_model.pkl"
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self.ml_model, model_path)
            joblib.dump(self.scaler, "models/traffic_scaler.pkl")
            
            return {
                "success": True,
                "model_type": "GradientBoostingRegressor",
                "train_score": train_score,
                "test_score": test_score,
                "features": ["hour", "rainfall", "visibility", "wind_speed", "grade", "surface_type", "lanes"],
                "model_path": model_path
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erro ao treinar modelo ML: {str(e)}"}
    
    def _generate_synthetic_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Gera dados sintéticos para treinamento do modelo ML."""
        np.random.seed(42)
        n_samples = 10000
        
        # Features
        features = []
        
        # Hora do dia (0-23)
        hour = np.random.randint(0, 24, n_samples)
        features.append(hour)
        
        # Condições meteorológicas
        rainfall = np.random.exponential(2, n_samples)  # mm/h
        visibility = np.random.normal(10, 3, n_samples)  # km
        wind_speed = np.random.exponential(5, n_samples)  # m/s
        
        features.extend([rainfall, visibility, wind_speed])
        
        # Propriedades da via
        grade = np.random.normal(0, 5, n_samples)  # %
        surface_type = np.random.choice([0, 1, 2], n_samples)  # 0=asphalt, 1=concrete, 2=gravel
        lanes = np.random.choice([1, 2, 3, 4], n_samples, p=[0.3, 0.4, 0.2, 0.1])
        
        features.extend([grade, surface_type, lanes])
        
        X = np.column_stack(features)
        
        # Tempo de viagem alvo (função complexa das features)
        base_time = 60  # segundos base
        hour_effect = 20 * np.sin(2 * np.pi * hour / 24)  # efeito diurno
        weather_effect = 10 * rainfall + 5 * (10 - visibility) + 2 * wind_speed
        road_effect = 3 * abs(grade) + 5 * surface_type + 2 * (4 - lanes)
        noise = np.random.normal(0, 5, n_samples)
        
        y = base_time + hour_effect + weather_effect + road_effect + noise
        y = np.maximum(y, 10)  # tempo mínimo de 10 segundos
        
        return X, y
    
    def predict_travel_time(self, features: Dict) -> float:
        """
        Prediz tempo de viagem usando modelo ML.
        
        Args:
            features: Dicionário com features para predição
            
        Returns:
            Tempo de viagem previsto em segundos
        """
        try:
            if self.ml_model is None:
                # Carregar modelo se não estiver carregado
                self._load_ml_model()
            
            # Preparar features
            feature_vector = np.array([
                features.get('hour', 12),
                features.get('rainfall', 0),
                features.get('visibility', 10),
                features.get('wind_speed', 5),
                features.get('grade', 0),
                features.get('surface_type', 0),
                features.get('lanes', 2)
            ]).reshape(1, -1)
            
            # Normalizar e predizer
            feature_vector_scaled = self.scaler.transform(feature_vector)
            prediction = self.ml_model.predict(feature_vector_scaled)[0]
            
            return max(prediction, 10)  # tempo mínimo
            
        except Exception as e:
            print(f"Erro na predição ML: {e}")
            return 60.0  # tempo padrão
    
    def _load_ml_model(self):
        """Carrega modelo ML salvo."""
        try:
            self.ml_model = joblib.load("models/traffic_ml_model.pkl")
            self.scaler = joblib.load("models/traffic_scaler.pkl")
        except:
            # Se não conseguir carregar, treinar novo modelo
            self.train_ml_model()
    
    def get_evacuation_routes(self, k_routes: int = 3) -> Dict:
        """
        Gera k rotas alternativas para evacuação.
        
        Args:
            k_routes: Número de rotas alternativas por OD pair
            
        Returns:
            Dicionário com rotas calculadas
        """
        try:
            if not self.demand_matrix:
                return {"success": False, "error": "Matriz de demanda não definida"}
            
            all_routes = {}
            
            for (origin, dest), od_data in self.demand_matrix.items():
                try:
                    # Calcular k caminhos mais curtos
                    paths = list(nx.shortest_simple_paths(
                        self.graph, 
                        origin, 
                        dest, 
                        weight='cost'
                    ))[:k_routes]
                    
                    route_info = []
                    for i, path in enumerate(paths):
                        # Calcular métricas da rota
                        total_distance = 0
                        total_time = 0
                        route_coords = []
                        
                        for j in range(len(path) - 1):
                            edge_id = self._get_edge_id(path[j], path[j+1])
                            if edge_id in self.edge_properties:
                                props = self.edge_properties[edge_id]
                                total_distance += props.length
                                total_time += props.length / props.free_speed_ms
                                
                                # Coordenadas do nó
                                node_data = self.graph.nodes[path[j]]
                                route_coords.append([node_data['x'], node_data['y']])
                        
                        # Adicionar último nó
                        if path:
                            last_node = self.graph.nodes[path[-1]]
                            route_coords.append([last_node['x'], last_node['y']])
                        
                        route_info.append({
                            "route_id": f"{od_data.origin_id}_{od_data.destination_id}_{i}",
                            "path_nodes": path,
                            "coordinates": route_coords,
                            "distance_m": total_distance,
                            "distance_km": total_distance / 1000,
                            "time_seconds": total_time,
                            "time_minutes": total_time / 60,
                            "demand": od_data.demand,
                            "priority": od_data.priority
                        })
                    
                    all_routes[f"{od_data.origin_id}_{od_data.destination_id}"] = route_info
                    
                except nx.NetworkXNoPath:
                    continue
            
            return {
                "success": True,
                "total_od_pairs": len(all_routes),
                "routes_per_pair": k_routes,
                "routes": all_routes
            }
            
        except Exception as e:
            return {"success": False, "error": f"Erro ao gerar rotas de evacuação: {str(e)}"}

# Instância global do serviço
traffic_ai_service = TrafficAIService()
