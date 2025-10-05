"""
Serviço para integração com USGS APIs para dados de elevação e geologia.
"""

import requests
import rasterio
import numpy as np
from typing import Dict, List, Tuple, Optional
from shapely.geometry import Point, Polygon
import io
import json

class USGSService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://elevation.nationalmap.gov/arcgis/rest/services"
        self.dem_service_url = f"{self.base_url}/3DEPElevation/ImageServer"
        self.geology_service_url = f"{self.base_url}/USGS_Geologic_Map/MapServer"
        
    def get_elevation_data(self, lat: float, lon: float, buffer_km: float = 1.0) -> Dict:
        """
        Obtém dados de elevação para uma área específica.
        
        Args:
            lat: Latitude central
            lon: Longitude central
            buffer_km: Raio da área em km
        
        Returns:
            Dicionário com dados de elevação
        """
        try:
            # Converter buffer para graus (aproximadamente)
            buffer_deg = buffer_km / 111.0
            
            # Definir bounding box
            bbox = {
                "xmin": lon - buffer_deg,
                "ymin": lat - buffer_deg,
                "xmax": lon + buffer_deg,
                "ymax": lat + buffer_deg
            }
            
            # Parâmetros para a requisição
            params = {
                "bbox": f"{bbox['xmin']},{bbox['ymin']},{bbox['xmax']},{bbox['ymax']}",
                "bboxSR": "4326",  # WGS84
                "imageSR": "4326",
                "size": "256,256",  # Resolução da imagem
                "format": "tiff",
                "f": "json"
            }
            
            # Fazer requisição
            response = requests.get(f"{self.dem_service_url}/exportImage", params=params)
            response.raise_for_status()
            
            # Processar resposta
            data = response.json()
            
            if "href" in data:
                # Baixar dados de elevação
                elevation_data = self._download_elevation_data(data["href"])
                
                return {
                    "success": True,
                    "center_coordinates": [lon, lat],
                    "buffer_km": buffer_km,
                    "elevation_stats": elevation_data["stats"],
                    "elevation_range_m": elevation_data["range"],
                    "terrain_analysis": elevation_data["analysis"]
                }
            else:
                return {
                    "success": False,
                    "error": "Falha ao obter dados de elevação"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados de elevação: {str(e)}"
            }
    
    def _download_elevation_data(self, href: str) -> Dict:
        """Baixa e processa dados de elevação."""
        try:
            response = requests.get(href)
            response.raise_for_status()
            
            # Ler dados TIFF
            with rasterio.io.MemoryFile(response.content) as memfile:
                with memfile.open() as dataset:
                    elevation_array = dataset.read(1)
                    
                    # Calcular estatísticas
                    valid_data = elevation_array[elevation_array != dataset.nodata]
                    
                    stats = {
                        "min_elevation_m": float(np.min(valid_data)),
                        "max_elevation_m": float(np.max(valid_data)),
                        "mean_elevation_m": float(np.mean(valid_data)),
                        "std_elevation_m": float(np.std(valid_data)),
                        "total_pixels": int(np.size(valid_data))
                    }
                    
                    # Análise do terreno
                    analysis = self._analyze_terrain(elevation_array, valid_data)
                    
                    return {
                        "stats": stats,
                        "range": {
                            "elevation_range_m": stats["max_elevation_m"] - stats["min_elevation_m"]
                        },
                        "analysis": analysis
                    }
                    
        except Exception as e:
            return {
                "stats": {"error": str(e)},
                "range": {"error": str(e)},
                "analysis": {"error": str(e)}
            }
    
    def _analyze_terrain(self, elevation_array: np.ndarray, valid_data: np.ndarray) -> Dict:
        """Analisa características do terreno."""
        try:
            # Calcular gradientes (inclinação)
            grad_y, grad_x = np.gradient(elevation_array)
            slope = np.sqrt(grad_x**2 + grad_y**2)
            slope_degrees = np.arctan(slope) * 180 / np.pi
            
            # Análise de relevo
            elevation_range = np.max(valid_data) - np.min(valid_data)
            mean_elevation = np.mean(valid_data)
            
            # Classificação do terreno
            if elevation_range < 50:
                terrain_type = "Plano"
            elif elevation_range < 200:
                terrain_type = "Suavemente Ondulado"
            elif elevation_range < 500:
                terrain_type = "Ondulado"
            else:
                terrain_type = "Montanhoso"
            
            # Análise de declividade
            mean_slope = np.mean(slope_degrees[~np.isnan(slope_degrees)])
            
            if mean_slope < 5:
                slope_category = "Suave"
            elif mean_slope < 15:
                slope_category = "Moderada"
            elif mean_slope < 30:
                slope_category = "Íngreme"
            else:
                slope_category = "Muito Íngreme"
            
            return {
                "terrain_type": terrain_type,
                "elevation_range_m": float(elevation_range),
                "mean_elevation_m": float(mean_elevation),
                "mean_slope_degrees": float(mean_slope),
                "slope_category": slope_category,
                "max_slope_degrees": float(np.max(slope_degrees[~np.isnan(slope_degrees)])),
                "relief_ratio": float(elevation_range / mean_elevation) if mean_elevation > 0 else 0
            }
            
        except Exception as e:
            return {"error": f"Erro na análise do terreno: {str(e)}"}
    
    def get_geologic_data(self, lat: float, lon: float, buffer_km: float = 5.0) -> Dict:
        """
        Obtém dados geológicos para uma área específica.
        
        Args:
            lat: Latitude central
            lon: Longitude central
            buffer_km: Raio da área em km
        
        Returns:
            Dicionário com dados geológicos
        """
        try:
            # Converter buffer para graus
            buffer_deg = buffer_km / 111.0
            
            # Definir bounding box
            bbox = {
                "xmin": lon - buffer_deg,
                "ymin": lat - buffer_deg,
                "xmax": lon + buffer_deg,
                "ymax": lat + buffer_deg
            }
            
            # Parâmetros para a requisição
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "outSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "f": "json"
            }
            
            # Fazer requisição
            response = requests.get(f"{self.geology_service_url}/0/query", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "features" in data and len(data["features"]) > 0:
                feature = data["features"][0]
                attributes = feature.get("attributes", {})
                
                return {
                    "success": True,
                    "coordinates": [lon, lat],
                    "geologic_unit": attributes.get("UNIT_NAME", "Desconhecido"),
                    "age": attributes.get("AGE", "Desconhecido"),
                    "lithology": attributes.get("LITHOLOGY", "Desconhecido"),
                    "description": attributes.get("DESCRIPTION", "Sem descrição disponível")
                }
            else:
                return {
                    "success": False,
                    "error": "Nenhum dado geológico encontrado para esta localização"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados geológicos: {str(e)}"
            }
    
    def analyze_tsunami_impact_terrain(self, lat: float, lon: float, tsunami_height_m: float) -> Dict:
        """
        Analisa o terreno para impacto de tsunami.
        
        Args:
            lat: Latitude do ponto de impacto
            lon: Longitude do ponto de impacto
            tsunami_height_m: Altura estimada do tsunami
        
        Returns:
            Análise de impacto de tsunami no terreno
        """
        try:
            # Obter dados de elevação em área maior para análise de tsunami
            elevation_data = self.get_elevation_data(lat, lon, buffer_km=20)
            
            if not elevation_data["success"]:
                return {
                    "success": False,
                    "error": "Falha ao obter dados de elevação"
                }
            
            # Simular propagação do tsunami
            tsunami_analysis = self._simulate_tsunami_propagation(
                lat, lon, tsunami_height_m, elevation_data
            )
            
            return {
                "success": True,
                "tsunami_height_m": tsunami_height_m,
                "impact_point": [lon, lat],
                "elevation_data": elevation_data,
                "tsunami_propagation": tsunami_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise de tsunami: {str(e)}"
            }
    
    def _simulate_tsunami_propagation(self, lat: float, lon: float, height_m: float, elevation_data: Dict) -> Dict:
        """Simula a propagação do tsunami baseada na topografia."""
        try:
            # Dados básicos da análise
            mean_elevation = elevation_data["elevation_stats"]["mean_elevation_m"]
            terrain_type = elevation_data["elevation_stats"]["terrain_analysis"]["terrain_type"]
            
            # Calcular alcance do tsunami
            # Simplificação baseada na altura e topografia
            if terrain_type == "Plano":
                propagation_factor = 1.5
            elif terrain_type == "Suavemente Ondulado":
                propagation_factor = 1.2
            elif terrain_type == "Ondulado":
                propagation_factor = 0.8
            else:  # Montanhoso
                propagation_factor = 0.5
            
            # Estimar alcance
            base_range_km = height_m * 0.1  # Base: 1km por 10m de altura
            estimated_range_km = base_range_km * propagation_factor
            
            # Zonas de impacto
            impact_zones = []
            
            # Zona de impacto direto (altura máxima)
            impact_zones.append({
                "zone": "impacto_direto",
                "distance_km": 0,
                "tsunami_height_m": height_m,
                "description": "Zona de impacto direto com altura máxima do tsunami"
            })
            
            # Zona de impacto severo (50% da altura)
            impact_zones.append({
                "zone": "impacto_severo",
                "distance_km": estimated_range_km * 0.3,
                "tsunami_height_m": height_m * 0.5,
                "description": "Zona de impacto severo com altura reduzida"
            })
            
            # Zona de impacto moderado (25% da altura)
            impact_zones.append({
                "zone": "impacto_moderado",
                "distance_km": estimated_range_km * 0.6,
                "tsunami_height_m": height_m * 0.25,
                "description": "Zona de impacto moderado"
            })
            
            # Zona de impacto leve (10% da altura)
            impact_zones.append({
                "zone": "impacto_leve",
                "distance_km": estimated_range_km,
                "tsunami_height_m": height_m * 0.1,
                "description": "Zona de impacto leve"
            })
            
            return {
                "estimated_max_range_km": estimated_range_km,
                "terrain_factor": propagation_factor,
                "impact_zones": impact_zones,
                "coastal_vulnerability": "Alta" if mean_elevation < 10 else "Moderada" if mean_elevation < 50 else "Baixa"
            }
            
        except Exception as e:
            return {"error": f"Erro na simulação de tsunami: {str(e)}"}

# Instância global do serviço
usgs_service = USGSService()
