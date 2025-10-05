from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from services import report_service, physics_service, geojson_service, evacuation_service

router = APIRouter()

class ReportRequest(BaseModel):
    # Dados de simulação
    diameter_m: float = Field(..., description="Diâmetro do asteroide em metros")
    velocity_kms: float = Field(..., description="Velocidade do asteroide em km/s")
    impact_angle_deg: float = Field(default=45, description="Ângulo de impacto em graus")
    target_type: str = Field(default="rocha", description="Tipo de terreno (solo, rocha, oceano)")
    wind_speed_ms: float = Field(default=10, description="Velocidade do vento em m/s")
    wind_direction_deg: float = Field(default=0, description="Direção do vento em graus")
    
    # Coordenadas do impacto
    impact_latitude: float = Field(..., description="Latitude do ponto de impacto")
    impact_longitude: float = Field(..., description="Longitude do ponto de impacto")
    
    # Dados do asteroide (opcional)
    asteroid_name: Optional[str] = Field(default=None, description="Nome do asteroide")
    asteroid_id: Optional[str] = Field(default=None, description="ID do asteroide")
    is_potentially_hazardous: Optional[bool] = Field(default=False, description="Se é potencialmente perigoso")
    
    # Pontos de evacuação
    evacuation_points: List[Dict] = Field(default_factory=list, description="Lista de pontos de evacuação")

