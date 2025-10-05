"""
Serviço geográfico aprimorado com integração de dados reais de elevação e população.
"""

import requests
import numpy as np
from typing import Dict, List, Tuple, Optional
from services.usgs_service import usgs_service
from services.atmospheric_service import atmospheric_service
from services.air_quality_service import air_quality_service

def check_local_risk(lat: float, lon: float, crater_diameter_km: float) -> dict:
    """
    Verifica risco local com dados geográficos reais.
    """
    try:
        # Obter dados de elevação
        elevation_data = usgs_service.get_elevation_data(lat, lon, crater_diameter_km)
        
        # Obter dados atmosféricos
        atmospheric_data = atmospheric_service.get_merra2_data(lat, lon)
        
        # Obter dados de qualidade do ar
        air_quality_data = air_quality_service.get_airnow_data(lat, lon)
        
        # Calcular risco baseado nos dados reais
        risk_assessment = _calculate_comprehensive_risk(
            lat, lon, crater_diameter_km, elevation_data, atmospheric_data, air_quality_data
        )
        
        return {
            "latitude": lat,
            "longitude": lon,
            "crater_diameter_km": crater_diameter_km,
            "risk_assessment": risk_assessment,
            "elevation_data": elevation_data,
            "atmospheric_conditions": atmospheric_data,
            "air_quality": air_quality_data
        }
        
    except Exception as e:
        return {
            "latitude": lat,
            "longitude": lon,
            "error": f"Erro ao calcular risco local: {str(e)}",
            "fallback_data": {
                "in_risk_zone": True,
                "estimated_impact": "Alto (dados indisponíveis)",
                "population_density": "Dados indisponíveis"
            }
        }

def _calculate_comprehensive_risk(lat: float, lon: float, crater_diameter_km: float,
                                elevation_data: Dict, atmospheric_data: Dict, air_quality_data: Dict) -> Dict:
    """Calcula risco abrangente baseado em dados geográficos reais."""
    try:
        risk_factors = []
        total_risk_score = 0
        
        # Fator de elevação
        if elevation_data.get("success"):
            terrain_analysis = elevation_data.get("elevation_stats", {}).get("terrain_analysis", {})
            terrain_type = terrain_analysis.get("terrain_type", "Desconhecido")
            elevation_range = terrain_analysis.get("elevation_range_m", 0)
            
            # Terreno plano aumenta risco de propagação
            if terrain_type == "Plano":
                elevation_risk = 0.8
                risk_factors.append("Terreno plano - alta propagação de efeitos")
            elif terrain_type == "Suavemente Ondulado":
                elevation_risk = 0.6
                risk_factors.append("Terreno suavemente ondulado - propagação moderada")
            elif terrain_type == "Ondulado":
                elevation_risk = 0.4
                risk_factors.append("Terreno ondulado - propagação limitada")
            else:
                elevation_risk = 0.2
                risk_factors.append("Terreno montanhoso - propagação muito limitada")
            
            total_risk_score += elevation_risk
        else:
            elevation_risk = 0.5  # Risco médio se dados indisponíveis
            risk_factors.append("Dados de elevação indisponíveis")
            total_risk_score += elevation_risk
        
        # Fator atmosférico
        if atmospheric_data.get("success"):
            wind_speed = atmospheric_data.get("data", {}).get("WIND_SPEED", {}).get("value", 0)
            wind_direction = atmospheric_data.get("data", {}).get("WIND_DIRECTION", {}).get("value", 0)
            
            # Vento forte aumenta dispersão de poluentes
            if wind_speed > 10:
                atmospheric_risk = 0.7
                risk_factors.append(f"Vento forte ({wind_speed:.1f} m/s) - alta dispersão")
            elif wind_speed > 5:
                atmospheric_risk = 0.5
                risk_factors.append(f"Vento moderado ({wind_speed:.1f} m/s) - dispersão moderada")
            else:
                atmospheric_risk = 0.3
                risk_factors.append(f"Vento fraco ({wind_speed:.1f} m/s) - baixa dispersão")
            
            total_risk_score += atmospheric_risk
        else:
            atmospheric_risk = 0.5
            risk_factors.append("Dados atmosféricos indisponíveis")
            total_risk_score += atmospheric_risk
        
        # Fator de qualidade do ar
        if air_quality_data.get("success"):
            aqi = air_quality_data.get("data", {}).get("aqi", 0)
            
            # AQI alto indica vulnerabilidade prévia
            if aqi > 150:
                air_quality_risk = 0.8
                risk_factors.append(f"AQI alto ({aqi}) - vulnerabilidade prévia")
            elif aqi > 100:
                air_quality_risk = 0.6
                risk_factors.append(f"AQI moderado ({aqi}) - vulnerabilidade moderada")
            else:
                air_quality_risk = 0.3
                risk_factors.append(f"AQI baixo ({aqi}) - baixa vulnerabilidade")
            
            total_risk_score += air_quality_risk
        else:
            air_quality_risk = 0.5
            risk_factors.append("Dados de qualidade do ar indisponíveis")
            total_risk_score += air_quality_risk
        
        # Normalizar score (0-1)
        normalized_risk = total_risk_score / 3.0
        
        # Classificar risco
        if normalized_risk > 0.7:
            risk_level = "Muito Alto"
            risk_color = "red"
        elif normalized_risk > 0.5:
            risk_level = "Alto"
            risk_color = "orange"
        elif normalized_risk > 0.3:
            risk_level = "Moderado"
            risk_color = "yellow"
        else:
            risk_level = "Baixo"
            risk_color = "green"
        
        return {
            "risk_level": risk_level,
            "risk_score": normalized_risk,
            "risk_color": risk_color,
            "risk_factors": risk_factors,
            "component_scores": {
                "elevation_risk": elevation_risk,
                "atmospheric_risk": atmospheric_risk,
                "air_quality_risk": air_quality_risk
            },
            "recommendations": _generate_risk_recommendations(normalized_risk, risk_factors)
        }
        
    except Exception as e:
        return {
            "error": f"Erro no cálculo de risco: {str(e)}",
            "risk_level": "Desconhecido",
            "risk_score": 0.5
        }

