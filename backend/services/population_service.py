"""
Serviço para dados de população e demografia.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

class PopulationService:
    def __init__(self):
        # URLs de APIs de população (simuladas para demonstração)
        self.worldbank_api = "https://api.worldbank.org/v2/country"
        self.un_population_api = "https://population.un.org/wpp/Download/Files/1_Indicators"
        self.census_api = "https://api.census.gov/data"  # Para dados dos EUA
        
        # Dados simulados de população por região
        self.simulated_population_data = {
            "north_america": {
                "total_population": 579000000,
                "density_per_km2": 22.9,
                "age_distribution": {
                    "0-14": 18.4,
                    "15-64": 65.2,
                    "65+": 16.4
                },
                "major_cities": [
                    {"name": "New York", "population": 8336817, "lat": 40.7128, "lon": -74.0060},
                    {"name": "Los Angeles", "population": 3979576, "lat": 34.0522, "lon": -118.2437},
                    {"name": "Chicago", "population": 2693976, "lat": 41.8781, "lon": -87.6298},
                    {"name": "Houston", "population": 2320268, "lat": 29.7604, "lon": -95.3698},
                    {"name": "Phoenix", "population": 1680992, "lat": 33.4484, "lon": -112.0740}
                ]
            },
            "europe": {
                "total_population": 747000000,
                "density_per_km2": 34.0,
                "age_distribution": {
                    "0-14": 15.2,
                    "15-64": 64.1,
                    "65+": 20.7
                },
                "major_cities": [
                    {"name": "London", "population": 8982000, "lat": 51.5074, "lon": -0.1278},
                    {"name": "Berlin", "population": 3677472, "lat": 52.5200, "lon": 13.4050},
                    {"name": "Madrid", "population": 3223334, "lat": 40.4168, "lon": -3.7038},
                    {"name": "Rome", "population": 2873000, "lat": 41.9028, "lon": 12.4964},
                    {"name": "Paris", "population": 2161000, "lat": 48.8566, "lon": 2.3522}
                ]
            },
            "asia": {
                "total_population": 4600000000,
                "density_per_km2": 150.0,
                "age_distribution": {
                    "0-14": 23.1,
                    "15-64": 68.4,
                    "65+": 8.5
                },
                "major_cities": [
                    {"name": "Tokyo", "population": 37400068, "lat": 35.6762, "lon": 139.6503},
                    {"name": "Delhi", "population": 32941000, "lat": 28.7041, "lon": 77.1025},
                    {"name": "Shanghai", "population": 26317104, "lat": 31.2304, "lon": 121.4737},
                    {"name": "Mumbai", "population": 20667656, "lat": 19.0760, "lon": 72.8777},
                    {"name": "Beijing", "population": 19612368, "lat": 39.9042, "lon": 116.4074}
                ]
            }
        }
    
    def get_population_by_region(self, lat: float, lon: float, radius_km: float = 50) -> Dict:
        """
        Obtém dados de população para uma região específica.
        
        Args:
            lat: Latitude do centro
            lon: Longitude do centro
            radius_km: Raio da região em km
        
        Returns:
            Dados demográficos da região
        """
        try:
            # Determinar região baseada nas coordenadas
            region = self._determine_region(lat, lon)
            
            # Calcular população na área afetada
            area_km2 = 3.14159 * (radius_km ** 2)
            population_density = self.simulated_population_data[region]["density_per_km2"]
            estimated_population = int(area_km2 * population_density)
            
            # Buscar cidades próximas
            nearby_cities = self._find_nearby_cities(lat, lon, radius_km, region)
            
            # Calcular distribuição etária
            age_distribution = self._calculate_age_distribution(estimated_population, region)
            
            return {
                "success": True,
                "region": region,
                "coordinates": {"lat": lat, "lon": lon},
                "radius_km": radius_km,
                "area_km2": round(area_km2, 2),
                "demographics": {
                    "total_population": estimated_population,
                    "population_density_per_km2": population_density,
                    "age_distribution": age_distribution,
                    "population_at_risk": {
                        "children_0_14": age_distribution["0-14"]["count"],
                        "adults_15_64": age_distribution["15-64"]["count"],
                        "seniors_65_plus": age_distribution["65+"]["count"]
                    }
                },
                "nearby_cities": nearby_cities,
                "vulnerability_assessment": self._assess_vulnerability(age_distribution, region),
                "data_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter dados de população: {str(e)}"
            }
    
    def _determine_region(self, lat: float, lon: float) -> str:
        """Determina a região baseada nas coordenadas."""
        if 25 <= lat <= 70 and -170 <= lon <= -50:
            return "north_america"
        elif 35 <= lat <= 70 and -25 <= lon <= 40:
            return "europe"
        elif -10 <= lat <= 55 and 60 <= lon <= 180:
            return "asia"
        else:
            return "north_america"  # Default
    
    def _find_nearby_cities(self, lat: float, lon: float, radius_km: float, region: str) -> List[Dict]:
        """Encontra cidades próximas à coordenada."""
        try:
            import math
            
            nearby_cities = []
            cities = self.simulated_population_data[region]["major_cities"]
            
            for city in cities:
                # Calcular distância usando fórmula de Haversine
                distance = self._calculate_distance(lat, lon, city["lat"], city["lon"])
                
                if distance <= radius_km:
                    nearby_cities.append({
                        "name": city["name"],
                        "population": city["population"],
                        "distance_km": round(distance, 2),
                        "coordinates": {"lat": city["lat"], "lon": city["lon"]},
                        "impact_level": self._calculate_city_impact_level(distance, radius_km)
                    })
            
            # Ordenar por distância
            nearby_cities.sort(key=lambda x: x["distance_km"])
            return nearby_cities[:5]  # Top 5 cidades mais próximas
            
        except Exception as e:
            return [{"error": f"Erro ao buscar cidades: {str(e)}"}]
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distância entre duas coordenadas em km."""
        import math
        
        R = 6371  # Raio da Terra em km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def _calculate_age_distribution(self, total_population: int, region: str) -> Dict:
        """Calcula distribuição etária da população."""
        age_percentages = self.simulated_population_data[region]["age_distribution"]
        
        return {
            "0-14": {
                "percentage": age_percentages["0-14"],
                "count": int(total_population * age_percentages["0-14"] / 100),
                "vulnerability": "Alta"
            },
            "15-64": {
                "percentage": age_percentages["15-64"],
                "count": int(total_population * age_percentages["15-64"] / 100),
                "vulnerability": "Média"
            },
            "65+": {
                "percentage": age_percentages["65+"],
                "count": int(total_population * age_percentages["65+"] / 100),
                "vulnerability": "Alta"
            }
        }
    
    def _assess_vulnerability(self, age_distribution: Dict, region: str) -> Dict:
        """Avalia vulnerabilidade da população."""
        total_high_risk = age_distribution["0-14"]["count"] + age_distribution["65+"]["count"]
        total_population = sum([age_distribution[age]["count"] for age in age_distribution])
        
        high_risk_percentage = (total_high_risk / total_population) * 100 if total_population > 0 else 0
        
        if high_risk_percentage > 40:
            vulnerability_level = "Muito Alta"
        elif high_risk_percentage > 30:
            vulnerability_level = "Alta"
        elif high_risk_percentage > 20:
            vulnerability_level = "Moderada"
        else:
            vulnerability_level = "Baixa"
        
        return {
            "overall_vulnerability": vulnerability_level,
            "high_risk_population": total_high_risk,
            "high_risk_percentage": round(high_risk_percentage, 1),
            "evacuation_priority": "Crítica" if vulnerability_level in ["Muito Alta", "Alta"] else "Alta" if vulnerability_level == "Moderada" else "Normal",
            "special_needs": {
                "children_evacuation": age_distribution["0-14"]["count"],
                "elderly_evacuation": age_distribution["65+"]["count"],
                "medical_assistance_needed": age_distribution["65+"]["count"]
            }
        }
    
    def _calculate_city_impact_level(self, distance: float, radius_km: float) -> str:
        """Calcula nível de impacto para uma cidade."""
        if distance <= radius_km * 0.3:
            return "Crítico"
        elif distance <= radius_km * 0.6:
            return "Alto"
        elif distance <= radius_km:
            return "Moderado"
        else:
            return "Baixo"
    
    def get_population_density_map(self, bbox: Tuple[float, float, float, float], resolution: int = 10) -> Dict:
        """
        Gera mapa de densidade populacional para uma área.
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            resolution: Resolução da grade (pontos por lado)
        
        Returns:
            Mapa de densidade populacional
        """
        try:
            min_lon, min_lat, max_lon, max_lat = bbox
            
            # Calcular passo da grade
            lon_step = (max_lon - min_lon) / resolution
            lat_step = (max_lat - min_lat) / resolution
            
            density_grid = []
            
            for i in range(resolution):
                row = []
                for j in range(resolution):
                    lat = min_lat + (i * lat_step)
                    lon = min_lon + (j * lon_step)
                    
                    region = self._determine_region(lat, lon)
                    density = self.simulated_population_data[region]["density_per_km2"]
                    
                    # Adicionar variação local
                    import random
                    variation = random.uniform(0.8, 1.2)
                    local_density = density * variation
                    
                    row.append({
                        "coordinates": {"lat": lat, "lon": lon},
                        "population_density": round(local_density, 1),
                        "region": region
                    })
                density_grid.append(row)
            
            return {
                "success": True,
                "bbox": bbox,
                "resolution": resolution,
                "density_grid": density_grid,
                "statistics": {
                    "min_density": min([min([cell["population_density"] for cell in row]) for row in density_grid]),
                    "max_density": max([max([cell["population_density"] for cell in row]) for row in density_grid]),
                    "avg_density": sum([sum([cell["population_density"] for cell in row]) for row in density_grid]) / (resolution * resolution)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao gerar mapa de densidade: {str(e)}"
            }
    
    def get_evacuation_capacity_analysis(self, lat: float, lon: float, radius_km: float = 50) -> Dict:
        """
        Analisa capacidade de evacuação baseada na população local.
        
        Args:
            lat: Latitude do centro
            lon: Longitude do centro
            radius_km: Raio da área
        
        Returns:
            Análise de capacidade de evacuação
        """
        try:
            # Obter dados populacionais
            pop_data = self.get_population_by_region(lat, lon, radius_km)
            
            if not pop_data.get("success"):
                return pop_data
            
            total_population = pop_data["demographics"]["total_population"]
            
            # Estimar capacidade de evacuação (simulado)
            evacuation_capacity = self._estimate_evacuation_capacity(total_population, radius_km)
            
            return {
                "success": True,
                "population_data": pop_data,
                "evacuation_capacity": evacuation_capacity,
                "recommendations": self._generate_evacuation_recommendations(total_population, evacuation_capacity),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise de capacidade: {str(e)}"
            }
    
    def _estimate_evacuation_capacity(self, total_population: int, radius_km: float) -> Dict:
        """Estima capacidade de evacuação."""
        # Capacidades simuladas baseadas em infraestrutura típica
        vehicles_per_1000 = 800  # Veículos por 1000 habitantes
        buses_per_1000 = 2       # Ônibus por 1000 habitantes
        trains_per_1000 = 0.5    # Trens por 1000 habitantes
        
        available_vehicles = int(total_population * vehicles_per_1000 / 1000)
        available_buses = int(total_population * buses_per_1000 / 1000)
        available_trains = int(total_population * trains_per_1000 / 1000)
        
        # Capacidade por veículo
        car_capacity = 4
        bus_capacity = 50
        train_capacity = 500
        
        total_vehicle_capacity = (available_vehicles * car_capacity + 
                                available_buses * bus_capacity + 
                                available_trains * train_capacity)
        
        evacuation_time_hours = self._estimate_evacuation_time(radius_km, total_population)
        
        return {
            "available_vehicles": {
                "cars": available_vehicles,
                "buses": available_buses,
                "trains": available_trains
            },
            "total_capacity": total_vehicle_capacity,
            "population_to_evacuate": total_population,
            "capacity_ratio": total_vehicle_capacity / total_population if total_population > 0 else 0,
            "estimated_evacuation_time_hours": evacuation_time_hours,
            "evacuation_feasibility": "Viável" if total_vehicle_capacity >= total_population else "Limitada"
        }
    
    def _estimate_evacuation_time(self, radius_km: float, population: int) -> float:
        """Estima tempo de evacuação."""
        # Fórmula simplificada baseada em densidade e distância
        density_factor = min(population / (3.14159 * radius_km**2), 1000) / 1000
        distance_factor = radius_km / 50
        
        base_time = 2  # 2 horas base
        time_factor = 1 + (density_factor * 2) + (distance_factor * 1.5)
        
        return round(base_time * time_factor, 1)
    
    def _generate_evacuation_recommendations(self, total_population: int, capacity: Dict) -> List[str]:
        """Gera recomendações de evacuação."""
        recommendations = []
        
        if capacity["capacity_ratio"] < 0.5:
            recommendations.extend([
                "Capacidade de transporte insuficiente",
                "Solicitar apoio de veículos de outras regiões",
                "Priorizar evacuação de grupos vulneráveis",
                "Considerar evacuação por etapas"
            ])
        elif capacity["capacity_ratio"] < 1.0:
            recommendations.extend([
                "Capacidade de transporte limitada",
                "Otimizar uso de veículos disponíveis",
                "Coordenação eficiente necessária"
            ])
        else:
            recommendations.extend([
                "Capacidade de transporte adequada",
                "Evacuação completa possível",
                "Manter coordenação para eficiência"
            ])
        
        if capacity["estimated_evacuation_time_hours"] > 12:
            recommendations.append("Tempo de evacuação longo - iniciar o mais cedo possível")
        
        return recommendations

# Instância global do serviço
population_service = PopulationService()
