"""
Serviço para integração com GIBS + Worldview para imagens de satélite.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class SatelliteImageryService:
    def __init__(self):
        self.gibs_base_url = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best"
        self.worldview_base_url = "https://worldview.earthdata.nasa.gov"
        
        # Camadas disponíveis no GIBS
        self.available_layers = {
            "clouds": {
                "layer": "MODIS_Terra_Cloud_Fraction_Day",
                "description": "Cobertura de nuvens do MODIS Terra",
                "temporal_resolution": "Daily",
                "spatial_resolution": "1km"
            },
            "fires": {
                "layer": "MODIS_Terra_Fires_All",
                "description": "Detecção de incêndios do MODIS Terra",
                "temporal_resolution": "Daily",
                "spatial_resolution": "1km"
            },
            "aerosols": {
                "layer": "MODIS_Terra_Aerosol_Optical_Depth",
                "description": "Profundidade óptica de aerossóis",
                "temporal_resolution": "Daily",
                "spatial_resolution": "10km"
            },
            "precipitation": {
                "layer": "GPM_3IMERGDF",
                "description": "Precipitação GPM IMERG",
                "temporal_resolution": "Daily",
                "spatial_resolution": "0.1°"
            },
            "temperature": {
                "layer": "AIRS_L3_Surface_Air_Temperature_Daily_Night",
                "description": "Temperatura da superfície (noite)",
                "temporal_resolution": "Daily",
                "spatial_resolution": "1°"
            },
            "vegetation": {
                "layer": "MODIS_Terra_NDVI",
                "description": "Índice de vegetação (NDVI)",
                "temporal_resolution": "16-day",
                "spatial_resolution": "250m"
            }
        }
    
    def get_satellite_imagery(self, 
                            layer_type: str,
                            bbox: Tuple[float, float, float, float],
                            date: str = None,
                            format_type: str = "png",
                            width: int = 512,
                            height: int = 512) -> Dict:
        """
        Obtém imagens de satélite via GIBS.
        
        Args:
            layer_type: Tipo de camada (clouds, fires, aerosols, etc.)
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            date: Data no formato YYYY-MM-DD (padrão: hoje)
            format_type: Formato da imagem (png, jpg)
            width: Largura da imagem
            height: Altura da imagem
        
        Returns:
            Dados da imagem de satélite
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            if layer_type not in self.available_layers:
                return {
                    "success": False,
                    "error": f"Tipo de camada '{layer_type}' não disponível"
                }
            
            layer_info = self.available_layers[layer_type]
            layer_name = layer_info["layer"]
            
            # Construir URL para requisição WMTS
            wmts_url = self._build_wmts_url(
                layer_name, bbox, date, format_type, width, height
            )
            
            # Simular dados de imagem (em produção, fazer requisição real)
            imagery_data = self._simulate_satellite_imagery(
                layer_type, bbox, date, layer_info
            )
            
            return {
                "success": True,
                "layer_type": layer_type,
                "layer_info": layer_info,
                "bbox": bbox,
                "date": date,
                "image_url": wmts_url,
                "imagery_data": imagery_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter imagens de satélite: {str(e)}"
            }
    
    def _build_wmts_url(self, 
                       layer_name: str,
                       bbox: Tuple[float, float, float, float],
                       date: str,
                       format_type: str,
                       width: int,
                       height: int) -> str:
        """Constrói URL para requisição WMTS do GIBS."""
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # URL base do WMTS
        base_url = f"{self.gibs_base_url}/{layer_name}/default/{date}/EPSG4326_1km"
        
        # Parâmetros da requisição
        params = {
            "SERVICE": "WMTS",
            "REQUEST": "GetTile",
            "VERSION": "1.0.0",
            "LAYER": layer_name,
            "STYLE": "default",
            "TILEMATRIXSET": "EPSG4326_1km",
            "TILEMATRIX": "EPSG4326_1km:0",
            "TILEROW": "0",
            "TILECOL": "0",
            "FORMAT": f"image/{format_type}"
        }
        
        # Construir URL final
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _simulate_satellite_imagery(self, 
                                  layer_type: str,
                                  bbox: Tuple[float, float, float, float],
                                  date: str,
                                  layer_info: Dict) -> Dict:
        """Simula dados de imagens de satélite."""
        try:
            import numpy as np
            
            min_lon, min_lat, max_lon, max_lat = bbox
            
            # Simular dados baseados no tipo de camada
            if layer_type == "clouds":
                # Simular cobertura de nuvens (0-100%)
                cloud_cover = 30 + 40 * np.random.random()
                imagery_data = {
                    "cloud_cover_percent": round(cloud_cover, 1),
                    "visibility_impact": "Baixo" if cloud_cover < 30 else "Moderado" if cloud_cover < 70 else "Alto",
                    "evacuation_impact": "Mínimo" if cloud_cover < 50 else "Moderado"
                }
                
            elif layer_type == "fires":
                # Simular detecção de incêndios
                fire_count = np.random.poisson(2)  # Distribuição de Poisson
                imagery_data = {
                    "active_fires": fire_count,
                    "fire_intensity": "Baixa" if fire_count < 2 else "Moderada" if fire_count < 5 else "Alta",
                    "evacuation_impact": "Nenhum" if fire_count == 0 else "Moderado" if fire_count < 3 else "Alto"
                }
                
            elif layer_type == "aerosols":
                # Simular profundidade óptica de aerossóis
                aerosol_depth = 0.1 + 0.3 * np.random.random()
                imagery_data = {
                    "aerosol_optical_depth": round(aerosol_depth, 3),
                    "air_quality_impact": "Bom" if aerosol_depth < 0.2 else "Moderado" if aerosol_depth < 0.4 else "Ruim",
                    "visibility_km": max(5, 20 - aerosol_depth * 50)
                }
                
            elif layer_type == "precipitation":
                # Simular precipitação
                precipitation_mm = 5 * np.random.exponential(1)
                imagery_data = {
                    "precipitation_mm": round(precipitation_mm, 1),
                    "intensity": "Leve" if precipitation_mm < 2 else "Moderada" if precipitation_mm < 10 else "Forte",
                    "evacuation_impact": "Baixo" if precipitation_mm < 5 else "Moderado" if precipitation_mm < 15 else "Alto"
                }
                
            elif layer_type == "temperature":
                # Simular temperatura
                temperature = 15 + 20 * np.random.random()
                imagery_data = {
                    "temperature_celsius": round(temperature, 1),
                    "thermal_stress": "Baixo" if 15 <= temperature <= 25 else "Moderado" if 10 <= temperature <= 30 else "Alto"
                }
                
            elif layer_type == "vegetation":
                # Simular índice de vegetação
                ndvi = 0.3 + 0.5 * np.random.random()
                imagery_data = {
                    "ndvi_index": round(ndvi, 3),
                    "vegetation_health": "Baixa" if ndvi < 0.4 else "Moderada" if ndvi < 0.7 else "Alta",
                    "fire_risk": "Alto" if ndvi < 0.3 else "Moderado" if ndvi < 0.6 else "Baixo"
                }
            
            else:
                imagery_data = {"data_type": "unknown", "values": "simulated"}
            
            # Adicionar metadados comuns
            imagery_data.update({
                "area_coverage_km2": self._calculate_area_km2(bbox),
                "spatial_resolution": layer_info.get("spatial_resolution", "Unknown"),
                "temporal_resolution": layer_info.get("temporal_resolution", "Unknown"),
                "data_quality": "Simulado para demonstração",
                "processing_timestamp": datetime.now().isoformat()
            })
            
            return imagery_data
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados: {str(e)}"}
    
    def _calculate_area_km2(self, bbox: Tuple[float, float, float, float]) -> float:
        """Calcula área do bounding box em km²."""
        min_lon, min_lat, max_lon, max_lat = bbox
        
        # Conversão aproximada para km
        lat_diff = (max_lat - min_lat) * 111.0  # 1 grau ≈ 111 km
        lon_diff = (max_lon - min_lon) * 111.0 * np.cos(np.radians((min_lat + max_lat) / 2))
        
        return lat_diff * lon_diff
    
    def get_multi_layer_analysis(self, 
                               bbox: Tuple[float, float, float, float],
                               layers: List[str] = None,
                               date: str = None) -> Dict:
        """
        Obtém análise de múltiplas camadas de satélite.
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            layers: Lista de camadas a analisar (padrão: todas disponíveis)
            date: Data no formato YYYY-MM-DD
        
        Returns:
            Análise combinada de múltiplas camadas
        """
        try:
            if layers is None:
                layers = list(self.available_layers.keys())
            
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Obter dados de cada camada
            layer_data = {}
            for layer in layers:
                if layer in self.available_layers:
                    layer_result = self.get_satellite_imagery(layer, bbox, date)
                    if layer_result.get("success"):
                        layer_data[layer] = layer_result["imagery_data"]
            
            # Análise combinada
            combined_analysis = self._analyze_combined_layers(layer_data, bbox)
            
            return {
                "success": True,
                "bbox": bbox,
                "date": date,
                "layers_analyzed": layers,
                "layer_data": layer_data,
                "combined_analysis": combined_analysis,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise multi-camada: {str(e)}"
            }
    
    def _analyze_combined_layers(self, layer_data: Dict, bbox: Tuple[float, float, float, float]) -> Dict:
        """Analisa dados combinados de múltiplas camadas."""
        try:
            analysis = {
                "overall_conditions": {},
                "evacuation_factors": {},
                "environmental_risks": {},
                "recommendations": []
            }
            
            # Análise de condições gerais
            if "clouds" in layer_data:
                cloud_cover = layer_data["clouds"].get("cloud_cover_percent", 0)
                analysis["overall_conditions"]["visibility"] = "Boa" if cloud_cover < 30 else "Moderada" if cloud_cover < 70 else "Ruim"
            
            if "precipitation" in layer_data:
                precipitation = layer_data["precipitation"].get("precipitation_mm", 0)
                analysis["overall_conditions"]["weather"] = "Seco" if precipitation < 2 else "Chuvoso" if precipitation < 10 else "Muito chuvoso"
            
            if "temperature" in layer_data:
                temperature = layer_data["temperature"].get("temperature_celsius", 20)
                analysis["overall_conditions"]["temperature"] = f"{temperature}°C"
            
            # Fatores de evacuação
            evacuation_score = 0
            evacuation_factors = []
            
            if "clouds" in layer_data:
                cloud_impact = layer_data["clouds"].get("evacuation_impact", "Mínimo")
                if cloud_impact == "Moderado":
                    evacuation_score += 1
                    evacuation_factors.append("Visibilidade reduzida por nuvens")
                elif cloud_impact == "Alto":
                    evacuation_score += 2
                    evacuation_factors.append("Visibilidade muito reduzida por nuvens")
            
            if "precipitation" in layer_data:
                precip_impact = layer_data["precipitation"].get("evacuation_impact", "Baixo")
                if precip_impact == "Moderado":
                    evacuation_score += 1
                    evacuation_factors.append("Condições de chuva moderada")
                elif precip_impact == "Alto":
                    evacuation_score += 2
                    evacuation_factors.append("Chuva forte - evacuação difícil")
            
            if "fires" in layer_data:
                fire_impact = layer_data["fires"].get("evacuation_impact", "Nenhum")
                if fire_impact == "Moderado":
                    evacuation_score += 1
                    evacuation_factors.append("Incêndios ativos na área")
                elif fire_impact == "Alto":
                    evacuation_score += 2
                    evacuation_factors.append("Múltiplos incêndios ativos")
            
            analysis["evacuation_factors"] = {
                "evacuation_difficulty_score": evacuation_score,
                "difficulty_level": "Baixo" if evacuation_score <= 1 else "Moderado" if evacuation_score <= 3 else "Alto",
                "factors": evacuation_factors
            }
            
            # Riscos ambientais
            environmental_risks = []
            
            if "aerosols" in layer_data:
                air_quality = layer_data["aerosols"].get("air_quality_impact", "Bom")
                if air_quality != "Bom":
                    environmental_risks.append(f"Qualidade do ar: {air_quality}")
            
            if "vegetation" in layer_data:
                fire_risk = layer_data["vegetation"].get("fire_risk", "Baixo")
                if fire_risk != "Baixo":
                    environmental_risks.append(f"Risco de incêndio: {fire_risk}")
            
            analysis["environmental_risks"] = environmental_risks
            
            # Recomendações
            recommendations = []
            
            if evacuation_score > 2:
                recommendations.extend([
                    "Condições adversas para evacuação",
                    "Considerar adiar evacuação se possível",
                    "Usar rotas alternativas com melhor visibilidade"
                ])
            
            if "precipitation" in layer_data and layer_data["precipitation"].get("precipitation_mm", 0) > 10:
                recommendations.extend([
                    "Chuva forte - evacuação muito difícil",
                    "Preparar equipamentos de proteção contra chuva",
                    "Considerar abrigos temporários"
                ])
            
            if "fires" in layer_data and layer_data["fires"].get("active_fires", 0) > 2:
                recommendations.extend([
                    "Múltiplos incêndios ativos na área",
                    "Evitar rotas próximas a incêndios",
                    "Coordenar com bombeiros locais"
                ])
            
            analysis["recommendations"] = recommendations if recommendations else ["Condições favoráveis para evacuação"]
            
            return analysis
            
        except Exception as e:
            return {"error": f"Erro na análise combinada: {str(e)}"}
    
    def get_available_layers(self) -> Dict:
        """Retorna informações sobre camadas disponíveis."""
        return {
            "success": True,
            "total_layers": len(self.available_layers),
            "layers": self.available_layers,
            "data_source": "NASA GIBS / Worldview",
            "note": "Dados simulados para demonstração. Em produção, usar dados reais do GIBS."
        }

# Instância global do serviço
satellite_imagery_service = SatelliteImageryService()