def _generate_risk_recommendations(risk_score: float, risk_factors: List[str]) -> List[str]:
    """Gera recomendações baseadas no score de risco."""
    recommendations = []
    
    if risk_score > 0.7:
        recommendations.extend([
            "Evacuação imediata recomendada",
            "Ativação de protocolos de emergência",
            "Monitoramento contínuo da área",
            "Preparação de abrigos de emergência"
        ])
    elif risk_score > 0.5:
        recommendations.extend([
            "Monitoramento intensivo",
            "Preparação para possível evacuação",
            "Ativação de sistemas de alerta",
            "Coordenar com autoridades locais"
        ])
    elif risk_score > 0.3:
        recommendations.extend([
            "Monitoramento regular",
            "Preparação de planos de contingência",
            "Comunicação com comunidades locais"
        ])
    else:
        recommendations.extend([
            "Monitoramento básico",
            "Manter vigilância"
        ])
    
    return recommendations

def get_population_data(lat: float, lon: float, radius_km: float = 10) -> Dict:
    """
    Obtém dados de população para uma área específica.
    """
    try:
        # Em produção, integrar com APIs de dados demográficos reais
        # Por enquanto, usar estimativas baseadas em padrões geográficos
        
        # Simular densidade populacional baseada na localização
        if abs(lat) < 30:  # Região tropical (mais populosa)
            base_density = 200
        elif abs(lat) < 60:  # Região temperada
            base_density = 150
        else:  # Região polar
            base_density = 50
        
        # Ajustar baseado na longitude (aproximação para áreas urbanas)
        if abs(lon) < 30:  # Aproximação para áreas mais desenvolvidas
            density_multiplier = 2.0
        else:
            density_multiplier = 1.0
        
        population_density = base_density * density_multiplier
        
        # Calcular população total
        area_km2 = 3.14159 * radius_km ** 2
        total_population = int(area_km2 * population_density)
        
        # Distribuição por faixa etária (estimativas típicas)
        age_distribution = {
            "0-14": int(total_population * 0.25),
            "15-64": int(total_population * 0.65),
            "65+": int(total_population * 0.10)
        }
        
        # Grupos vulneráveis
        vulnerable_groups = {
            "children": age_distribution["0-14"],
            "elderly": age_distribution["65+"],
            "pregnant_women": int(total_population * 0.03),
            "people_with_respiratory_conditions": int(total_population * 0.05)
        }
        
        return {
            "success": True,
            "coordinates": [lon, lat],
            "radius_km": radius_km,
            "area_km2": area_km2,
            "population_density_per_km2": population_density,
            "total_population": total_population,
            "age_distribution": age_distribution,
            "vulnerable_groups": vulnerable_groups,
            "data_source": "Estimativa baseada em padrões geográficos",
            "note": "Em produção, usar dados reais de censo e demografia"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao obter dados de população: {str(e)}"
        }

