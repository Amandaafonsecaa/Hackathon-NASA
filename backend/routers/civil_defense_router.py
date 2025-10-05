from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from services import civil_defense_service

router = APIRouter()

class AlertStatusRequest(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    alert_type: str = Field(default="asteroid_impact", description="Tipo de alerta")

class UpdateAlertRequest(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    new_alert_level: str = Field(..., description="Novo nível de alerta")
    alert_type: str = Field(default="asteroid_impact", description="Tipo de alerta")

@router.post("/alert-status", summary="Obter status de alerta de defesa civil")
def get_alert_status(request: AlertStatusRequest) -> Dict:
    """
    Obtém status de alerta de defesa civil para uma região.
    
    Inclui:
    - Nível de alerta atual
    - Recursos disponíveis
    - Planos de contingência ativos
    - Recomendações específicas
    """
    try:
        alert_status = civil_defense_service.get_alert_status(
            lat=request.lat,
            lon=request.lon,
            alert_type=request.alert_type
        )
        
        return alert_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status de alerta: {str(e)}")

@router.get("/alert-status", summary="Obter status de alerta de defesa civil (GET)")
def get_alert_status_get(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    alert_type: str = Query(default="asteroid_impact", description="Tipo de alerta")
) -> Dict:
    """
    Obtém status de alerta de defesa civil para uma região.
    """
    try:
        alert_status = civil_defense_service.get_alert_status(
            lat=lat,
            lon=lon,
            alert_type=alert_type
        )
        
        return alert_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status de alerta: {str(e)}")

@router.post("/update-alert", summary="Atualizar status de alerta")
def update_alert_status(request: UpdateAlertRequest) -> Dict:
    """
    Atualiza status de alerta de defesa civil.
    
    Níveis de alerta disponíveis:
    - green: Normal
    - yellow: Atenção
    - orange: Alerta
    - red: Emergência
    - black: Crise
    """
    try:
        update_result = civil_defense_service.update_alert_status(
            lat=request.lat,
            lon=request.lon,
            new_alert_level=request.new_alert_level,
            alert_type=request.alert_type
        )
        
        return update_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar alerta: {str(e)}")

@router.get("/emergency-coordination", summary="Coordenação de emergência")
def get_emergency_coordination(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    emergency_type: str = Query(default="asteroid_impact", description="Tipo de emergência")
) -> Dict:
    """
    Obtém informações de coordenação de emergência.
    
    Inclui:
    - Agências envolvidas
    - Centros de comando
    - Canais de comunicação
    - Protocolos de coordenação
    """
    try:
        coordination = civil_defense_service.get_emergency_coordination(
            lat=lat,
            lon=lon,
            emergency_type=emergency_type
        )
        
        return coordination
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na coordenação de emergência: {str(e)}")

@router.get("/available-resources", summary="Recursos disponíveis de defesa civil")
def get_available_resources(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    alert_level: str = Query(default="orange", description="Nível de alerta")
) -> Dict:
    """
    Obtém recursos disponíveis de defesa civil.
    
    Inclui:
    - Equipes de emergência
    - Equipamentos disponíveis
    - Abrigos de emergência
    - Nível de prontidão
    """
    try:
        # Obter status de alerta para acessar recursos
        alert_status = civil_defense_service.get_alert_status(
            lat=lat,
            lon=lon,
            alert_type="general"
        )
        
        if not alert_status.get("success"):
            return alert_status
        
        # Extrair informações de recursos
        available_resources = alert_status.get("available_resources", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "alert_level": alert_level,
            "available_resources": available_resources,
            "resource_summary": {
                "emergency_teams": len(available_resources.get("emergency_teams", {})),
                "equipment_types": len(available_resources.get("equipment", {})),
                "shelter_capacity": available_resources.get("shelters", {}).get("total_capacity", 0),
                "overall_readiness": available_resources.get("overall_readiness", {}).get("readiness_level", "Unknown")
            },
            "timestamp": alert_status.get("status_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter recursos disponíveis: {str(e)}")

@router.get("/contingency-plans", summary="Planos de contingência")
def get_contingency_plans(
    alert_level: str = Query(default="orange", description="Nível de alerta"),
    emergency_type: str = Query(default="asteroid_impact", description="Tipo de emergência")
) -> Dict:
    """
    Obtém planos de contingência baseados no nível de alerta.
    
    Inclui:
    - Planos ativos
    - Fases de execução
    - Coordenação necessária
    - Ações específicas
    """
    try:
        # Simular obtenção de planos de contingência
        contingency_data = civil_defense_service.simulated_civil_defense_data["contingency_plans"]
        
        # Filtrar planos baseado no nível de alerta
        active_plans = civil_defense_service._get_active_contingency_plans(alert_level, emergency_type)
        
        return {
            "success": True,
            "alert_level": alert_level,
            "emergency_type": emergency_type,
            "active_plans": active_plans,
            "available_plans": contingency_data,
            "plan_statistics": {
                "total_active_plans": len(active_plans),
                "high_priority_plans": len([p for p in active_plans if p.get("priority") == "Crítica"]),
                "coordination_required": len([p for p in active_plans if "coordination" in p])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter planos de contingência: {str(e)}")

@router.get("/emergency-teams", summary="Equipes de emergência disponíveis")
def get_emergency_teams(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém informações sobre equipes de emergência disponíveis.
    
    Inclui:
    - Tipos de equipes
    - Número de unidades
    - Pessoal disponível
    - Nível de prontidão
    """
    try:
        # Obter recursos disponíveis
        alert_status = civil_defense_service.get_alert_status(
            lat=lat,
            lon=lon,
            alert_type="general"
        )
        
        if not alert_status.get("success"):
            return alert_status
        
        emergency_teams = alert_status.get("available_resources", {}).get("emergency_teams", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "emergency_teams": emergency_teams,
            "team_summary": {
                "total_team_types": len(emergency_teams),
                "total_units": sum([team.get("units_available", 0) for team in emergency_teams.values()]),
                "total_personnel": sum([team.get("personnel_available", 0) for team in emergency_teams.values()]),
                "high_readiness_teams": len([team for team in emergency_teams.values() if team.get("readiness_level") == "Alto"])
            },
            "team_details": [
                {
                    "team_type": team_type,
                    "units_available": team_data.get("units_available", 0),
                    "personnel_available": team_data.get("personnel_available", 0),
                    "readiness_level": team_data.get("readiness_level", "Unknown")
                }
                for team_type, team_data in emergency_teams.items()
            ],
            "timestamp": alert_status.get("status_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter equipes de emergência: {str(e)}")

@router.get("/shelters", summary="Abrigos de emergência")
def get_emergency_shelters(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém informações sobre abrigos de emergência disponíveis.
    
    Inclui:
    - Capacidade total
    - Tipos de abrigos
    - Serviços disponíveis
    - Localização
    """
    try:
        # Obter recursos disponíveis
        alert_status = civil_defense_service.get_alert_status(
            lat=lat,
            lon=lon,
            alert_type="general"
        )
        
        if not alert_status.get("success"):
            return alert_status
        
        shelter_info = alert_status.get("available_resources", {}).get("shelters", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "shelters": shelter_info,
            "shelter_summary": {
                "total_capacity": shelter_info.get("total_capacity", 0),
                "available_shelters": shelter_info.get("available_shelters", 0),
                "shelter_types": shelter_info.get("shelter_types", []),
                "capacity_per_shelter": shelter_info.get("total_capacity", 0) / max(1, shelter_info.get("available_shelters", 1))
            },
            "services_available": civil_defense_service.simulated_civil_defense_data["resources"]["shelters"]["services"],
            "timestamp": alert_status.get("status_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter abrigos de emergência: {str(e)}")

@router.get("/alert-levels", summary="Níveis de alerta disponíveis")
def get_alert_levels() -> Dict:
    """
    Obtém informações sobre todos os níveis de alerta disponíveis.
    
    Inclui:
    - Descrição de cada nível
    - Ações necessárias
    - Escala de prioridade
    """
    try:
        alert_levels = civil_defense_service.simulated_civil_defense_data["alert_levels"]
        
        return {
            "success": True,
            "alert_levels": alert_levels,
            "level_summary": {
                "total_levels": len(alert_levels),
                "highest_level": max([level_info["level"] for level_info in alert_levels.values()]),
                "lowest_level": min([level_info["level"] for level_info in alert_levels.values()])
            },
            "usage_guidelines": {
                "green": "Monitoramento normal, sem ações especiais",
                "yellow": "Aumentar vigilância, preparar recursos",
                "orange": "Mobilizar recursos, ativar planos",
                "red": "Emergência ativa, evacuação recomendada",
                "black": "Crise máxima, evacuação obrigatória"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter níveis de alerta: {str(e)}")
