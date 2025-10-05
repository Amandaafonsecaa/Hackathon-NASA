"""
Serviço para cálculo de rotas de evacuação otimizadas considerando zonas de risco.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union
import networkx as nx

def calculate_evacuation_routes(
    start_lat: float, 
    start_lon: float,
    risk_zones_geojson: Dict,
    evacuation_points: List[Dict],
    transport_mode: str = "car",
    buffer_km: float = 5.0
) -> Dict:
    """
    Calcula rotas de evacuação otimizadas evitando zonas de risco.
    
    Args:
        start_lat: Latitude do ponto de origem
        start_lon: Longitude do ponto de origem
        risk_zones_geojson: GeoJSON das zonas de risco
        evacuation_points: Lista de pontos de evacuação seguros
        transport_mode: Modo de transporte ("car", "ambulance", "pedestrian")
        buffer_km: Buffer adicional em km para evitar zonas de risco
    
    Returns:
        Dicionário com rotas calculadas e estatísticas
    """
    try:
        # Parâmetros por modo de transporte
        transport_params = _get_transport_parameters(transport_mode)
        
        # Criar polígonos de risco com buffer
        risk_polygons = _create_risk_polygons_with_buffer(risk_zones_geojson, buffer_km)
        
        # Calcular rotas para cada ponto de evacuação
        evacuation_routes = []
        
        for evac_point in evacuation_points:
            route = _calculate_single_evacuation_route(
                start_point=(start_lat, start_lon),
                end_point=(evac_point["latitude"], evac_point["longitude"]),
                risk_polygons=risk_polygons,
                transport_params=transport_params,
                evac_point_info=evac_point
            )
            
            if route:
                evacuation_routes.append(route)
        
        # Ordenar rotas por prioridade (distância, tempo, segurança)
        evacuation_routes.sort(key=lambda x: x["priority_score"])
        
        # Calcular estatísticas gerais
        statistics = _calculate_evacuation_statistics(
            evacuation_routes, 
            start_lat, 
            start_lon, 
            risk_polygons
        )
        
        return {
            "success": True,
            "transport_mode": transport_mode,
            "total_routes": len(evacuation_routes),
            "statistics": statistics,
            "routes": evacuation_routes,
            "risk_avoidance": {
                "buffer_km": buffer_km,
                "risk_zones_avoided": len(risk_polygons)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao calcular rotas de evacuação: {str(e)}"
        }

def _get_transport_parameters(transport_mode: str) -> Dict:
    """Retorna parâmetros específicos para cada modo de transporte."""
    params = {
        "car": {
            "speed_kmh": 60,  # Velocidade média urbana
            "max_distance_km": 100,
            "route_precision": 0.5,  # km
            "avoid_highways": False,
            "priority_weight": {"distance": 0.4, "time": 0.4, "safety": 0.2}
        },
        "ambulance": {
            "speed_kmh": 80,  # Velocidade com sirene
            "max_distance_km": 50,
            "route_precision": 0.3,  # km
            "avoid_highways": False,
            "priority_weight": {"distance": 0.3, "time": 0.5, "safety": 0.2}
        },
        "pedestrian": {
            "speed_kmh": 5,  # Velocidade de caminhada
            "max_distance_km": 10,
            "route_precision": 0.1,  # km
            "avoid_highways": True,
            "priority_weight": {"distance": 0.5, "time": 0.3, "safety": 0.2}
        }
    }
    
    return params.get(transport_mode, params["car"])

def _create_risk_polygons_with_buffer(risk_zones_geojson: Dict, buffer_km: float) -> List[Polygon]:
    """Cria polígonos de risco com buffer adicional."""
    risk_polygons = []
    
    for feature in risk_zones_geojson.get("features", []):
        if feature["geometry"]["type"] == "Polygon":
            coords = feature["geometry"]["coordinates"][0]
            polygon = Polygon(coords)
            
            # Aplicar buffer baseado no tipo de risco
            zone_type = feature["properties"].get("zone_type", "")
            if zone_type == "crater":
                buffer_multiplier = 2.0
            elif zone_type == "blast_overpressure":
                buffer_multiplier = 1.5
            elif zone_type == "thermal_burn":
                buffer_multiplier = 1.2
            else:
                buffer_multiplier = 1.0
            
            effective_buffer = buffer_km * buffer_multiplier / 111.0  # Converter para graus
            buffered_polygon = polygon.buffer(effective_buffer)
            risk_polygons.append(buffered_polygon)
    
    return risk_polygons

def _calculate_single_evacuation_route(
    start_point: Tuple[float, float],
    end_point: Tuple[float, float],
    risk_polygons: List[Polygon],
    transport_params: Dict,
    evac_point_info: Dict
) -> Optional[Dict]:
    """Calcula uma única rota de evacuação."""
    try:
        start_lat, start_lon = start_point
        end_lat, end_lon = end_point
        
        # Calcular distância direta
        direct_distance = _calculate_distance_km(start_lat, start_lon, end_lat, end_lon)
        
        # Verificar se a rota direta é muito longa
        if direct_distance > transport_params["max_distance_km"]:
            return None
        
        # Calcular rota otimizada evitando zonas de risco
        route_coords = _calculate_optimized_route(
            start_point, 
            end_point, 
            risk_polygons, 
            transport_params
        )
        
        if not route_coords:
            return None
        
        # Calcular métricas da rota
        route_distance = _calculate_route_distance(route_coords)
        route_time_hours = route_distance / transport_params["speed_kmh"]
        safety_score = _calculate_route_safety(route_coords, risk_polygons)
        
        # Calcular score de prioridade
        priority_score = (
            route_distance * transport_params["priority_weight"]["distance"] +
            route_time_hours * 60 * transport_params["priority_weight"]["time"] +  # Converter para minutos
            (1 - safety_score) * 100 * transport_params["priority_weight"]["safety"]
        )
        
        return {
            "evacuation_point": {
                "name": evac_point_info.get("name", "Ponto de Evacuação"),
                "type": evac_point_info.get("type", "shelter"),
                "capacity": evac_point_info.get("capacity", 0),
                "coordinates": [end_lon, end_lat]
            },
            "route": {
                "coordinates": route_coords,
                "distance_km": round(route_distance, 2),
                "estimated_time_hours": round(route_time_hours, 2),
                "estimated_time_minutes": round(route_time_hours * 60, 0),
                "safety_score": round(safety_score, 2),
                "priority_score": round(priority_score, 2)
            },
            "direct_distance_km": round(direct_distance, 2),
            "route_efficiency": round(direct_distance / route_distance, 2) if route_distance > 0 else 1.0
        }
        
    except Exception as e:
        print(f"Erro ao calcular rota individual: {e}")
        return None

def _calculate_optimized_route(
    start_point: Tuple[float, float],
    end_point: Tuple[float, float],
    risk_polygons: List[Polygon],
    transport_params: Dict
) -> Optional[List[List[float]]]:
    """Calcula rota otimizada evitando zonas de risco."""
    try:
        start_lat, start_lon = start_point
        end_lat, end_lon = end_point
        
        # Algoritmo simplificado: criar waypoints intermediários
        precision = transport_params["route_precision"]
        
        # Calcular número de segmentos baseado na distância
        distance = _calculate_distance_km(start_lat, start_lon, end_lat, end_lon)
        num_segments = max(2, int(distance / precision))
        
        route_coords = []
        
        for i in range(num_segments + 1):
            t = i / num_segments
            
            # Interpolação linear
            lat = start_lat + t * (end_lat - start_lat)
            lon = start_lon + t * (end_lon - start_lon)
            
            # Verificar se o ponto está em zona de risco
            point = Point(lon, lat)
            in_risk_zone = any(polygon.contains(point) for polygon in risk_polygons)
            
            if in_risk_zone:
                # Desviar do ponto de risco
                lat, lon = _find_safe_alternative_point(
                    (lat, lon), 
                    risk_polygons, 
                    transport_params
                )
            
            route_coords.append([lon, lat])
        
        return route_coords
        
    except Exception as e:
        print(f"Erro ao calcular rota otimizada: {e}")
        return None

def _find_safe_alternative_point(
    original_point: Tuple[float, float],
    risk_polygons: List[Polygon],
    transport_params: Dict
) -> Tuple[float, float]:
    """Encontra um ponto seguro alternativo próximo ao ponto original."""
    lat, lon = original_point
    precision = transport_params["route_precision"] / 111.0  # Converter para graus
    
    # Tentar pontos em círculo ao redor do ponto original
    for radius in [precision, precision * 2, precision * 3]:
        for angle in range(0, 360, 30):  # A cada 30 graus
            angle_rad = math.radians(angle)
            new_lat = lat + radius * math.cos(angle_rad)
            new_lon = lon + radius * math.sin(angle_rad)
            
            point = Point(new_lon, new_lat)
            in_risk_zone = any(polygon.contains(point) for polygon in risk_polygons)
            
            if not in_risk_zone:
                return (new_lat, new_lon)
    
    # Se não encontrar ponto seguro, retornar o original
    return original_point

def _calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância em km entre dois pontos usando fórmula de Haversine."""
    R = 6371  # Raio da Terra em km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def _calculate_route_distance(route_coords: List[List[float]]) -> float:
    """Calcula distância total de uma rota."""
    total_distance = 0.0
    
    for i in range(len(route_coords) - 1):
        lon1, lat1 = route_coords[i]
        lon2, lat2 = route_coords[i + 1]
        distance = _calculate_distance_km(lat1, lon1, lat2, lon2)
        total_distance += distance
    
    return total_distance