def analyze_evacuation_capacity(lat: float, lon: float, radius_km: float = 20) -> Dict:
    """
    Analisa capacidade de evacuação da área.
    """
    try:
        # Obter dados de população
        population_data = get_population_data(lat, lon, radius_km)
        
        if not population_data.get("success"):
            return {
                "success": False,
                "error": "Falha ao obter dados de população"
            }
        
        total_population = population_data["total_population"]
        
        # Simular infraestrutura de evacuação
        # Em produção, usar dados reais de estradas, hospitais, abrigos
        
        evacuation_infrastructure = {
            "roads": {
                "major_highways": 2,
                "secondary_roads": 8,
                "local_roads": 25,
                "total_capacity_per_hour": 5000  # pessoas/hora
            },
            "shelters": {
                "emergency_shelters": 3,
                "capacity_per_shelter": 500,
                "total_capacity": 1500
            },
            "hospitals": {
                "hospitals": 2,
                "capacity_per_hospital": 200,
                "total_capacity": 400
            }
        }
        
        # Calcular tempo de evacuação
        evacuation_time_hours = total_population / evacuation_infrastructure["roads"]["total_capacity_per_hour"]
        
        # Analisar capacidade
        if evacuation_time_hours < 6:
            evacuation_capacity = "Alta"
            evacuation_feasibility = "Viável"
        elif evacuation_time_hours < 12:
            evacuation_capacity = "Moderada"
            evacuation_feasibility = "Viável com planejamento"
        elif evacuation_time_hours < 24:
            evacuation_capacity = "Baixa"
            evacuation_feasibility = "Desafiador"
        else:
            evacuation_capacity = "Muito Baixa"
            evacuation_feasibility = "Muito Desafiador"
        
        return {
            "success": True,
            "coordinates": [lon, lat],
            "radius_km": radius_km,
            "population_data": population_data,
            "evacuation_infrastructure": evacuation_infrastructure,
            "evacuation_analysis": {
                "estimated_evacuation_time_hours": evacuation_time_hours,
                "evacuation_capacity": evacuation_capacity,
                "evacuation_feasibility": evacuation_feasibility,
                "infrastructure_adequacy": "Adequada" if evacuation_time_hours < 12 else "Inadequada"
            },
            "recommendations": _generate_evacuation_recommendations(evacuation_time_hours)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro na análise de capacidade de evacuação: {str(e)}"
        }

def _generate_evacuation_recommendations(evacuation_time_hours: float) -> List[str]:
    """Gera recomendações baseadas no tempo de evacuação."""
    recommendations = []
    
    if evacuation_time_hours < 6:
        recommendations.extend([
            "Evacuação rápida é viável",
            "Focar em organização eficiente",
            "Manter rotas de evacuação desobstruídas"
        ])
    elif evacuation_time_hours < 12:
        recommendations.extend([
            "Planejamento detalhado necessário",
            "Implementar evacuação em fases",
            "Coordenar com autoridades de transporte"
        ])
    elif evacuation_time_hours < 24:
        recommendations.extend([
            "Evacuação desafiadora - começar cedo",
            "Considerar evacuação seletiva",
            "Preparar abrigos temporários"
        ])
    else:
        recommendations.extend([
            "Evacuação muito desafiadora",
            "Focar em proteção in-situ",
            "Preparar abrigos de emergência",
            "Coordenar com ajuda externa"
        ])
    
    return recommendations