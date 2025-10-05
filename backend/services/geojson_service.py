"""
Serviço para geração de polígonos GeoJSON das zonas de risco de impacto de asteroides.
"""

import math
import json
from typing import Dict, List, Tuple
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

def create_circle_polygon(center_lat: float, center_lon: float, radius_km: float, num_points: int = 32) -> List[List[float]]:
    """
    Cria um polígono circular para representar uma zona de risco.
    
    Args:
        center_lat: Latitude do centro
        center_lon: Longitude do centro
        radius_km: Raio em quilômetros
        num_points: Número de pontos para definir o círculo
    
    Returns:
        Lista de coordenadas [lon, lat] do polígono
    """
    # Conversão aproximada de km para graus (1 grau ≈ 111 km)
    radius_deg = radius_km / 111.0
    
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        lat = center_lat + radius_deg * math.cos(angle)
        lon = center_lon + radius_deg * math.sin(angle)
        points.append([lon, lat])
    
    # Fechar o polígono
    points.append(points[0])
    return points

def create_ellipse_polygon(center_lat: float, center_lon: float, 
                          semi_major_km: float, semi_minor_km: float, 
                          rotation_deg: float = 0, num_points: int = 32) -> List[List[float]]:
    """
    Cria um polígono elíptico para representar zonas de risco alongadas.
    
    Args:
        center_lat: Latitude do centro
        center_lon: Longitude do centro
        semi_major_km: Semi-eixo maior em km
        semi_minor_km: Semi-eixo menor em km
        rotation_deg: Rotação em graus
        num_points: Número de pontos para definir a elipse
    
    Returns:
        Lista de coordenadas [lon, lat] do polígono
    """
    # Conversão para graus
    semi_major_deg = semi_major_km / 111.0
    semi_minor_deg = semi_minor_km / 111.0
    rotation_rad = math.radians(rotation_deg)
    
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        
        # Coordenadas na elipse não rotacionada
        x = semi_major_deg * math.cos(angle)
        y = semi_minor_deg * math.sin(angle)
        
        # Aplicar rotação
        x_rot = x * math.cos(rotation_rad) - y * math.sin(rotation_rad)
        y_rot = x * math.sin(rotation_rad) + y * math.cos(rotation_rad)
        
        # Transladar para o centro
        lat = center_lat + y_rot
        lon = center_lon + x_rot
        points.append([lon, lat])
    
    # Fechar o polígono
    points.append(points[0])
    return points