def _calculate_route_safety(route_coords: List[List[float]], risk_polygons: List[Polygon]) -> float:
    """Calcula score de segurança de uma rota (0-1, onde 1 é mais seguro)."""
    if not route_coords:
        return 0.0
    
    safe_points = 0
    total_points = len(route_coords)
    
    for coord in route_coords:
        lon, lat = coord
        point = Point(lon, lat)
        in_risk_zone = any(polygon.contains(point) for polygon in risk_polygons)
        
        if not in_risk_zone:
            safe_points += 1
    
    return safe_points / total_points

def _calculate_evacuation_statistics(
    evacuation_routes: List[Dict],
    start_lat: float,
    start_lon: float,
    risk_polygons: List[Polygon]
) -> Dict:
    """Calcula estatísticas gerais das rotas de evacuação."""
    if not evacuation_routes:
        return {
            "total_routes": 0,
            "average_distance_km": 0,
            "average_time_hours": 0,
            "average_safety_score": 0,
            "recommended_route": None
        }
    
    distances = [route["route"]["distance_km"] for route in evacuation_routes]
    times = [route["route"]["estimated_time_hours"] for route in evacuation_routes]
    safety_scores = [route["route"]["safety_score"] for route in evacuation_routes]
    
    return {
        "total_routes": len(evacuation_routes),
        "average_distance_km": round(sum(distances) / len(distances), 2),
        "min_distance_km": round(min(distances), 2),
        "max_distance_km": round(max(distances), 2),
        "average_time_hours": round(sum(times) / len(times), 2),
        "min_time_hours": round(min(times), 2),
        "max_time_hours": round(max(times), 2),
        "average_safety_score": round(sum(safety_scores) / len(safety_scores), 2),
        "recommended_route": evacuation_routes[0] if evacuation_routes else None,
        "risk_zones_avoided": len(risk_polygons)
    }

def generate_evacuation_points_grid(
    center_lat: float,
    center_lon: float,
    radius_km: float,
    grid_size: int = 5
) -> List[Dict]:
    """
    Gera uma grade de pontos de evacuação em torno de um ponto central.
    """
    evacuation_points = []
    radius_deg = radius_km / 111.0
    
    for i in range(-grid_size, grid_size + 1):
        for j in range(-grid_size, grid_size + 1):
            lat = center_lat + (i * radius_deg / grid_size)
            lon = center_lon + (j * radius_deg / grid_size)
            
            # Calcular distância do centro
            distance = _calculate_distance_km(center_lat, center_lon, lat, lon)
            
            if distance <= radius_km:
                evacuation_points.append({
                    "name": f"Ponto de Evacuação {len(evacuation_points) + 1}",
                    "type": "emergency_shelter",
                    "capacity": 100,  # Capacidade padrão
                    "latitude": lat,
                    "longitude": lon,
                    "distance_from_center_km": round(distance, 2)
                })
    
    return evacuation_points
