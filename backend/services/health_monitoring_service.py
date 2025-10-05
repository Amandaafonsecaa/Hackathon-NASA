"""
Serviço para monitoramento de saúde e alertas pós-evento de impacto de asteroide.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

class HealthMonitoringService:
    def __init__(self):
        self.health_thresholds = {
            "aqi": {
                "good": 50,
                "moderate": 100,
                "unhealthy_sensitive": 150,
                "unhealthy": 200,
                "very_unhealthy": 300,
                "hazardous": 500
            },
            "pm25": {
                "good": 12,
                "moderate": 35,
                "unhealthy_sensitive": 55,
                "unhealthy": 150,
                "very_unhealthy": 250,
                "hazardous": 500
            },
            "pm10": {
                "good": 54,
                "moderate": 154,
                "unhealthy_sensitive": 254,
                "unhealthy": 354,
                "very_unhealthy": 424,
                "hazardous": 604
            },
            "no2": {
                "good": 53,
                "moderate": 100,
                "unhealthy_sensitive": 360,
                "unhealthy": 649,
                "very_unhealthy": 1249,
                "hazardous": 2049
            },
            "o3": {
                "good": 54,
                "moderate": 70,
                "unhealthy_sensitive": 85,
                "unhealthy": 105,
                "very_unhealthy": 200,
                "hazardous": 300
            }
        }
        
        self.sensitive_groups = [
            "crianças",
            "idosos",
            "pessoas com asma",
            "pessoas com doenças cardíacas",
            "pessoas com doenças pulmonares",
            "grávidas",
            "pessoas com sistema imunológico comprometido"
        ]
    
    def monitor_post_impact_health(self, 
                                 impact_coordinates: Tuple[float, float],
                                 impact_data: Dict,
                                 air_quality_data: Dict,
                                 time_since_impact_hours: float = 0) -> Dict:
        """
        Monitora condições de saúde pós-impacto.
        
        Args:
            impact_coordinates: Coordenadas do impacto (lat, lon)
            impact_data: Dados do impacto (energia, tipo, etc.)
            air_quality_data: Dados de qualidade do ar
            time_since_impact_hours: Tempo desde o impacto em horas
        
        Returns:
            Análise de saúde pós-impacto
        """
        try:
            lat, lon = impact_coordinates
            
            # Analisar impacto na qualidade do ar
            air_quality_impact = self._analyze_air_quality_impact(
                impact_data, air_quality_data, time_since_impact_hours
            )
            
            # Avaliar riscos à saúde
            health_risks = self._assess_health_risks(air_quality_impact)
            
            # Gerar alertas de saúde
            health_alerts = self._generate_health_alerts(health_risks, time_since_impact_hours)
            
            # Calcular recomendações de saúde
            health_recommendations = self._generate_health_recommendations(
                health_risks, air_quality_impact, time_since_impact_hours
            )
            
            # Estimar população afetada
            population_impact = self._estimate_population_impact(
                impact_coordinates, air_quality_impact
            )
            
            return {
                "success": True,
                "impact_coordinates": impact_coordinates,
                "time_since_impact_hours": time_since_impact_hours,
                "air_quality_impact": air_quality_impact,
                "health_risks": health_risks,
                "health_alerts": health_alerts,
                "health_recommendations": health_recommendations,
                "population_impact": population_impact,
                "monitoring_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no monitoramento de saúde: {str(e)}"
            }
    
    def _analyze_air_quality_impact(self, impact_data: Dict, air_quality_data: Dict, time_hours: float) -> Dict:
        """Analisa o impacto na qualidade do ar pós-impacto."""
        try:
            # Dados do impacto
            energy_megatons = impact_data.get("energia", {}).get("equivalente_tnt_megatons", 0)
            is_airburst = impact_data.get("fireball", {}).get("is_airburst", False)
            tsunami_generated = impact_data.get("tsunami", {}).get("tsunami_generated", False)
            
            # Dados de qualidade do ar
            current_aqi = air_quality_data.get("aqi", {}).get("value", 0)
            pollutants = air_quality_data.get("pollutants", {})
            
            # Calcular impacto pós-evento
            impact_factor = self._calculate_impact_factor(energy_megatons, is_airburst, time_hours)
            
            # Simular degradação da qualidade do ar
            degraded_air_quality = self._simulate_air_quality_degradation(
                pollutants, impact_factor, time_hours
            )
            
            # Calcular novo AQI
            new_aqi = self._calculate_new_aqi(degraded_air_quality)
            
            # Determinar zonas de risco
            risk_zones = self._determine_air_quality_risk_zones(
                degraded_air_quality, impact_factor
            )
            
            return {
                "baseline_aqi": current_aqi,
                "impact_factor": impact_factor,
                "degraded_pollutants": degraded_air_quality,
                "new_aqi": new_aqi,
                "aqi_change": new_aqi["value"] - current_aqi,
                "risk_zones": risk_zones,
                "time_decay_factor": self._calculate_time_decay_factor(time_hours)
            }
            
        except Exception as e:
            return {"error": f"Erro na análise de qualidade do ar: {str(e)}"}
    
    def _calculate_impact_factor(self, energy_megatons: float, is_airburst: bool, time_hours: float) -> float:
        """Calcula fator de impacto baseado na energia e tipo de evento."""
        try:
            # Fator base baseado na energia
            if energy_megatons < 1:
                base_factor = 1.2
            elif energy_megatons < 10:
                base_factor = 1.5
            elif energy_megatons < 100:
                base_factor = 2.0
            else:
                base_factor = 3.0
            
            # Modificador para airburst (mais poluentes atmosféricos)
            if is_airburst:
                base_factor *= 1.5
            
            # Fator de decaimento temporal
            decay_factor = max(0.3, 1.0 - (time_hours / 72))  # Decaimento em 72 horas
            
            return base_factor * decay_factor
            
        except Exception as e:
            return 1.0
    
    def _simulate_air_quality_degradation(self, pollutants: Dict, impact_factor: float, time_hours: float) -> Dict:
        """Simula degradação da qualidade do ar pós-impacto."""
        try:
            degraded_pollutants = {}
            
            for pollutant, data in pollutants.items():
                baseline_value = data.get("value", 0)
                
                # Calcular aumento baseado no tipo de poluente
                if pollutant == "NO2":
                    increase_factor = impact_factor * 2.0  # NO2 aumenta muito com explosões
                elif pollutant == "PM2_5":
                    increase_factor = impact_factor * 1.8  # Partículas finas aumentam
                elif pollutant == "PM10":
                    increase_factor = impact_factor * 1.5  # Partículas maiores
                elif pollutant == "O3":
                    increase_factor = impact_factor * 1.2  # Ozônio aumenta moderadamente
                else:
                    increase_factor = impact_factor
                
                # Aplicar fator de decaimento temporal
                time_decay = max(0.5, 1.0 - (time_hours / 48))  # Decaimento em 48 horas
                effective_increase = increase_factor * time_decay
                
                new_value = baseline_value * effective_increase
                
                degraded_pollutants[pollutant] = {
                    "baseline_value": baseline_value,
                    "new_value": new_value,
                    "increase_factor": effective_increase,
                    "unit": data.get("unit", ""),
                    "description": data.get("description", "")
                }
            
            return degraded_pollutants
            
        except Exception as e:
            return {"error": f"Erro na simulação de degradação: {str(e)}"}
    
    def _calculate_new_aqi(self, degraded_pollutants: Dict) -> Dict:
        """Calcula novo AQI baseado nos poluentes degradados."""
        try:
            # Calcular AQI para cada poluente
            aqi_values = []
            
            for pollutant, data in degraded_pollutants.items():
                if "error" in data:
                    continue
                
                value = data["new_value"]
                unit = data["unit"]
                
                # Converter para escala AQI (simplificado)
                if pollutant == "PM2_5" and unit == "μg/m³":
                    aqi = min(500, max(0, (value / 35) * 100))
                elif pollutant == "PM10" and unit == "μg/m³":
                    aqi = min(500, max(0, (value / 50) * 100))
                elif pollutant == "NO2" and unit == "ppb":
                    aqi = min(500, max(0, (value / 100) * 100))
                elif pollutant == "O3" and unit == "ppb":
                    aqi = min(500, max(0, (value / 70) * 100))
                else:
                    continue
                
                aqi_values.append(aqi)
            
            if not aqi_values:
                return {"value": 0, "category": "Unknown", "error": "Não foi possível calcular AQI"}
            
            # AQI é o máximo entre os valores
            max_aqi = max(aqi_values)
            
            # Classificar AQI
            if max_aqi <= 50:
                category = "Good"
            elif max_aqi <= 100:
                category = "Moderate"
            elif max_aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
            elif max_aqi <= 200:
                category = "Unhealthy"
            elif max_aqi <= 300:
                category = "Very Unhealthy"
            else:
                category = "Hazardous"
            
            return {
                "value": max_aqi,
                "category": category,
                "dominant_pollutant": "PM2.5",  # Simplificado
                "health_concern": "Low" if max_aqi <= 100 else "Moderate" if max_aqi <= 150 else "High"
            }
            
        except Exception as e:
            return {"error": f"Erro no cálculo do AQI: {str(e)}"}
    
    def _determine_air_quality_risk_zones(self, degraded_pollutants: Dict, impact_factor: float) -> List[Dict]:
        """Determina zonas de risco baseadas na qualidade do ar."""
        try:
            risk_zones = []
            
            # Zona de alto risco (próximo ao impacto)
            high_risk_zone = {
                "zone_type": "high_risk",
                "radius_km": 10 * impact_factor,
                "description": "Zona de alto risco - qualidade do ar muito degradada",
                "recommendations": [
                    "Evacuação imediata recomendada",
                    "Uso obrigatório de máscaras N95",
                    "Evitar atividades ao ar livre"
                ],
                "health_impact": "Crítico para grupos sensíveis"
            }
            
            # Zona de risco moderado
            moderate_risk_zone = {
                "zone_type": "moderate_risk",
                "radius_km": 25 * impact_factor,
                "description": "Zona de risco moderado - qualidade do ar degradada",
                "recommendations": [
                    "Grupos sensíveis devem evitar atividades ao ar livre",
                    "Considerar uso de máscaras",
                    "Monitorar sintomas respiratórios"
                ],
                "health_impact": "Moderado para grupos sensíveis"
            }
            
            # Zona de baixo risco
            low_risk_zone = {
                "zone_type": "low_risk",
                "radius_km": 50 * impact_factor,
                "description": "Zona de baixo risco - qualidade do ar ligeiramente afetada",
                "recommendations": [
                    "Monitoramento contínuo",
                    "Pessoas com problemas respiratórios devem ter cuidado"
                ],
                "health_impact": "Baixo para a maioria das pessoas"
            }
            
            risk_zones.extend([high_risk_zone, moderate_risk_zone, low_risk_zone])
            
            return risk_zones
            
        except Exception as e:
            return [{"error": f"Erro na determinação de zonas de risco: {str(e)}"}]
    
    def _assess_health_risks(self, air_quality_impact: Dict) -> Dict:
        """Avalia riscos à saúde baseados na qualidade do ar."""
        try:
            new_aqi = air_quality_impact.get("new_aqi", {})
            aqi_value = new_aqi.get("value", 0)
            aqi_category = new_aqi.get("category", "Unknown")
            
            # Avaliar riscos por grupo populacional
            general_population_risk = self._assess_population_risk(aqi_value, "general")
            sensitive_groups_risk = self._assess_population_risk(aqi_value, "sensitive")
            
            # Identificar sintomas esperados
            expected_symptoms = self._identify_expected_symptoms(aqi_value)
            
            # Calcular tempo de exposição seguro
            safe_exposure_time = self._calculate_safe_exposure_time(aqi_value)
            
            return {
                "aqi_level": aqi_value,
                "aqi_category": aqi_category,
                "general_population_risk": general_population_risk,
                "sensitive_groups_risk": sensitive_groups_risk,
                "expected_symptoms": expected_symptoms,
                "safe_exposure_time_minutes": safe_exposure_time,
                "emergency_threshold_exceeded": aqi_value > 200
            }
            
        except Exception as e:
            return {"error": f"Erro na avaliação de riscos: {str(e)}"}
    
    def _assess_population_risk(self, aqi_value: float, population_type: str) -> Dict:
        """Avalia risco para um tipo específico de população."""
        try:
            if population_type == "sensitive":
                # Grupos sensíveis são mais afetados
                if aqi_value <= 50:
                    risk_level = "Baixo"
                    description = "Baixo risco para grupos sensíveis"
                elif aqi_value <= 100:
                    risk_level = "Moderado"
                    description = "Risco moderado para grupos sensíveis"
                elif aqi_value <= 150:
                    risk_level = "Alto"
                    description = "Alto risco para grupos sensíveis"
                else:
                    risk_level = "Crítico"
                    description = "Risco crítico para grupos sensíveis"
            else:
                # População geral
                if aqi_value <= 100:
                    risk_level = "Baixo"
                    description = "Baixo risco para a população geral"
                elif aqi_value <= 150:
                    risk_level = "Moderado"
                    description = "Risco moderado para a população geral"
                elif aqi_value <= 200:
                    risk_level = "Alto"
                    description = "Alto risco para a população geral"
                else:
                    risk_level = "Crítico"
                    description = "Risco crítico para a população geral"
            
            return {
                "risk_level": risk_level,
                "description": description,
                "recommended_action": self._get_recommended_action(risk_level)
            }
            
        except Exception as e:
            return {"error": f"Erro na avaliação de risco populacional: {str(e)}"}
    
    def _get_recommended_action(self, risk_level: str) -> str:
        """Retorna ação recomendada baseada no nível de risco."""
        actions = {
            "Baixo": "Continuar atividades normais",
            "Moderado": "Reduzir atividades intensas ao ar livre",
            "Alto": "Evitar atividades ao ar livre",
            "Crítico": "Evacuação recomendada"
        }
        return actions.get(risk_level, "Avaliação adicional necessária")
    
    def _identify_expected_symptoms(self, aqi_value: float) -> List[str]:
        """Identifica sintomas esperados baseados no AQI."""
        symptoms = []
        
        if aqi_value > 100:
            symptoms.extend([
                "Irritação nos olhos",
                "Irritação na garganta",
                "Tosse leve"
            ])
        
        if aqi_value > 150:
            symptoms.extend([
                "Dificuldade respiratória leve",
                "Dor de cabeça",
                "Fadiga"
            ])
        
        if aqi_value > 200:
            symptoms.extend([
                "Dificuldade respiratória moderada",
                "Dor no peito",
                "Náusea"
            ])
        
        if aqi_value > 300:
            symptoms.extend([
                "Dificuldade respiratória severa",
                "Confusão",
                "Perda de consciência (em casos extremos)"
            ])
        
        return symptoms if symptoms else ["Nenhum sintoma esperado"]
    
    def _calculate_safe_exposure_time(self, aqi_value: float) -> float:
        """Calcula tempo de exposição seguro em minutos."""
        try:
            if aqi_value <= 50:
                return 480  # 8 horas
            elif aqi_value <= 100:
                return 240  # 4 horas
            elif aqi_value <= 150:
                return 120  # 2 horas
            elif aqi_value <= 200:
                return 60   # 1 hora
            elif aqi_value <= 300:
                return 30   # 30 minutos
            else:
                return 15   # 15 minutos
        except:
            return 60
    
    def _generate_health_alerts(self, health_risks: Dict, time_hours: float) -> List[Dict]:
        """Gera alertas de saúde baseados nos riscos identificados."""
        try:
            alerts = []
            
            if health_risks.get("emergency_threshold_exceeded"):
                alerts.append({
                    "alert_type": "EMERGENCY",
                    "priority": "HIGH",
                    "title": "Alerta de Emergência de Saúde",
                    "message": "Qualidade do ar em níveis perigosos - evacuação recomendada",
                    "affected_groups": self.sensitive_groups,
                    "immediate_actions": [
                        "Evacuação imediata da área",
                        "Uso obrigatório de máscaras N95",
                        "Ativação de protocolos de emergência médica"
                    ]
                })
            
            sensitive_risk = health_risks.get("sensitive_groups_risk", {})
            if sensitive_risk.get("risk_level") in ["Alto", "Crítico"]:
                alerts.append({
                    "alert_type": "SENSITIVE_GROUPS",
                    "priority": "MEDIUM",
                    "title": "Alerta para Grupos Sensíveis",
                    "message": "Grupos sensíveis devem evitar exposição ao ar livre",
                    "affected_groups": self.sensitive_groups,
                    "immediate_actions": [
                        "Ficar em ambientes fechados",
                        "Usar purificadores de ar",
                        "Monitorar sintomas respiratórios"
                    ]
                })
            
            # Alerta baseado no tempo desde o impacto
            if time_hours < 6:
                alerts.append({
                    "alert_type": "IMMEDIATE_POST_IMPACT",
                    "priority": "HIGH",
                    "title": "Período Crítico Pós-Impacto",
                    "message": "Primeiras 6 horas são críticas para exposição a poluentes",
                    "affected_groups": ["Toda a população"],
                    "immediate_actions": [
                        "Evitar exposição desnecessária",
                        "Monitorar qualidade do ar",
                        "Preparar equipamentos de proteção"
                    ]
                })
            
            return alerts
            
        except Exception as e:
            return [{"error": f"Erro na geração de alertas: {str(e)}"}]
    
    def _generate_health_recommendations(self, health_risks: Dict, air_quality_impact: Dict, time_hours: float) -> Dict:
        """Gera recomendações de saúde abrangentes."""
        try:
            recommendations = {
                "immediate_actions": [],
                "short_term_actions": [],
                "long_term_actions": [],
                "medical_preparations": [],
                "public_health_measures": []
            }
            
            aqi_value = health_risks.get("aqi_level", 0)
            
            # Ações imediatas
            if aqi_value > 150:
                recommendations["immediate_actions"].extend([
                    "Evitar atividades ao ar livre",
                    "Fechar janelas e portas",
                    "Usar máscaras N95 se necessário sair",
                    "Ativar sistemas de filtragem de ar"
                ])
            
            # Ações de curto prazo
            if time_hours < 24:
                recommendations["short_term_actions"].extend([
                    "Monitorar qualidade do ar continuamente",
                    "Preparar abrigos com ar filtrado",
                    "Distribuir máscaras para população",
                    "Ativar protocolos de saúde pública"
                ])
            
            # Ações de longo prazo
            if aqi_value > 100:
                recommendations["long_term_actions"].extend([
                    "Implementar monitoramento contínuo",
                    "Desenvolver planos de contingência",
                    "Treinar equipes de resposta médica",
                    "Estabelecer centros de saúde temporários"
                ])
            
            # Preparações médicas
            recommendations["medical_preparations"] = [
                "Estoque de medicamentos para problemas respiratórios",
                "Equipamentos de oxigenoterapia",
                "Máscaras e equipamentos de proteção",
                "Equipes médicas de emergência"
            ]
            
            # Medidas de saúde pública
            recommendations["public_health_measures"] = [
                "Comunicação de risco à população",
                "Distribuição de informações de saúde",
                "Ativação de linhas de emergência médica",
                "Coordenação com autoridades de saúde"
            ]
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Erro na geração de recomendações: {str(e)}"}
    
    def _estimate_population_impact(self, impact_coordinates: Tuple[float, float], air_quality_impact: Dict) -> Dict:
        """Estima população afetada baseada na qualidade do ar."""
        try:
            lat, lon = impact_coordinates
            risk_zones = air_quality_impact.get("risk_zones", [])
            
            # Simular densidade populacional (em produção, usar dados reais)
            population_estimates = {}
            
            for zone in risk_zones:
                if "error" in zone:
                    continue
                
                zone_type = zone.get("zone_type", "")
                radius_km = zone.get("radius_km", 0)
                
                # Estimativa simplificada de população
                # Em produção, usar dados reais de densidade populacional
                if zone_type == "high_risk":
                    population_density = 500  # pessoas/km²
                elif zone_type == "moderate_risk":
                    population_density = 300
                else:
                    population_density = 100
                
                area_km2 = 3.14159 * radius_km ** 2
                estimated_population = int(area_km2 * population_density)
                
                population_estimates[zone_type] = {
                    "radius_km": radius_km,
                    "area_km2": area_km2,
                    "population_density": population_density,
                    "estimated_population": estimated_population
                }
            
            total_affected = sum(est["estimated_population"] for est in population_estimates.values())
            
            return {
                "total_affected_population": total_affected,
                "zone_estimates": population_estimates,
                "methodology": "Estimativa baseada em densidade populacional típica",
                "note": "Em produção, usar dados reais de censo e demografia"
            }
            
        except Exception as e:
            return {"error": f"Erro na estimativa de população: {str(e)}"}
    
    def _calculate_time_decay_factor(self, time_hours: float) -> float:
        """Calcula fator de decaimento temporal para poluentes."""
        try:
            # Modelo de decaimento exponencial
            # Poluentes decaem com o tempo, mas alguns persistem mais
            if time_hours < 6:
                return 1.0  # Concentração máxima nas primeiras 6 horas
            elif time_hours < 24:
                return 0.8  # Decaimento moderado no primeiro dia
            elif time_hours < 72:
                return 0.5  # Decaimento significativo em 3 dias
            else:
                return 0.3  # Níveis baixos após 3 dias
        except:
            return 1.0

# Instância global do serviço
health_monitoring_service = HealthMonitoringService()
