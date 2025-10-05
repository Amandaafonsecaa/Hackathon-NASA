"""
Serviço para dados de defesa civil e gestão de emergências.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class CivilDefenseService:
    def __init__(self):
        # URLs de APIs de defesa civil (simuladas para demonstração)
        self.fema_api = "https://www.fema.gov/api/open/v1"
        self.red_cross_api = "https://www.redcross.org/api"
        self.un_ocha_api = "https://api.humanitarianresponse.info"
        
        # Dados simulados de defesa civil
        self.simulated_civil_defense_data = {
            "alert_levels": {
                "green": {"level": 1, "description": "Normal", "action_required": "Monitoramento"},
                "yellow": {"level": 2, "description": "Atenção", "action_required": "Preparação"},
                "orange": {"level": 3, "description": "Alerta", "action_required": "Mobilização"},
                "red": {"level": 4, "description": "Emergência", "action_required": "Ação Imediata"},
                "black": {"level": 5, "description": "Crise", "action_required": "Evacuação Imediata"}
            },
            "resources": {
                "emergency_teams": {
                    "search_rescue": {"units_per_100k": 2, "personnel_per_unit": 8},
                    "medical_emergency": {"units_per_100k": 3, "personnel_per_unit": 6},
                    "hazardous_materials": {"units_per_100k": 0.5, "personnel_per_unit": 10},
                    "communications": {"units_per_100k": 1, "personnel_per_unit": 4}
                },
                "equipment": {
                    "emergency_vehicles": {"per_100k": 15},
                    "communication_radios": {"per_100k": 50},
                    "generators": {"per_100k": 8},
                    "emergency_supplies": {"per_100k": 200}
                },
                "shelters": {
                    "capacity_per_100k": 5000,
                    "types": ["Emergency", "Temporary", "Long-term"],
                    "services": ["Food", "Water", "Medical", "Communications"]
                }
            },
            "contingency_plans": {
                "evacuation": {
                    "phases": ["Warning", "Preparation", "Evacuation", "Shelter", "Return"],
                    "coordination": ["Police", "Fire", "Medical", "Transport", "Communications"]
                },
                "search_rescue": {
                    "priority_areas": ["Residential", "Commercial", "Critical Infrastructure"],
                    "methods": ["Grid Search", "Aerial Search", "K9 Units", "Technical Rescue"]
                },
                "emergency_communications": {
                    "channels": ["Radio", "Satellite", "Internet", "Mobile Networks"],
                    "backup_systems": ["HAM Radio", "Emergency Broadcast", "Satellite Phones"]
                }
            }
        }
    
    def get_alert_status(self, lat: float, lon: float, alert_type: str = "asteroid_impact") -> Dict:
        """
        Obtém status de alerta de defesa civil para uma região.
        
        Args:
            lat: Latitude
            lon: Longitude
            alert_type: Tipo de alerta
        
        Returns:
            Status de alerta atual
        """
        try:
            # Simular status de alerta baseado em fatores
            alert_level = self._calculate_alert_level(lat, lon, alert_type)
            alert_info = self.simulated_civil_defense_data["alert_levels"][alert_level]
            
            # Obter recursos disponíveis
            available_resources = self._get_available_resources(lat, lon, alert_level)
            
            # Obter planos de contingência ativos
            active_plans = self._get_active_contingency_plans(alert_level, alert_type)
            
            return {
                "success": True,
                "alert_info": {
                    "level": alert_level,
                    "level_number": alert_info["level"],
                    "description": alert_info["description"],
                    "action_required": alert_info["action_required"],
                    "alert_type": alert_type
                },
                "coordinates": {"lat": lat, "lon": lon},
                "available_resources": available_resources,
                "active_plans": active_plans,
                "recommendations": self._generate_alert_recommendations(alert_level, alert_type),
                "status_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter status de alerta: {str(e)}"
            }
    
    def _calculate_alert_level(self, lat: float, lon: float, alert_type: str) -> str:
        """Calcula nível de alerta baseado em fatores."""
        import random
        
        # Simular cálculo baseado em múltiplos fatores
        base_level = random.choice(["green", "yellow", "orange", "red", "black"])
        
        # Ajustar baseado no tipo de alerta
        if alert_type == "asteroid_impact":
            # Aumentar probabilidade de alertas mais altos
            if random.random() < 0.3:
                base_level = "red"
            elif random.random() < 0.5:
                base_level = "orange"
        
        return base_level
    
    def _get_available_resources(self, lat: float, lon: float, alert_level: str) -> Dict:
        """Obtém recursos disponíveis."""
        import random
        
        # Estimar população da região (simulado)
        estimated_population = 100000  # 100k habitantes
        
        # Calcular recursos baseados na população
        resources = {}
        
        for team_type, team_info in self.simulated_civil_defense_data["resources"]["emergency_teams"].items():
            units_needed = int(estimated_population * team_info["units_per_100k"] / 100000)
            total_personnel = units_needed * team_info["personnel_per_unit"]
            
            # Ajustar baseado no nível de alerta
            availability_factor = self._get_availability_factor(alert_level)
            available_personnel = int(total_personnel * availability_factor)
            
            resources[team_type] = {
                "units_available": max(1, int(units_needed * availability_factor)),
                "personnel_available": max(team_info["personnel_per_unit"], available_personnel),
                "readiness_level": self._assess_readiness_level(availability_factor)
            }
        
        # Calcular equipamentos disponíveis
        equipment = {}
        for equip_type, equip_info in self.simulated_civil_defense_data["resources"]["equipment"].items():
            total_equipment = int(estimated_population * equip_info["per_100k"] / 100000)
            availability_factor = self._get_availability_factor(alert_level)
            available_equipment = int(total_equipment * availability_factor)
            
            equipment[equip_type] = {
                "total_available": max(1, available_equipment),
                "operational_status": "Operacional" if availability_factor > 0.8 else "Limitado"
            }
        
        # Calcular abrigos disponíveis
        shelter_capacity = int(estimated_population * self.simulated_civil_defense_data["resources"]["shelters"]["capacity_per_100k"] / 100000)
        
        return {
            "emergency_teams": resources,
            "equipment": equipment,
            "shelters": {
                "total_capacity": shelter_capacity,
                "available_shelters": max(1, int(shelter_capacity / 1000)),
                "shelter_types": self.simulated_civil_defense_data["resources"]["shelters"]["types"]
            },
            "overall_readiness": self._assess_overall_readiness(resources, equipment, alert_level)
        }
    
    def _get_availability_factor(self, alert_level: str) -> float:
        """Calcula fator de disponibilidade baseado no nível de alerta."""
        factors = {
            "green": 0.9,
            "yellow": 0.85,
            "orange": 0.8,
            "red": 0.95,  # Mobilização total
            "black": 1.0  # Máxima mobilização
        }
        return factors.get(alert_level, 0.8)
    
    def _assess_readiness_level(self, availability_factor: float) -> str:
        """Avalia nível de prontidão."""
        if availability_factor >= 0.9:
            return "Alto"
        elif availability_factor >= 0.7:
            return "Bom"
        elif availability_factor >= 0.5:
            return "Moderado"
        else:
            return "Baixo"
    
    def _assess_overall_readiness(self, teams: Dict, equipment: Dict, alert_level: str) -> Dict:
        """Avalia prontidão geral do sistema."""
        # Calcular pontuação geral
        team_readiness = sum([1 if team["readiness_level"] in ["Alto", "Bom"] else 0.5 for team in teams.values()])
        equipment_readiness = sum([1 if equip["operational_status"] == "Operacional" else 0.5 for equip in equipment.values()])
        
        total_score = (team_readiness + equipment_readiness) / (len(teams) + len(equipment))
        
        if total_score >= 0.8:
            readiness_level = "Excelente"
        elif total_score >= 0.6:
            readiness_level = "Boa"
        elif total_score >= 0.4:
            readiness_level = "Adequada"
        else:
            readiness_level = "Limitada"
        
        return {
            "readiness_level": readiness_level,
            "readiness_score": round(total_score, 2),
            "can_handle_emergency": readiness_level in ["Excelente", "Boa"],
            "improvement_needed": readiness_level in ["Limitada", "Adequada"]
        }
    
    def _get_active_contingency_plans(self, alert_level: str, alert_type: str) -> List[Dict]:
        """Obtém planos de contingência ativos."""
        active_plans = []
        
        # Baseado no nível de alerta, ativar diferentes planos
        if alert_level in ["red", "black"]:
            active_plans.extend([
                {
                    "plan_name": "Evacuação de Emergência",
                    "status": "Ativo",
                    "phases": self.simulated_civil_defense_data["contingency_plans"]["evacuation"]["phases"],
                    "coordination": self.simulated_civil_defense_data["contingency_plans"]["evacuation"]["coordination"],
                    "priority": "Alta"
                },
                {
                    "plan_name": "Busca e Resgate",
                    "status": "Preparado",
                    "priority_areas": self.simulated_civil_defense_data["contingency_plans"]["search_rescue"]["priority_areas"],
                    "methods": self.simulated_civil_defense_data["contingency_plans"]["search_rescue"]["methods"],
                    "priority": "Alta"
                }
            ])
        
        if alert_level in ["orange", "red", "black"]:
            active_plans.append({
                "plan_name": "Comunicações de Emergência",
                "status": "Ativo",
                "channels": self.simulated_civil_defense_data["contingency_plans"]["emergency_communications"]["channels"],
                "backup_systems": self.simulated_civil_defense_data["contingency_plans"]["emergency_communications"]["backup_systems"],
                "priority": "Crítica"
            })
        
        # Adicionar planos específicos para tipo de alerta
        if alert_type == "asteroid_impact":
            active_plans.append({
                "plan_name": "Impacto de Asteroide",
                "status": "Ativo",
                "specific_actions": [
                    "Ativar centros de comando",
                    "Mobilizar equipes de busca e resgate",
                    "Preparar abrigos de emergência",
                    "Coordenar com agências espaciais",
                    "Ativar sistemas de comunicação de emergência"
                ],
                "priority": "Crítica"
            })
        
        return active_plans
    
    def _generate_alert_recommendations(self, alert_level: str, alert_type: str) -> List[str]:
        """Gera recomendações baseadas no nível de alerta."""
        recommendations = []
        
        if alert_level == "black":
            recommendations.extend([
                "Evacuação imediata da área de risco",
                "Ativar todos os recursos de emergência",
                "Coordenar com agências nacionais/internacionais",
                "Implementar protocolos de crise máxima"
            ])
        elif alert_level == "red":
            recommendations.extend([
                "Iniciar evacuação da área de risco",
                "Mobilizar todos os recursos disponíveis",
                "Ativar centros de comando de emergência",
                "Coordenar com autoridades regionais"
            ])
        elif alert_level == "orange":
            recommendations.extend([
                "Preparar para evacuação imediata",
                "Mobilizar recursos de emergência",
                "Ativar planos de contingência",
                "Alertar população"
            ])
        elif alert_level == "yellow":
            recommendations.extend([
                "Monitorar situação continuamente",
                "Preparar recursos para mobilização",
                "Revisar planos de contingência",
                "Manter comunicação com autoridades"
            ])
        else:  # green
            recommendations.extend([
                "Monitoramento normal",
                "Manter recursos em prontidão",
                "Atualizar planos de contingência"
            ])
        
        # Adicionar recomendações específicas por tipo
        if alert_type == "asteroid_impact":
            recommendations.extend([
                "Coordenar com observatórios astronômicos",
                "Monitorar trajetória do objeto",
                "Preparar para múltiplos cenários de impacto"
            ])
        
        return recommendations
    
    def get_emergency_coordination(self, lat: float, lon: float, emergency_type: str = "asteroid_impact") -> Dict:
        """
        Obtém informações de coordenação de emergência.
        
        Args:
            lat: Latitude
            lon: Longitude
            emergency_type: Tipo de emergência
        
        Returns:
            Informações de coordenação
        """
        try:
            # Obter status de alerta
            alert_status = self.get_alert_status(lat, lon, emergency_type)
            
            if not alert_status.get("success"):
                return alert_status
            
            # Obter agências envolvidas
            involved_agencies = self._get_involved_agencies(emergency_type, alert_status["alert_info"]["level"])
            
            # Obter centros de comando
            command_centers = self._get_command_centers(lat, lon, alert_status["alert_info"]["level"])
            
            # Obter canais de comunicação
            communication_channels = self._get_communication_channels(alert_status["alert_info"]["level"])
            
            return {
                "success": True,
                "emergency_type": emergency_type,
                "coordinates": {"lat": lat, "lon": lon},
                "alert_status": alert_status["alert_info"],
                "involved_agencies": involved_agencies,
                "command_centers": command_centers,
                "communication_channels": communication_channels,
                "coordination_protocols": self._get_coordination_protocols(emergency_type),
                "status_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na coordenação de emergência: {str(e)}"
            }
    
    def _get_involved_agencies(self, emergency_type: str, alert_level: str) -> List[Dict]:
        """Obtém agências envolvidas na resposta."""
        agencies = []
        
        # Agências base sempre envolvidas
        base_agencies = [
            {"name": "Defesa Civil Local", "role": "Coordenação Local", "priority": "Alta"},
            {"name": "Polícia Militar", "role": "Segurança e Ordem", "priority": "Alta"},
            {"name": "Corpo de Bombeiros", "role": "Resgate e Emergências", "priority": "Alta"},
            {"name": "Serviços Médicos", "role": "Atendimento Médico", "priority": "Alta"}
        ]
        
        agencies.extend(base_agencies)
        
        # Agências específicas por tipo de emergência
        if emergency_type == "asteroid_impact":
            agencies.extend([
                {"name": "NASA/JPL", "role": "Monitoramento Espacial", "priority": "Crítica"},
                {"name": "NOAA", "role": "Monitoramento Atmosférico", "priority": "Alta"},
                {"name": "USGS", "role": "Monitoramento Geológico", "priority": "Alta"},
                {"name": "FEMA", "role": "Coordenação Federal", "priority": "Alta"}
            ])
        
        # Agências adicionais para alertas altos
        if alert_level in ["red", "black"]:
            agencies.extend([
                {"name": "Exército", "role": "Suporte Militar", "priority": "Alta"},
                {"name": "Cruz Vermelha", "role": "Assistência Humanitária", "priority": "Alta"},
                {"name": "Organizações Internacionais", "role": "Suporte Internacional", "priority": "Moderada"}
            ])
        
        return agencies
    
    def _get_command_centers(self, lat: float, lon: float, alert_level: str) -> List[Dict]:
        """Obtém centros de comando disponíveis."""
        import random
        
        centers = []
        
        # Centro de comando principal
        centers.append({
            "name": "Centro de Comando Principal",
            "type": "Primary",
            "coordinates": {
                "lat": lat + random.uniform(-0.01, 0.01),
                "lon": lon + random.uniform(-0.01, 0.01)
            },
            "capabilities": ["Coordenação", "Comunicação", "Monitoramento"],
            "status": "Ativo"
        })
        
        # Centros secundários para alertas altos
        if alert_level in ["red", "black"]:
            for i in range(2):
                centers.append({
                    "name": f"Centro de Comando Secundário {i+1}",
                    "type": "Secondary",
                    "coordinates": {
                        "lat": lat + random.uniform(-0.05, 0.05),
                        "lon": lon + random.uniform(-0.05, 0.05)
                    },
                    "capabilities": ["Coordenação Regional", "Comunicação Backup"],
                    "status": "Ativo"
                })
        
        return centers
    
    def _get_communication_channels(self, alert_level: str) -> Dict:
        """Obtém canais de comunicação disponíveis."""
        channels = {
            "primary": {
                "radio_emergency": {"status": "Operacional", "priority": "Crítica"},
                "satellite_communication": {"status": "Operacional", "priority": "Alta"},
                "mobile_networks": {"status": "Operacional", "priority": "Alta"}
            },
            "backup": {
                "ham_radio": {"status": "Disponível", "priority": "Moderada"},
                "emergency_broadcast": {"status": "Disponível", "priority": "Moderada"},
                "internet_backup": {"status": "Disponível", "priority": "Baixa"}
            }
        }
        
        # Ajustar baseado no nível de alerta
        if alert_level in ["red", "black"]:
            channels["backup"]["ham_radio"]["priority"] = "Alta"
            channels["backup"]["emergency_broadcast"]["priority"] = "Alta"
        
        return channels
    
    def _get_coordination_protocols(self, emergency_type: str) -> List[Dict]:
        """Obtém protocolos de coordenação."""
        protocols = [
            {
                "name": "Protocolo de Comunicação",
                "description": "Estabelece canais de comunicação entre agências",
                "priority": "Crítica",
                "steps": [
                    "Ativar canais de comunicação primários",
                    "Estabelecer backup de comunicação",
                    "Definir frequências de emergência",
                    "Testar conectividade"
                ]
            },
            {
                "name": "Protocolo de Coordenação",
                "description": "Define estrutura de comando e controle",
                "priority": "Crítica",
                "steps": [
                    "Ativar centro de comando principal",
                    "Estabelecer hierarquia de comando",
                    "Definir responsabilidades por agência",
                    "Implementar sistema de relatórios"
                ]
            }
        ]
        
        if emergency_type == "asteroid_impact":
            protocols.append({
                "name": "Protocolo de Impacto Espacial",
                "description": "Protocolos específicos para eventos espaciais",
                "priority": "Crítica",
                "steps": [
                    "Coordenar com observatórios astronômicos",
                    "Monitorar trajetória do objeto",
                    "Ativar sistemas de alerta precoce",
                    "Preparar para múltiplos cenários"
                ]
            })
        
        return protocols
    
    def update_alert_status(self, lat: float, lon: float, new_alert_level: str, alert_type: str = "asteroid_impact") -> Dict:
        """
        Atualiza status de alerta (simulado).
        
        Args:
            lat: Latitude
            lon: Longitude
            new_alert_level: Novo nível de alerta
            alert_type: Tipo de alerta
        
        Returns:
            Status da atualização
        """
        try:
            if new_alert_level not in self.simulated_civil_defense_data["alert_levels"]:
                return {
                    "success": False,
                    "error": f"Nível de alerta inválido: {new_alert_level}"
                }
            
            # Simular atualização de status
            alert_info = self.simulated_civil_defense_data["alert_levels"][new_alert_level]
            
            return {
                "success": True,
                "alert_updated": {
                    "coordinates": {"lat": lat, "lon": lon},
                    "new_level": new_alert_level,
                    "level_info": alert_info,
                    "alert_type": alert_type
                },
                "actions_triggered": self._get_actions_for_alert_level(new_alert_level),
                "updated_at": datetime.now().isoformat(),
                "message": f"Alerta atualizado para nível {new_alert_level}: {alert_info['description']}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao atualizar alerta: {str(e)}"
            }
    
    def _get_actions_for_alert_level(self, alert_level: str) -> List[str]:
        """Obtém ações acionadas por nível de alerta."""
        actions = {
            "green": ["Monitoramento normal"],
            "yellow": ["Aumentar monitoramento", "Preparar recursos"],
            "orange": ["Mobilizar recursos", "Ativar planos", "Alertar população"],
            "red": ["Evacuação", "Mobilização total", "Ativar emergência"],
            "black": ["Evacuação imediata", "Crise máxima", "Suporte nacional"]
        }
        return actions.get(alert_level, [])

# Instância global do serviço
civil_defense_service = CivilDefenseService()