def generate_impact_risk_zones(impact_lat: float, impact_lon: float, 
                              physics_results: Dict) -> Dict:
    """
    Gera todas as zonas de risco GeoJSON baseadas nos resultados da simulação física.
    
    Args:
        impact_lat: Latitude do ponto de impacto
        impact_lon: Longitude do ponto de impacto
        physics_results: Resultados da simulação física
    
    Returns:
        Dicionário com todas as zonas de risco em formato GeoJSON
    """
    zones = []
    
    # 1. Zona da Cratera
    crater_diameter_km = physics_results["cratera"]["diametro_final_km"]
    if crater_diameter_km > 0:
        crater_zone = {
            "type": "Feature",
            "properties": {
                "zone_type": "crater",
                "name": "Zona da Cratera",
                "description": f"Cratera de {crater_diameter_km:.2f} km de diâmetro",
                "risk_level": "critical",
                "color": "#8B0000",
                "opacity": 0.8,
                "diameter_km": crater_diameter_km,
                "depth_m": physics_results["cratera"]["profundidade_m"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [create_circle_polygon(impact_lat, impact_lon, crater_diameter_km / 2)]
            }
        }
        zones.append(crater_zone)
    
    # 2. Zonas de Queimadura (Fireball)
    fireball = physics_results["fireball"]
    if fireball["is_airburst"]:
        for burn_level in ["raio_queimadura_3_grau_km", "raio_queimadura_2_grau_km", "raio_queimadura_1_grau_km"]:
            radius_km = fireball[burn_level]
            if radius_km > 0:
                level_name = burn_level.replace("raio_queimadura_", "").replace("_km", "").replace("_", "º grau")
                burn_zone = {
                    "type": "Feature",
                    "properties": {
                        "zone_type": "thermal_burn",
                        "name": f"Zona de Queimadura {level_name}",
                        "description": f"Queimaduras de {level_name} até {radius_km:.2f} km",
                        "risk_level": "high" if "3_grau" in burn_level else "moderate" if "2_grau" in burn_level else "low",
                        "color": "#FF4500" if "3_grau" in burn_level else "#FF8C00" if "2_grau" in burn_level else "#FFA500",
                        "opacity": 0.6,
                        "radius_km": radius_km
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [create_circle_polygon(impact_lat, impact_lon, radius_km)]
                    }
                }
                zones.append(burn_zone)
    
    # 3. Zonas de Sobrepressão (Onda de Choque)
    shockwave = physics_results["onda_de_choque_e_vento"]
    for psi_level in ["psi_5_predios_destruidos", "psi_3_casas_destruidas", "psi_1_janelas_quebradas"]:
        radius_km = shockwave["raios_sobrepressao_km"][psi_level]
        if radius_km > 0:
            psi_value = psi_level.replace("psi_", "").replace("_predios_destruidos", "").replace("_casas_destruidas", "").replace("_janelas_quebradas", "")
            damage_desc = psi_level.replace("psi_", "").replace("_", " ").title()
            
            blast_zone = {
                "type": "Feature",
                "properties": {
                    "zone_type": "blast_overpressure",
                    "name": f"Sobrepressão {psi_value} PSI",
                    "description": damage_desc,
                    "risk_level": "critical" if psi_value == "5" else "high" if psi_value == "3" else "moderate",
                    "color": "#DC143C" if psi_value == "5" else "#FF6347" if psi_value == "3" else "#FFB6C1",
                    "opacity": 0.7,
                    "radius_km": radius_km,
                    "psi_level": psi_value
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [create_circle_polygon(impact_lat, impact_lon, radius_km)]
                }
            }
            zones.append(blast_zone)
    
    # 4. Zona de Tremor Sísmico
    earthquake = physics_results["terremoto"]
    tremor_radius_km = earthquake["distancia_sentida_km"]
    if tremor_radius_km > 0:
        tremor_zone = {
            "type": "Feature",
            "properties": {
                "zone_type": "seismic_shaking",
                "name": "Zona de Tremor Sísmico",
                "description": f"Tremor sentido até {tremor_radius_km:.0f} km (Magnitude {earthquake['magnitude_richter']})",
                "risk_level": "moderate",
                "color": "#8B4513",
                "opacity": 0.5,
                "radius_km": tremor_radius_km,
                "magnitude_richter": earthquake["magnitude_richter"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [create_circle_polygon(impact_lat, impact_lon, tremor_radius_km)]
            }
        }
        zones.append(tremor_zone)
    
    # 5. Zona de Tsunami (se aplicável)
    tsunami = physics_results["tsunami"]
    if tsunami["tsunami_generated"]:
        # Zona de impacto direto do tsunami
        tsunami_radius_km = 50  # Raio aproximado para impacto direto
        tsunami_zone = {
            "type": "Feature",
            "properties": {
                "zone_type": "tsunami_impact",
                "name": "Zona de Impacto do Tsunami",
                "description": f"Tsunami com altura inicial de {tsunami['initial_wave_height_m']:.1f}m",
                "risk_level": "critical",
                "color": "#0066CC",
                "opacity": 0.6,
                "radius_km": tsunami_radius_km,
                "initial_wave_height_m": tsunami["initial_wave_height_m"],
                "max_runup_m": tsunami["max_runup_m"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [create_circle_polygon(impact_lat, impact_lon, tsunami_radius_km)]
            }
        }
        zones.append(tsunami_zone)
    
    # 6. Zonas de Dispersão Atmosférica (se aplicável)
    dispersion = physics_results["dispersao_atmosferica"]
    if dispersion["atmospheric_dispersion"]:
        wind_direction = dispersion["plume_dispersion"]["wind_direction_deg"]
        wind_speed = dispersion["plume_dispersion"]["wind_speed_ms"]
        
        # Zona principal da pluma (elíptica alongada na direção do vento)
        sigma_y = dispersion["plume_dispersion"]["sigma_y_km"]
        sigma_z = dispersion["plume_dispersion"]["sigma_z_km"]
        
        plume_zone = {
            "type": "Feature",
            "properties": {
                "zone_type": "atmospheric_plume",
                "name": "Pluma de Poluentes Atmosféricos",
                "description": f"Dispersão de poluentes na direção do vento ({wind_direction}°)",
                "risk_level": "moderate",
                "color": "#9370DB",
                "opacity": 0.4,
                "wind_direction_deg": wind_direction,
                "wind_speed_ms": wind_speed,
                "sigma_y_km": sigma_y,
                "sigma_z_km": sigma_z
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [create_ellipse_polygon(
                    impact_lat, impact_lon, 
                    sigma_y * 3, sigma_z * 3, 
                    wind_direction
                )]
            }
        }
        zones.append(plume_zone)
    
    # Criar o GeoJSON final
    geojson = {
        "type": "FeatureCollection",
        "features": zones,
        "properties": {
            "impact_coordinates": [impact_lon, impact_lat],
            "total_zones": len(zones),
            "simulation_data": {
                "energy_megatons": physics_results["energia"]["equivalente_tnt_megatons"],
                "diameter_m": physics_results["inputs"]["diametro_m"],
                "velocity_kms": physics_results["inputs"]["velocidade_kms"],
                "terrain_type": physics_results["inputs"]["tipo_terreno"]
            }
        }
    }
    
    return geojson

def generate_evacuation_zones(risk_zones_geojson: Dict, buffer_km: float = 5.0) -> Dict:
    """
    Gera zonas de evacuação baseadas nas zonas de risco.
    
    Args:
        risk_zones_geojson: GeoJSON das zonas de risco
        buffer_km: Buffer adicional em km para evacuação
    
    Returns:
        GeoJSON das zonas de evacuação
    """
    evacuation_zones = []
    
    for feature in risk_zones_geojson["features"]:
        zone_type = feature["properties"]["zone_type"]
        
        # Aplicar buffer baseado no tipo de zona
        if zone_type == "crater":
            buffer_multiplier = 2.0
        elif zone_type == "blast_overpressure":
            buffer_multiplier = 1.5
        elif zone_type == "thermal_burn":
            buffer_multiplier = 1.2
        else:
            buffer_multiplier = 1.0
        
        # Calcular buffer efetivo
        effective_buffer = buffer_km * buffer_multiplier
        
        # Criar zona de evacuação (simplificada - círculo maior)
        if "radius_km" in feature["properties"]:
            original_radius = feature["properties"]["radius_km"]
            evacuation_radius = original_radius + effective_buffer
            
            # Obter coordenadas do centro (assumindo círculo)
            coords = feature["geometry"]["coordinates"][0]
            center_lon = sum([c[0] for c in coords]) / len(coords)
            center_lat = sum([c[1] for c in coords]) / len(coords)
            
            evacuation_zone = {
                "type": "Feature",
                "properties": {
                    "zone_type": "evacuation",
                    "name": f"Zona de Evacuação - {feature['properties']['name']}",
                    "description": f"Área de evacuação com buffer de {effective_buffer:.1f}km",
                    "risk_level": "evacuation",
                    "color": "#FFD700",
                    "opacity": 0.3,
                    "original_zone": zone_type,
                    "buffer_km": effective_buffer
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [create_circle_polygon(center_lat, center_lon, evacuation_radius)]
                }
            }
            evacuation_zones.append(evacuation_zone)
    
    return {
        "type": "FeatureCollection",
        "features": evacuation_zones,
        "properties": {
            "total_evacuation_zones": len(evacuation_zones),
            "buffer_km": buffer_km
        }
    }
