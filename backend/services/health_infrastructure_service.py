"""
Serviço para dados de infraestrutura de saúde.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class HealthInfrastructureService:
    def __init__(self):
        # URLs de APIs de saúde (simuladas para demonstração)
        self.hhs_api = "https://healthdata.gov/api/3/action/datastore_search"
        self.who_api = "https://ghoapi.azureedge.net/api"
        self.cdc_api = "https://data.cdc.gov/api/views"
        
        # Dados simulados de infraestrutura de saúde
        self.simulated_health_data = {
            "hospitals": {
                "capacity_per_1000": 2.8,  # Leitos por 1000 habitantes
                "specialties": [
                    "Emergency Medicine", "Trauma Surgery", "Burn Treatment", 
                    "Pediatrics", "Geriatrics", "Respiratory Medicine"
                ],
                "equipment_per_hospital": {
                    "ventilators": 20,
                    "icu_beds": 15,
                    "emergency_beds": 50,
                    "surgery_rooms": 8,
                    "ambulances": 5
                }
            },
            "clinics": {
                "capacity_per_1000": 5.0,  # Consultórios por 1000 habitantes
                "types": [
                    "Primary Care", "Urgent Care", "Specialty Care", "Mental Health"
                ]
            },
            "emergency_services": {
                "response_time_minutes": 8.5,  # Tempo médio de resposta
                "ambulances_per_100k": 12.5,
                "paramedics_per_100k": 45.0
            },
            "pharmaceutical": {
                "pharmacies_per_1000": 3.2,
                "emergency_medications": [
                    "Antibiotics", "Pain Relief", "Respiratory Support", 
                    "Burn Treatment", "Trauma Care"
                ]
            }
        }
    
    def get_health_capacity_by_region(self, lat: float, lon: float, radius_km: float = 50) -> Dict:
        """
        Obtém capacidade de infraestrutura de saúde para uma região.
        
        Args:
            lat: Latitude do centro
            lon: Longitude do centro
            radius_km: Raio da região em km
        
        Returns:
            Capacidade de infraestrutura de saúde
        """
        try:
            # Estimar população da região (simulado)
            area_km2 = 3.14159 * (radius_km ** 2)
            population_density = 150  # Pessoas por km² (média global)
            estimated_population = int(area_km2 * population_density)
            
            # Calcular infraestrutura disponível
            health_infrastructure = self._calculate_health_infrastructure(estimated_population, radius_km)
            
            # Simular ocupação atual
            current_occupancy = self._simulate_current_occupancy(health_infrastructure)
            
            # Calcular capacidade para emergência
            emergency_capacity = self._calculate_emergency_capacity(health_infrastructure, current_occupancy)
            
            return {
                "success": True,
                "region_info": {
                    "coordinates": {"lat": lat, "lon": lon},
                    "radius_km": radius_km,
                    "area_km2": round(area_km2, 2),
                    "estimated_population": estimated_population
                },
                "health_infrastructure": health_infrastructure,
                "current_occupancy": current_occupancy,
                "emergency_capacity": emergency_capacity,
                "vulnerability_assessment": self._assess_health_vulnerability(emergency_capacity, estimated_population),
                "data_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter capacidade de saúde: {str(e)}"
            }
    
    def _calculate_health_infrastructure(self, population: int, radius_km: float) -> Dict:
        """Calcula infraestrutura de saúde disponível."""
        import random
        
        # Calcular número de hospitais
        hospital_capacity = self.simulated_health_data["hospitals"]["capacity_per_1000"]
        total_beds_needed = int(population * hospital_capacity / 1000)
        beds_per_hospital = 200  # Média de leitos por hospital
        num_hospitals = max(1, int(total_beds_needed / beds_per_hospital))
        
        # Calcular número de clínicas
        clinic_capacity = self.simulated_health_data["clinics"]["capacity_per_1000"]
        num_clinics = int(population * clinic_capacity / 1000)
        
        # Calcular ambulâncias
        ambulance_capacity = self.simulated_health_data["emergency_services"]["ambulances_per_100k"]
        num_ambulances = int(population * ambulance_capacity / 100000)
        
        # Calcular farmácias
        pharmacy_capacity = self.simulated_health_data["pharmaceutical"]["pharmacies_per_1000"]
        num_pharmacies = int(population * pharmacy_capacity / 1000)
        
        # Adicionar variação local
        variation_factor = random.uniform(0.8, 1.2)
        
        return {
            "hospitals": {
                "count": max(1, int(num_hospitals * variation_factor)),
                "total_beds": max(50, int(total_beds_needed * variation_factor)),
                "icu_beds": max(5, int(total_beds_needed * 0.1 * variation_factor)),
                "emergency_beds": max(10, int(total_beds_needed * 0.2 * variation_factor)),
                "ventilators": max(5, int(num_hospitals * 20 * variation_factor)),
                "surgery_rooms": max(1, int(num_hospitals * 8 * variation_factor))
            },
            "clinics": {
                "count": max(1, int(num_clinics * variation_factor)),
                "primary_care": max(1, int(num_clinics * 0.6 * variation_factor)),
                "urgent_care": max(1, int(num_clinics * 0.3 * variation_factor)),
                "specialty_care": max(1, int(num_clinics * 0.1 * variation_factor))
            },
            "emergency_services": {
                "ambulances": max(1, int(num_ambulances * variation_factor)),
                "paramedics": max(2, int(num_ambulances * 3 * variation_factor)),
                "response_time_minutes": self.simulated_health_data["emergency_services"]["response_time_minutes"]
            },
            "pharmaceutical": {
                "pharmacies": max(1, int(num_pharmacies * variation_factor)),
                "emergency_stock": "Adequado" if variation_factor > 0.9 else "Limitado"
            }
        }
    
    def _simulate_current_occupancy(self, infrastructure: Dict) -> Dict:
        """Simula ocupação atual da infraestrutura."""
        import random
        
        # Simular ocupação baseada em horário e dia da semana
        current_hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        
        # Fator de ocupação baseado no horário
        if 8 <= current_hour <= 18:
            base_occupancy = 0.7 if not is_weekend else 0.5
        elif 18 <= current_hour <= 22:
            base_occupancy = 0.9 if not is_weekend else 0.7
        else:
            base_occupancy = 0.3
        
        # Adicionar variação aleatória
        variation = random.uniform(-0.1, 0.1)
        occupancy_rate = max(0.1, min(0.95, base_occupancy + variation))
        
        return {
            "hospitals": {
                "bed_occupancy_rate": round(occupancy_rate, 2),
                "occupied_beds": int(infrastructure["hospitals"]["total_beds"] * occupancy_rate),
                "available_beds": infrastructure["hospitals"]["total_beds"] - int(infrastructure["hospitals"]["total_beds"] * occupancy_rate),
                "icu_occupancy_rate": round(min(0.95, occupancy_rate + 0.1), 2),
                "emergency_occupancy_rate": round(min(0.95, occupancy_rate + 0.05), 2)
            },
            "clinics": {
                "occupancy_rate": round(occupancy_rate * 0.8, 2),
                "available_appointments": int(infrastructure["clinics"]["count"] * 20 * (1 - occupancy_rate * 0.8))
            },
            "emergency_services": {
                "ambulances_available": max(0, infrastructure["emergency_services"]["ambulances"] - random.randint(0, 2)),
                "response_time_factor": 1.0 + (occupancy_rate * 0.3)
            }
        }
    
    def _calculate_emergency_capacity(self, infrastructure: Dict, occupancy: Dict) -> Dict:
        """Calcula capacidade para emergência."""
        # Calcular capacidade disponível para emergência
        available_hospital_beds = occupancy["hospitals"]["available_beds"]
        available_icu_beds = int(infrastructure["hospitals"]["icu_beds"] * (1 - occupancy["hospitals"]["icu_occupancy_rate"]))
        available_emergency_beds = int(infrastructure["hospitals"]["emergency_beds"] * (1 - occupancy["hospitals"]["emergency_occupancy_rate"]))
        
        # Calcular capacidade de triagem
        triage_capacity = available_emergency_beds * 3  # 3 pacientes por leito de emergência
        
        # Calcular capacidade de evacuação médica
        medical_evacuation_capacity = available_hospital_beds + available_icu_beds
        
        return {
            "immediate_care": {
                "emergency_beds_available": available_emergency_beds,
                "triage_capacity": triage_capacity,
                "ambulances_available": occupancy["emergency_services"]["ambulances_available"]
            },
            "hospitalization": {
                "regular_beds_available": available_hospital_beds,
                "icu_beds_available": available_icu_beds,
                "ventilators_available": int(infrastructure["hospitals"]["ventilators"] * 0.8)
            },
            "evacuation_medical": {
                "medical_evacuation_capacity": medical_evacuation_capacity,
                "critical_care_capacity": available_icu_beds,
                "specialized_equipment": infrastructure["hospitals"]["ventilators"]
            },
            "overall_capacity_assessment": self._assess_overall_capacity(available_hospital_beds, available_icu_beds, triage_capacity)
        }
    
    def _assess_overall_capacity(self, regular_beds: int, icu_beds: int, triage_capacity: int) -> Dict:
        """Avalia capacidade geral do sistema."""
        total_capacity = regular_beds + icu_beds + triage_capacity
        
        if total_capacity > 1000:
            capacity_level = "Excelente"
        elif total_capacity > 500:
            capacity_level = "Boa"
        elif total_capacity > 200:
            capacity_level = "Adequada"
        elif total_capacity > 50:
            capacity_level = "Limitada"
        else:
            capacity_level = "Crítica"
        
        return {
            "capacity_level": capacity_level,
            "total_emergency_capacity": total_capacity,
            "can_handle_mass_casualty": total_capacity > 100,
            "recommendations": self._generate_capacity_recommendations(capacity_level, total_capacity)
        }
    
    def _generate_capacity_recommendations(self, capacity_level: str, total_capacity: int) -> List[str]:
        """Gera recomendações baseadas na capacidade."""
        recommendations = []
        
        if capacity_level == "Crítica":
            recommendations.extend([
                "Solicitar apoio médico de outras regiões imediatamente",
                "Ativar protocolos de emergência médica",
                "Preparar unidades móveis de saúde",
                "Coordenar com hospitais militares ou federais"
            ])
        elif capacity_level == "Limitada":
            recommendations.extend([
                "Mobilizar recursos médicos adicionais",
                "Acelerar alta de pacientes não críticos",
                "Preparar áreas de triagem temporárias",
                "Coordenar transferências para hospitais vizinhos"
            ])
        elif capacity_level == "Adequada":
            recommendations.extend([
                "Monitorar ocupação em tempo real",
                "Preparar para aumento de demanda",
                "Mobilizar equipes de plantão"
            ])
        else:
            recommendations.extend([
                "Capacidade adequada para emergência",
                "Manter monitoramento contínuo",
                "Preparar para contingências"
            ])
        
        return recommendations
    
    def _assess_health_vulnerability(self, emergency_capacity: Dict, population: int) -> Dict:
        """Avalia vulnerabilidade do sistema de saúde."""
        total_capacity = emergency_capacity["overall_capacity_assessment"]["total_emergency_capacity"]
        
        # Calcular capacidade por 1000 habitantes
        capacity_per_1000 = (total_capacity / population) * 1000 if population > 0 else 0
        
        if capacity_per_1000 > 50:
            vulnerability = "Baixa"
        elif capacity_per_1000 > 25:
            vulnerability = "Moderada"
        elif capacity_per_1000 > 10:
            vulnerability = "Alta"
        else:
            vulnerability = "Crítica"
        
        return {
            "vulnerability_level": vulnerability,
            "capacity_per_1000": round(capacity_per_1000, 1),
            "risk_factors": self._identify_risk_factors(emergency_capacity),
            "mitigation_strategies": self._suggest_mitigation_strategies(vulnerability)
        }
    
    def _identify_risk_factors(self, emergency_capacity: Dict) -> List[str]:
        """Identifica fatores de risco."""
        risk_factors = []
        
        if emergency_capacity["immediate_care"]["emergency_beds_available"] < 10:
            risk_factors.append("Capacidade de atendimento imediato limitada")
        
        if emergency_capacity["hospitalization"]["icu_beds_available"] < 5:
            risk_factors.append("Leitos de UTI insuficientes")
        
        if emergency_capacity["immediate_care"]["ambulances_available"] < 3:
            risk_factors.append("Ambulâncias disponíveis limitadas")
        
        if emergency_capacity["evacuation_medical"]["ventilators_available"] < 5:
            risk_factors.append("Ventiladores disponíveis limitados")
        
        return risk_factors
    
    def _suggest_mitigation_strategies(self, vulnerability: str) -> List[str]:
        """Sugere estratégias de mitigação."""
        strategies = []
        
        if vulnerability in ["Crítica", "Alta"]:
            strategies.extend([
                "Mobilização imediata de recursos médicos externos",
                "Ativação de protocolos de emergência",
                "Preparação de unidades móveis de saúde",
                "Coordenar com sistemas de saúde regionais/nacionais"
            ])
        elif vulnerability == "Moderada":
            strategies.extend([
                "Preparar recursos médicos adicionais",
                "Acelerar protocolos de alta hospitalar",
                "Coordenar com hospitais vizinhos"
            ])
        else:
            strategies.extend([
                "Manter monitoramento contínuo",
                "Preparar para contingências"
            ])
        
        return strategies
    
    def get_health_facilities_map(self, bbox: Tuple[float, float, float, float]) -> Dict:
        """
        Gera mapa de instalações de saúde para uma área.
        
        Args:
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
        
        Returns:
            Mapa de instalações de saúde
        """
        try:
            min_lon, min_lat, max_lon, max_lat = bbox
            
            # Simular distribuição de instalações de saúde
            facilities = self._simulate_health_facilities_distribution(bbox)
            
            return {
                "success": True,
                "bbox": bbox,
                "facilities": facilities,
                "statistics": {
                    "total_hospitals": len([f for f in facilities if f["type"] == "hospital"]),
                    "total_clinics": len([f for f in facilities if f["type"] == "clinic"]),
                    "total_pharmacies": len([f for f in facilities if f["type"] == "pharmacy"]),
                    "total_ambulances": sum([f.get("ambulances", 0) for f in facilities if f["type"] == "hospital"])
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao gerar mapa de instalações: {str(e)}"
            }
    
    def _simulate_health_facilities_distribution(self, bbox: Tuple[float, float, float, float]) -> List[Dict]:
        """Simula distribuição de instalações de saúde."""
        import random
        
        min_lon, min_lat, max_lon, max_lat = bbox
        facilities = []
        
        # Calcular área e estimar número de instalações
        area_km2 = (max_lon - min_lon) * (max_lat - min_lat) * 111 * 111  # Aproximação
        estimated_population = int(area_km2 * 150)  # 150 pessoas/km²
        
        # Gerar hospitais
        num_hospitals = max(1, int(estimated_population / 50000))
        for i in range(num_hospitals):
            lat = min_lat + random.random() * (max_lat - min_lat)
            lon = min_lon + random.random() * (max_lon - min_lon)
            
            facilities.append({
                "type": "hospital",
                "name": f"Hospital {i+1}",
                "coordinates": {"lat": lat, "lon": lon},
                "beds": random.randint(100, 500),
                "icu_beds": random.randint(10, 50),
                "emergency_beds": random.randint(20, 100),
                "ventilators": random.randint(10, 30),
                "ambulances": random.randint(3, 8),
                "specialties": random.sample(self.simulated_health_data["hospitals"]["specialties"], 4)
            })
        
        # Gerar clínicas
        num_clinics = max(2, int(estimated_population / 10000))
        for i in range(num_clinics):
            lat = min_lat + random.random() * (max_lat - min_lat)
            lon = min_lon + random.random() * (max_lon - min_lon)
            
            facilities.append({
                "type": "clinic",
                "name": f"Clínica {i+1}",
                "coordinates": {"lat": lat, "lon": lon},
                "specialties": random.sample(self.simulated_health_data["clinics"]["types"], 2),
                "capacity": random.randint(50, 200)
            })
        
        # Gerar farmácias
        num_pharmacies = max(3, int(estimated_population / 5000))
        for i in range(num_pharmacies):
            lat = min_lat + random.random() * (max_lat - min_lat)
            lon = min_lon + random.random() * (max_lon - min_lon)
            
            facilities.append({
                "type": "pharmacy",
                "name": f"Farmácia {i+1}",
                "coordinates": {"lat": lat, "lon": lon},
                "emergency_medications": random.sample(self.simulated_health_data["pharmaceutical"]["emergency_medications"], 3)
            })
        
        return facilities
    
    def get_emergency_response_time(self, lat: float, lon: float, emergency_type: str = "medical") -> Dict:
        """
        Calcula tempo de resposta de emergência para uma localização.
        
        Args:
            lat: Latitude
            lon: Longitude
            emergency_type: Tipo de emergência (medical, fire, police)
        
        Returns:
            Tempo de resposta estimado
        """
        try:
            base_response_time = self.simulated_health_data["emergency_services"]["response_time_minutes"]
            
            # Simular variação baseada na localização
            import random
            location_factor = random.uniform(0.8, 1.5)
            traffic_factor = random.uniform(1.0, 1.3)
            
            estimated_time = base_response_time * location_factor * traffic_factor
            
            return {
                "success": True,
                "coordinates": {"lat": lat, "lon": lon},
                "emergency_type": emergency_type,
                "estimated_response_time_minutes": round(estimated_time, 1),
                "response_level": self._assess_response_level(estimated_time),
                "factors": {
                    "location_factor": round(location_factor, 2),
                    "traffic_factor": round(traffic_factor, 2),
                    "base_time": base_response_time
                },
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao calcular tempo de resposta: {str(e)}"
            }
    
    def _assess_response_level(self, response_time: float) -> str:
        """Avalia nível de resposta baseado no tempo."""
        if response_time <= 5:
            return "Excelente"
        elif response_time <= 10:
            return "Bom"
        elif response_time <= 15:
            return "Adequado"
        elif response_time <= 25:
            return "Lento"
        else:
            return "Crítico"

# Instância global do serviço
health_infrastructure_service = HealthInfrastructureService()
