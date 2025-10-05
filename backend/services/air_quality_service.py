"""
Serviço para integração com APIs de monitoramento de qualidade do ar (AirNow, OpenAQ).
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class AirQualityService:
    def __init__(self, airnow_api_key: str = None, openaq_api_key: str = None):
        self.airnow_api_key = airnow_api_key
        self.openaq_api_key = openaq_api_key
        self.airnow_base_url = "https://www.airnowapi.org/aq"
        self.openaq_base_url = "https://api.openaq.org/v2"
        
    def get_airnow_data(self, lat: float, lon: float, date: str = None) -> Dict:
        """
        Obtém dados de qualidade do ar do AirNow.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
        
        Returns:
            Dados de qualidade do ar do AirNow
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # URL para dados de observação do AirNow
            url = f"{self.airnow_base_url}/observation/latLong"
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "date": date,
                "distance": 25,  # Raio de busca em milhas
                "format": "application/json",
                "API_KEY": self.airnow_api_key or "DEMO_KEY"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                # Processar dados do AirNow
                processed_data = self._process_airnow_data(data, lat, lon)
                return {
                    "success": True,
                    "source": "AirNow",
                    "coordinates": [lon, lat],
                    "date": date,
                    "data": processed_data
                }
            else:
                # Simular dados se não houver dados reais
                simulated_data = self._simulate_airnow_data(lat, lon, date)
                return {
                    "success": True,
                    "source": "AirNow (Simulado)",
                    "coordinates": [lon, lat],
                    "date": date,
                    "data": simulated_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados AirNow: {str(e)}"
            }
    
    def _process_airnow_data(self, data: List[Dict], lat: float, lon: float) -> Dict:
        """Processa dados do AirNow."""
        try:
            # Encontrar a estação mais próxima
            closest_station = None
            min_distance = float('inf')
            
            for station in data:
                station_lat = station.get("Latitude", 0)
                station_lon = station.get("Longitude", 0)
                
                # Calcular distância simples
                distance = ((lat - station_lat)**2 + (lon - station_lon)**2)**0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_station = station
            
            if closest_station:
                # Processar dados da estação mais próxima
                aqi = closest_station.get("AQI", 0)
                category = closest_station.get("Category", {})
                pollutant = closest_station.get("ParameterName", "Unknown")
                
                return {
                    "station_name": closest_station.get("SiteName", "Unknown"),
                    "distance_km": min_distance * 111,  # Aproximação para km
                    "aqi": aqi,
                    "category_name": category.get("Name", "Unknown"),
                    "category_number": category.get("Number", 0),
                    "dominant_pollutant": pollutant,
                    "measurement_time": closest_station.get("DateObserved", ""),
                    "measurement_hour": closest_station.get("HourObserved", 0)
                }
            else:
                return {"error": "Nenhuma estação próxima encontrada"}
                
        except Exception as e:
            return {"error": f"Erro no processamento de dados AirNow: {str(e)}"}
    
    def _simulate_airnow_data(self, lat: float, lon: float, date: str) -> Dict:
        """Simula dados do AirNow quando dados reais não estão disponíveis."""
        try:
            import numpy as np
            
            # Simular AQI baseado em padrões geográficos e sazonais
            month = int(date[5:7])
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
            
            # Fator urbano (cidades tendem a ter pior qualidade do ar)
            if abs(lat) < 30 and abs(lon) < 30:  # Aproximação para áreas urbanas
                urban_factor = 1.5
            else:
                urban_factor = 1.0
            
            base_aqi = 50 + 30 * np.random.exponential(0.5) * seasonal_factor * urban_factor
            aqi = min(500, max(0, base_aqi))
            
            # Classificar AQI
            if aqi <= 50:
                category_name = "Good"
                category_number = 1
            elif aqi <= 100:
                category_name = "Moderate"
                category_number = 2
            elif aqi <= 150:
                category_name = "Unhealthy for Sensitive Groups"
                category_number = 3
            elif aqi <= 200:
                category_name = "Unhealthy"
                category_number = 4
            elif aqi <= 300:
                category_name = "Very Unhealthy"
                category_number = 5
            else:
                category_name = "Hazardous"
                category_number = 6
            
            # Poluente dominante simulado
            pollutants = ["PM2.5", "PM10", "OZONE", "NO2", "CO"]
            dominant_pollutant = np.random.choice(pollutants)
            
            return {
                "station_name": f"Simulated Station {int(lat*1000)}_{int(lon*1000)}",
                "distance_km": 5.0,
                "aqi": int(aqi),
                "category_name": category_name,
                "category_number": category_number,
                "dominant_pollutant": dominant_pollutant,
                "measurement_time": date,
                "measurement_hour": 12,
                "simulated": True
            }
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados AirNow: {str(e)}"}
    
    def get_openaq_data(self, lat: float, lon: float, radius_km: float = 50) -> Dict:
        """
        Obtém dados de qualidade do ar do OpenAQ.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Raio de busca em km
        
        Returns:
            Dados de qualidade do ar do OpenAQ
        """
        try:
            # URL para dados do OpenAQ
            url = f"{self.openaq_base_url}/measurements"
            
            params = {
                "coordinates": f"{lat},{lon}",
                "radius": radius_km * 1000,  # OpenAQ usa metros
                "limit": 100,
                "sort": "desc",
                "order_by": "datetime"
            }
            
            if self.openaq_api_key:
                params["api_key"] = self.openaq_api_key
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("results"):
                # Processar dados do OpenAQ
                processed_data = self._process_openaq_data(data["results"], lat, lon)
                return {
                    "success": True,
                    "source": "OpenAQ",
                    "coordinates": [lon, lat],
                    "radius_km": radius_km,
                    "data": processed_data
                }
            else:
                # Simular dados se não houver dados reais
                simulated_data = self._simulate_openaq_data(lat, lon)
                return {
                    "success": True,
                    "source": "OpenAQ (Simulado)",
                    "coordinates": [lon, lat],
                    "radius_km": radius_km,
                    "data": simulated_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados OpenAQ: {str(e)}"
            }
    
    def _process_openaq_data(self, results: List[Dict], lat: float, lon: float) -> Dict:
        """Processa dados do OpenAQ."""
        try:
            # Agrupar por localização
            locations = {}
            
            for measurement in results:
                location_name = measurement.get("location", "Unknown")
                
                if location_name not in locations:
                    locations[location_name] = {
                        "location": location_name,
                        "coordinates": [
                            measurement.get("coordinates", {}).get("longitude", 0),
                            measurement.get("coordinates", {}).get("latitude", 0)
                        ],
                        "measurements": []
                    }
                
                locations[location_name]["measurements"].append({
                    "parameter": measurement.get("parameter", "Unknown"),
                    "value": measurement.get("value", 0),
                    "unit": measurement.get("unit", ""),
                    "date": measurement.get("date", {}).get("utc", ""),
                    "country": measurement.get("country", ""),
                    "city": measurement.get("city", "")
                })
            
            # Encontrar localização mais próxima
            closest_location = None
            min_distance = float('inf')
            
            for location_name, location_data in locations.items():
                loc_lat = location_data["coordinates"][1]
                loc_lon = location_data["coordinates"][0]
                
                distance = ((lat - loc_lat)**2 + (lon - loc_lon)**2)**0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_location = location_data
            
            if closest_location:
                # Calcular estatísticas para a localização mais próxima
                measurements = closest_location["measurements"]
                
                # Agrupar por parâmetro
                parameters = {}
                for measurement in measurements:
                    param = measurement["parameter"]
                    if param not in parameters:
                        parameters[param] = []
                    parameters[param].append(measurement["value"])
                
                # Calcular médias
                parameter_stats = {}
                for param, values in parameters.items():
                    if values:
                        parameter_stats[param] = {
                            "mean": sum(values) / len(values),
                            "max": max(values),
                            "min": min(values),
                            "count": len(values),
                            "unit": measurements[0]["unit"] if measurements else ""
                        }
                
                return {
                    "closest_location": closest_location["location"],
                    "distance_km": min_distance * 111,
                    "coordinates": closest_location["coordinates"],
                    "parameter_statistics": parameter_stats,
                    "total_measurements": len(measurements),
                    "measurement_period": {
                        "latest": max([m["date"] for m in measurements]) if measurements else "",
                        "earliest": min([m["date"] for m in measurements]) if measurements else ""
                    }
                }
            else:
                return {"error": "Nenhuma localização próxima encontrada"}
                
        except Exception as e:
            return {"error": f"Erro no processamento de dados OpenAQ: {str(e)}"}
    
    def _simulate_openaq_data(self, lat: float, lon: float) -> Dict:
        """Simula dados do OpenAQ quando dados reais não estão disponíveis."""
        try:
            import numpy as np
            
            # Simular parâmetros de qualidade do ar
            parameters = {
                "pm25": {
                    "mean": 15 + 5 * np.random.normal(0, 1),
                    "max": 25 + 10 * np.random.normal(0, 1),
                    "min": 5 + 3 * np.random.normal(0, 1),
                    "count": 24,
                    "unit": "µg/m³"
                },
                "pm10": {
                    "mean": 25 + 8 * np.random.normal(0, 1),
                    "max": 40 + 15 * np.random.normal(0, 1),
                    "min": 10 + 5 * np.random.normal(0, 1),
                    "count": 24,
                    "unit": "µg/m³"
                },
                "no2": {
                    "mean": 20 + 5 * np.random.normal(0, 1),
                    "max": 35 + 10 * np.random.normal(0, 1),
                    "min": 8 + 3 * np.random.normal(0, 1),
                    "count": 24,
                    "unit": "µg/m³"
                },
                "o3": {
                    "mean": 80 + 20 * np.random.normal(0, 1),
                    "max": 120 + 30 * np.random.normal(0, 1),
                    "min": 40 + 10 * np.random.normal(0, 1),
                    "count": 24,
                    "unit": "µg/m³"
                }
            }
            
            return {
                "closest_location": f"Simulated Location {int(lat*1000)}_{int(lon*1000)}",
                "distance_km": 10.0,
                "coordinates": [lon, lat],
                "parameter_statistics": parameters,
                "total_measurements": 96,
                "measurement_period": {
                    "latest": datetime.now().isoformat(),
                    "earliest": (datetime.now() - timedelta(days=1)).isoformat()
                },
                "simulated": True
            }
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados OpenAQ: {str(e)}"}
    
    def validate_air_quality_data(self, lat: float, lon: float, date: str = None) -> Dict:
        """
        Valida dados de qualidade do ar comparando múltiplas fontes.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
        
        Returns:
            Validação cruzada de dados de qualidade do ar
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Obter dados de múltiplas fontes
            airnow_data = self.get_airnow_data(lat, lon, date)
            openaq_data = self.get_openaq_data(lat, lon)
            
            # Obter dados do TEMPO (simulados)
            from services.atmospheric_service import atmospheric_service
            tempo_data = atmospheric_service.get_tempo_air_quality(lat, lon, date)
            
            # Validar e comparar dados
            validation_result = self._validate_and_compare_data(
                airnow_data, openaq_data, tempo_data
            )
            
            return {
                "success": True,
                "coordinates": [lon, lat],
                "date": date,
                "validation_result": validation_result,
                "data_sources": {
                    "airnow": airnow_data,
                    "openaq": openaq_data,
                    "tempo": tempo_data
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na validação de dados: {str(e)}"
            }
    
    def _validate_and_compare_data(self, airnow_data: Dict, openaq_data: Dict, tempo_data: Dict) -> Dict:
        """Valida e compara dados de múltiplas fontes."""
        try:
            validation_result = {
                "consistency_score": 0.0,
                "reliability": "Unknown",
                "recommendations": [],
                "data_quality": {}
            }
            
            scores = []
            
            # Validar dados do AirNow
            if airnow_data.get("success"):
                aqi_airnow = airnow_data.get("data", {}).get("aqi", 0)
                scores.append(aqi_airnow)
                validation_result["data_quality"]["airnow"] = "Available"
            else:
                validation_result["data_quality"]["airnow"] = "Unavailable"
            
            # Validar dados do OpenAQ
            if openaq_data.get("success"):
                pm25_openaq = openaq_data.get("data", {}).get("parameter_statistics", {}).get("pm25", {}).get("mean", 0)
                scores.append(pm25_openaq)
                validation_result["data_quality"]["openaq"] = "Available"
            else:
                validation_result["data_quality"]["openaq"] = "Unavailable"
            
            # Validar dados do TEMPO
            if tempo_data.get("success"):
                aqi_tempo = tempo_data.get("air_quality_data", {}).get("aqi", {}).get("value", 0)
                scores.append(aqi_tempo)
                validation_result["data_quality"]["tempo"] = "Available"
            else:
                validation_result["data_quality"]["tempo"] = "Unavailable"
            
            # Calcular consistência
            if len(scores) >= 2:
                # Normalizar scores para comparação
                normalized_scores = []
                for score in scores:
                    if score > 0:
                        # Converter para escala 0-100 para comparação
                        if score > 500:  # AQI
                            normalized_scores.append(score)
                        else:  # PM2.5 em µg/m³
                            normalized_scores.append(score * 4)  # Aproximação
                
                if normalized_scores:
                    mean_score = sum(normalized_scores) / len(normalized_scores)
                    variance = sum((score - mean_score)**2 for score in normalized_scores) / len(normalized_scores)
                    consistency = max(0, 1 - (variance / mean_score)) if mean_score > 0 else 0
                    
                    validation_result["consistency_score"] = consistency
                    
                    if consistency > 0.8:
                        validation_result["reliability"] = "High"
                        validation_result["recommendations"].append("Dados consistentes entre fontes")
                    elif consistency > 0.6:
                        validation_result["reliability"] = "Medium"
                        validation_result["recommendations"].append("Dados moderadamente consistentes")
                    else:
                        validation_result["reliability"] = "Low"
                        validation_result["recommendations"].append("Dados inconsistentes - verificar fontes")
            
            # Recomendações baseadas na qualidade dos dados
            available_sources = sum(1 for quality in validation_result["data_quality"].values() if quality == "Available")
            
            if available_sources >= 3:
                validation_result["recommendations"].append("Múltiplas fontes disponíveis - alta confiabilidade")
            elif available_sources >= 2:
                validation_result["recommendations"].append("Fontes limitadas - confiabilidade moderada")
            else:
                validation_result["recommendations"].append("Fontes limitadas - baixa confiabilidade")
            
            return validation_result
            
        except Exception as e:
            return {"error": f"Erro na validação: {str(e)}"}

# Instância global do serviço
air_quality_service = AirQualityService()
