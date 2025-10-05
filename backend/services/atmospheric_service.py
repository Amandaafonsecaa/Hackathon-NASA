"""
Serviço para integração com APIs atmosféricas (MERRA-2, GPM IMERG, TEMPO).
"""

import requests
import xarray as xr
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import io

class AtmosphericService:
    def __init__(self):
        self.merra2_base_url = "https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2"
        self.gpm_base_url = "https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3"
        self.tempo_base_url = "https://goldsmr5.gesdisc.eosdis.nasa.gov/data/TEMPO"
        
    def get_merra2_data(self, lat: float, lon: float, date: str = None, variables: List[str] = None) -> Dict:
        """
        Obtém dados do MERRA-2 para uma localização específica.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
            variables: Lista de variáveis a obter
        
        Returns:
            Dados atmosféricos do MERRA-2
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            if variables is None:
                variables = ["U2M", "V2M", "T2M", "SLP"]  # Vento U, Vento V, Temperatura, Pressão
            
            # Construir URL para dados do MERRA-2
            year = date[:4]
            month = date[5:7]
            day = date[8:10]
            
            # URL de exemplo (precisa ser adaptado para dados reais)
            merra2_url = f"{self.merra2_base_url}/M2I1NXASM.5.12.4/{year}/{month:02d}/MERRA2_400.inst1_2d_asm_Nx.{year}{month:02d}{day:02d}.nc4"
            
            # Simular dados atmosféricos (em produção, usar dados reais)
            atmospheric_data = self._simulate_merra2_data(lat, lon, date, variables)
            
            return {
                "success": True,
                "date": date,
                "coordinates": [lon, lat],
                "variables": variables,
                "data": atmospheric_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados MERRA-2: {str(e)}"
            }
    
    def _simulate_merra2_data(self, lat: float, lon: float, date: str, variables: List[str]) -> Dict:
        """Simula dados do MERRA-2 baseados em padrões climáticos."""
        try:
            # Simular dados atmosféricos baseados na localização e data
            # Em produção, estes seriam dados reais do MERRA-2
            
            # Fatores sazonais e geográficos
            month = int(date[5:7])
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
            lat_factor = 1 - abs(lat) / 90  # Fator de latitude
            
            atmospheric_data = {}
            
            for var in variables:
                if var == "U2M":  # Componente U do vento (leste-oeste)
                    # Simular vento baseado em padrões sazonais
                    base_wind = 5 + 3 * np.sin(2 * np.pi * month / 12)
                    u_wind = base_wind * seasonal_factor * lat_factor + np.random.normal(0, 2)
                    atmospheric_data[var] = {
                        "value": float(u_wind),
                        "unit": "m/s",
                        "description": "Componente leste-oeste do vento a 2m"
                    }
                    
                elif var == "V2M":  # Componente V do vento (norte-sul)
                    base_wind = 3 + 2 * np.cos(2 * np.pi * month / 12)
                    v_wind = base_wind * seasonal_factor * lat_factor + np.random.normal(0, 1.5)
                    atmospheric_data[var] = {
                        "value": float(v_wind),
                        "unit": "m/s",
                        "description": "Componente norte-sul do vento a 2m"
                    }
                    
                elif var == "T2M":  # Temperatura a 2m
                    # Temperatura baseada na latitude e sazonalidade
                    base_temp = 25 - abs(lat) * 0.5 + 10 * np.sin(2 * np.pi * month / 12)
                    temperature = base_temp + np.random.normal(0, 3)
                    atmospheric_data[var] = {
                        "value": float(temperature),
                        "unit": "°C",
                        "description": "Temperatura a 2m"
                    }
                    
                elif var == "SLP":  # Pressão ao nível do mar
                    # Pressão baseada na altitude e variações sazonais
                    base_pressure = 1013.25 - lat * 0.1 + 5 * np.sin(2 * np.pi * month / 12)
                    pressure = base_pressure + np.random.normal(0, 2)
                    atmospheric_data[var] = {
                        "value": float(pressure),
                        "unit": "hPa",
                        "description": "Pressão ao nível do mar"
                    }
            
            # Calcular vento total e direção
            if "U2M" in atmospheric_data and "V2M" in atmospheric_data:
                u = atmospheric_data["U2M"]["value"]
                v = atmospheric_data["V2M"]["value"]
                
                wind_speed = np.sqrt(u**2 + v**2)
                wind_direction = np.degrees(np.arctan2(v, u))
                
                # Normalizar direção do vento (0-360°)
                if wind_direction < 0:
                    wind_direction += 360
                
                atmospheric_data["WIND_SPEED"] = {
                    "value": float(wind_speed),
                    "unit": "m/s",
                    "description": "Velocidade total do vento"
                }
                
                atmospheric_data["WIND_DIRECTION"] = {
                    "value": float(wind_direction),
                    "unit": "degrees",
                    "description": "Direção do vento (0° = Norte, 90° = Leste)"
                }
            
            return atmospheric_data
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados MERRA-2: {str(e)}"}
    
    def get_gpm_precipitation(self, lat: float, lon: float, date: str = None) -> Dict:
        """
        Obtém dados de precipitação do GPM IMERG.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
        
        Returns:
            Dados de precipitação
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Simular dados de precipitação (em produção, usar dados reais do GPM)
            precipitation_data = self._simulate_gpm_data(lat, lon, date)
            
            return {
                "success": True,
                "date": date,
                "coordinates": [lon, lat],
                "precipitation_data": precipitation_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados GPM: {str(e)}"
            }
    
    def _simulate_gpm_data(self, lat: float, lon: float, date: str) -> Dict:
        """Simula dados de precipitação do GPM."""
        try:
            # Fatores geográficos e sazonais para precipitação
            month = int(date[5:7])
            
            # Padrões de precipitação baseados na localização
            if abs(lat) < 30:  # Região tropical
                seasonal_factor = 1 + 0.5 * np.sin(2 * np.pi * month / 12)
                base_precipitation = 5 + 3 * np.random.exponential(1)
            elif abs(lat) < 60:  # Região temperada
                seasonal_factor = 1 + 0.8 * np.sin(2 * np.pi * month / 12)
                base_precipitation = 3 + 2 * np.random.exponential(0.8)
            else:  # Região polar
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
                base_precipitation = 1 + 1 * np.random.exponential(0.5)
            
            # Precipitação diária simulada
            daily_precipitation = base_precipitation * seasonal_factor
            
            # Classificar intensidade
            if daily_precipitation < 1:
                intensity = "Leve"
            elif daily_precipitation < 5:
                intensity = "Moderada"
            elif daily_precipitation < 10:
                intensity = "Forte"
            else:
                intensity = "Muito Forte"
            
            # Impacto na evacuação
            evacuation_impact = self._assess_evacuation_impact(daily_precipitation)
            
            return {
                "daily_precipitation_mm": float(daily_precipitation),
                "intensity_category": intensity,
                "evacuation_impact": evacuation_impact,
                "visibility_reduction": min(50, daily_precipitation * 5),  # % de redução de visibilidade
                "road_condition": "Molhada" if daily_precipitation > 2 else "Secas"
            }
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados GPM: {str(e)}"}
    
    def _assess_evacuation_impact(self, precipitation_mm: float) -> Dict:
        """Avalia o impacto da precipitação na evacuação."""
        if precipitation_mm < 1:
            return {
                "level": "Mínimo",
                "description": "Precipitação leve, impacto mínimo na evacuação",
                "speed_reduction": 0.05,
                "visibility_impact": "Baixo"
            }
        elif precipitation_mm < 5:
            return {
                "level": "Baixo",
                "description": "Precipitação moderada, redução leve na velocidade",
                "speed_reduction": 0.15,
                "visibility_impact": "Moderado"
            }
        elif precipitation_mm < 10:
            return {
                "level": "Moderado",
                "description": "Precipitação forte, redução significativa na velocidade",
                "speed_reduction": 0.25,
                "visibility_impact": "Alto"
            }
        else:
            return {
                "level": "Alto",
                "description": "Precipitação muito forte, condições perigosas para evacuação",
                "speed_reduction": 0.4,
                "visibility_impact": "Muito Alto"
            }
    
    def get_tempo_air_quality(self, lat: float, lon: float, date: str = None) -> Dict:
        """
        Obtém dados de qualidade do ar do TEMPO.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
        
        Returns:
            Dados de qualidade do ar
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Simular dados de qualidade do ar (em produção, usar dados reais do TEMPO)
            air_quality_data = self._simulate_tempo_data(lat, lon, date)
            
            return {
                "success": True,
                "date": date,
                "coordinates": [lon, lat],
                "air_quality_data": air_quality_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados TEMPO: {str(e)}"
            }
    
    def _simulate_tempo_data(self, lat: float, lon: float, date: str) -> Dict:
        """Simula dados de qualidade do ar do TEMPO."""
        try:
            # Simular poluentes atmosféricos
            # Em produção, estes seriam dados reais do TEMPO
            
            pollutants = {
                "NO2": {
                    "value": 15 + 5 * np.random.normal(0, 1),
                    "unit": "ppb",
                    "description": "Dióxido de Nitrogênio"
                },
                "PM2_5": {
                    "value": 10 + 3 * np.random.normal(0, 1),
                    "unit": "μg/m³",
                    "description": "Material Particulado 2.5μm"
                },
                "PM10": {
                    "value": 20 + 5 * np.random.normal(0, 1),
                    "unit": "μg/m³",
                    "description": "Material Particulado 10μm"
                },
                "O3": {
                    "value": 30 + 10 * np.random.normal(0, 1),
                    "unit": "ppb",
                    "description": "Ozônio"
                }
            }
            
            # Calcular índice de qualidade do ar (AQI)
            aqi = self._calculate_aqi(pollutants)
            
            # Avaliar impacto na saúde
            health_impact = self._assess_health_impact(pollutants, aqi)
            
            return {
                "pollutants": pollutants,
                "aqi": aqi,
                "health_impact": health_impact,
                "data_source": "TEMPO (Simulado)",
                "measurement_time": date
            }
            
        except Exception as e:
            return {"error": f"Erro na simulação de dados TEMPO: {str(e)}"}
    
    def _calculate_aqi(self, pollutants: Dict) -> Dict:
        """Calcula o Índice de Qualidade do Ar (AQI)."""
        try:
            # Simplificação do cálculo do AQI
            # Em produção, usar fórmula oficial da EPA
            
            aqi_values = []
            
            # NO2 (ppb para μg/m³ aproximado)
            no2_ugm3 = pollutants["NO2"]["value"] * 1.88
            no2_aqi = min(500, max(0, (no2_ugm3 / 100) * 100))
            aqi_values.append(no2_aqi)
            
            # PM2.5
            pm25_aqi = min(500, max(0, (pollutants["PM2_5"]["value"] / 35) * 100))
            aqi_values.append(pm25_aqi)
            
            # PM10
            pm10_aqi = min(500, max(0, (pollutants["PM10"]["value"] / 50) * 100))
            aqi_values.append(pm10_aqi)
            
            # O3
            o3_aqi = min(500, max(0, (pollutants["O3"]["value"] / 70) * 100))
            aqi_values.append(o3_aqi)
            
            # AQI é o máximo entre os valores
            max_aqi = max(aqi_values)
            
            # Classificar AQI
            if max_aqi <= 50:
                category = "Bom"
                color = "Verde"
            elif max_aqi <= 100:
                category = "Moderado"
                color = "Amarelo"
            elif max_aqi <= 150:
                category = "Insalubre para Grupos Sensíveis"
                color = "Laranja"
            elif max_aqi <= 200:
                category = "Insalubre"
                color = "Vermelho"
            elif max_aqi <= 300:
                category = "Muito Insalubre"
                color = "Roxo"
            else:
                category = "Perigoso"
                color = "Marrom"
            
            return {
                "value": float(max_aqi),
                "category": category,
                "color": color,
                "dominant_pollutant": "NO2" if no2_aqi == max_aqi else 
                                    "PM2.5" if pm25_aqi == max_aqi else
                                    "PM10" if pm10_aqi == max_aqi else "O3"
            }
            
        except Exception as e:
            return {"error": f"Erro no cálculo do AQI: {str(e)}"}
    
    def _assess_health_impact(self, pollutants: Dict, aqi: Dict) -> Dict:
        """Avalia o impacto na saúde baseado na qualidade do ar."""
        try:
            aqi_value = aqi.get("value", 0)
            
            if aqi_value <= 50:
                return {
                    "level": "Baixo",
                    "recommendations": [
                        "Ar de boa qualidade",
                        "Atividades ao ar livre são seguras"
                    ],
                    "sensitive_groups": "Nenhuma precaução especial"
                }
            elif aqi_value <= 100:
                return {
                    "level": "Moderado",
                    "recommendations": [
                        "Ar aceitável para a maioria das pessoas",
                        "Grupos sensíveis podem ter problemas respiratórios leves"
                    ],
                    "sensitive_groups": "Pessoas com problemas respiratórios devem evitar atividades intensas"
                }
            elif aqi_value <= 150:
                return {
                    "level": "Alto",
                    "recommendations": [
                        "Grupos sensíveis devem evitar atividades ao ar livre",
                        "Pessoas com problemas cardíacos ou pulmonares devem reduzir atividades"
                    ],
                    "sensitive_groups": "Crianças, idosos e pessoas com problemas respiratórios devem ficar em ambientes fechados"
                }
            else:
                return {
                    "level": "Crítico",
                    "recommendations": [
                        "Todos devem evitar atividades ao ar livre",
                        "Usar máscaras se necessário sair",
                        "Manter janelas fechadas"
                    ],
                    "sensitive_groups": "Evacuação recomendada para grupos sensíveis"
                }
                
        except Exception as e:
            return {"error": f"Erro na avaliação de impacto na saúde: {str(e)}"}
    
    def get_atmospheric_dispersion_conditions(self, lat: float, lon: float, date: str = None) -> Dict:
        """
        Obtém condições atmosféricas para modelagem de dispersão.
        
        Args:
            lat: Latitude
            lon: Longitude
            date: Data no formato YYYY-MM-DD (padrão: hoje)
        
        Returns:
            Condições para modelagem de dispersão
        """
        try:
            # Obter dados atmosféricos
            merra2_data = self.get_merra2_data(lat, lon, date)
            
            if not merra2_data["success"]:
                return {
                    "success": False,
                    "error": "Falha ao obter dados atmosféricos"
                }
            
            # Analisar condições de dispersão
            dispersion_analysis = self._analyze_dispersion_conditions(merra2_data["data"])
            
            return {
                "success": True,
                "coordinates": [lon, lat],
                "date": date,
                "atmospheric_conditions": merra2_data["data"],
                "dispersion_analysis": dispersion_analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise de dispersão: {str(e)}"
            }
    
    def _analyze_dispersion_conditions(self, atmospheric_data: Dict) -> Dict:
        """Analisa condições atmosféricas para dispersão."""
        try:
            wind_speed = atmospheric_data.get("WIND_SPEED", {}).get("value", 0)
            wind_direction = atmospheric_data.get("WIND_DIRECTION", {}).get("value", 0)
            temperature = atmospheric_data.get("T2M", {}).get("value", 20)
            pressure = atmospheric_data.get("SLP", {}).get("value", 1013)
            
            # Classificar condições de dispersão
            if wind_speed < 2:
                dispersion_class = "Fraca"
                dispersion_factor = 0.3
            elif wind_speed < 5:
                dispersion_class = "Moderada"
                dispersion_factor = 0.7
            elif wind_speed < 10:
                dispersion_class = "Boa"
                dispersion_factor = 1.0
            else:
                dispersion_class = "Excelente"
                dispersion_factor = 1.5
            
            # Estabilidade atmosférica (simplificada)
            if temperature > 25 and wind_speed < 3:
                stability = "Instável"
            elif temperature < 10 and wind_speed < 5:
                stability = "Estável"
            else:
                stability = "Neutra"
            
            return {
                "dispersion_class": dispersion_class,
                "dispersion_factor": dispersion_factor,
                "atmospheric_stability": stability,
                "wind_conditions": {
                    "speed_mps": wind_speed,
                    "direction_deg": wind_direction,
                    "category": "Calmo" if wind_speed < 2 else 
                               "Leve" if wind_speed < 5 else
                               "Moderado" if wind_speed < 10 else "Forte"
                },
                "plume_behavior": {
                    "horizontal_spread": dispersion_factor,
                    "vertical_mixing": 1.0 if stability == "Instável" else 0.5,
                    "downwind_distance_km": wind_speed * 2  # Estimativa simplificada
                }
            }
            
        except Exception as e:
            return {"error": f"Erro na análise de dispersão: {str(e)}"}

# Instância global do serviço
atmospheric_service = AtmosphericService()