@router.post("/generate-executive-report", summary="Gerar relatório executivo completo em PDF")
def generate_executive_report(request: ReportRequest) -> Response:
    """
    Gera um relatório executivo completo em PDF contendo:
    - Análise de impacto completa
    - Zonas de risco identificadas
    - Plano de evacuação
    - Recomendações estratégicas
    - Anexos técnicos
    """
    try:
        # Executar simulação de impacto
        impact_simulation = physics_service.calculate_all_impact_effects(
            diameter_m=request.diameter_m,
            velocity_kms=request.velocity_kms,
            impact_angle_deg=request.impact_angle_deg,
            tipo_terreno=request.target_type,
            wind_speed_ms=request.wind_speed_ms,
            wind_direction_deg=request.wind_direction_deg
        )
        
        # Gerar zonas de risco GeoJSON
        risk_zones_geojson = geojson_service.generate_impact_risk_zones(
            impact_lat=request.impact_latitude,
            impact_lon=request.impact_longitude,
            physics_results=impact_simulation
        )
        
        # Calcular evacuação (se pontos fornecidos)
        evacuation_analysis = None
        if request.evacuation_points:
            evacuation_analysis = evacuation_service.calculate_evacuation_routes(
                start_lat=request.impact_latitude,
                start_lon=request.impact_longitude,
                risk_zones_geojson=risk_zones_geojson,
                evacuation_points=request.evacuation_points,
                transport_mode="car",
                buffer_km=5.0
            )
        else:
            # Criar análise básica de evacuação
            evacuation_analysis = {
                "success": True,
                "total_routes": 0,
                "statistics": {
                    "total_routes": 0,
                    "average_distance_km": 0,
                    "average_time_hours": 0,
                    "average_safety_score": 0,
                    "risk_zones_avoided": len(risk_zones_geojson.get("features", []))
                },
                "routes": []
            }
        
        # Preparar informações do asteroide
        asteroid_info = None
        if request.asteroid_name or request.asteroid_id:
            asteroid_info = {
                "name": request.asteroid_name or "Asteroide Desconhecido",
                "id": request.asteroid_id,
                "is_potentially_hazardous": request.is_potentially_hazardous,
                "diameter_m": request.diameter_m,
                "classification": {
                    "object_type": "Asteroid",
                    "pha_flag": "Y" if request.is_potentially_hazardous else "N",
                    "orbit_class": "Unknown"
                }
            }
        
        # Gerar PDF
        pdf_bytes = report_service.generate_executive_report(
            impact_simulation=impact_simulation,
            risk_zones_geojson=risk_zones_geojson,
            evacuation_analysis=evacuation_analysis,
            asteroid_info=asteroid_info,
            impact_coordinates=[request.impact_longitude, request.impact_latitude]
        )
        
        # Retornar PDF como resposta
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=relatorio_impacto_asteroide.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.post("/generate-simulation-report", summary="Gerar relatório de simulação básica")
def generate_simulation_report(request: ReportRequest) -> Dict:
    """
    Gera um relatório de simulação básico em formato JSON.
    Útil para visualização rápida dos resultados.
    """
    try:
        # Executar simulação de impacto
        impact_simulation = physics_service.calculate_all_impact_effects(
            diameter_m=request.diameter_m,
            velocity_kms=request.velocity_kms,
            impact_angle_deg=request.impact_angle_deg,
            tipo_terreno=request.target_type,
            wind_speed_ms=request.wind_speed_ms,
            wind_direction_deg=request.wind_direction_deg
        )
        
        # Gerar zonas de risco GeoJSON
        risk_zones_geojson = geojson_service.generate_impact_risk_zones(
            impact_lat=request.impact_latitude,
            impact_lon=request.impact_longitude,
            physics_results=impact_simulation
        )
        
        # Calcular estatísticas resumidas
        energy_megatons = impact_simulation.get("energia", {}).get("equivalente_tnt_megatons", 0)
        crater_diameter = impact_simulation.get("cratera", {}).get("diametro_final_km", 0)
        earthquake_magnitude = impact_simulation.get("terremoto", {}).get("magnitude_richter", 0)
        
        # Avaliar criticidade
        if energy_megatons > 100:
            criticality = "CRÍTICO"
        elif energy_megatons > 10:
            criticality = "ALTO"
        elif energy_megatons > 1:
            criticality = "MODERADO"
        else:
            criticality = "BAIXO"
        
        # Contar zonas de risco
        risk_zones_count = len(risk_zones_geojson.get("features", []))
        
        return {
            "success": True,
            "report_type": "simulation_summary",
            "impact_coordinates": [request.impact_longitude, request.impact_latitude],
            "asteroid_info": {
                "name": request.asteroid_name,
                "id": request.asteroid_id,
                "diameter_m": request.diameter_m,
                "is_potentially_hazardous": request.is_potentially_hazardous
            },
            "impact_summary": {
                "energy_megatons": energy_megatons,
                "crater_diameter_km": crater_diameter,
                "earthquake_magnitude": earthquake_magnitude,
                "criticality_level": criticality,
                "risk_zones_count": risk_zones_count
            },
            "detailed_simulation": impact_simulation,
            "risk_zones_geojson": risk_zones_geojson
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de simulação: {str(e)}")

@router.get("/report-templates", summary="Listar templates de relatório disponíveis")
def get_report_templates() -> Dict:
    """
    Retorna informações sobre os templates de relatório disponíveis.
    """
    templates = {
        "executive_report": {
            "name": "Relatório Executivo Completo",
            "description": "Relatório PDF completo com análise detalhada, zonas de risco, plano de evacuação e recomendações",
            "format": "PDF",
            "sections": [
                "Resumo Executivo",
                "Informações do Asteroide",
                "Análise de Impacto",
                "Zonas de Risco",
                "Plano de Evacuação",
                "Recomendações",
                "Anexos Técnicos"
            ]
        },
        "simulation_report": {
            "name": "Relatório de Simulação",
            "description": "Relatório JSON com resultados básicos da simulação",
            "format": "JSON",
            "sections": [
                "Resumo da Simulação",
                "Parâmetros de Entrada",
                "Resultados Físicos",
                "Zonas de Risco GeoJSON"
            ]
        }
    }
    
    return {
        "success": True,
        "total_templates": len(templates),
        "templates": templates
    }

@router.get("/report-example", summary="Gerar exemplo de relatório com dados de teste")
def generate_report_example() -> Dict:
    """
    Gera um exemplo de relatório usando dados de teste.
    Útil para demonstrar as funcionalidades do sistema.
    """
    try:
        # Dados de exemplo
        example_request = ReportRequest(
            diameter_m=100,
            velocity_kms=17,
            impact_angle_deg=45,
            target_type="rocha",
            impact_latitude=-23.5505,
            impact_longitude=-46.6333,  # São Paulo
            asteroid_name="Exemplo 2024",
            asteroid_id="2024-TEST",
            is_potentially_hazardous=True,
            evacuation_points=[
                {
                    "name": "Abrigo Central",
                    "type": "shelter",
                    "capacity": 500,
                    "latitude": -23.6000,
                    "longitude": -46.7000
                },
                {
                    "name": "Hospital Municipal",
                    "type": "hospital",
                    "capacity": 200,
                    "latitude": -23.5000,
                    "longitude": -46.6000
                }
            ]
        )
        
        # Gerar relatório de simulação
        simulation_report = generate_simulation_report(example_request)
        
        return {
            "success": True,
            "message": "Exemplo de relatório gerado com sucesso",
            "example_data": example_request.dict(),
            "simulation_report": simulation_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exemplo: {str(e)}")
