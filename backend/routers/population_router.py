from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from services import population_service

router = APIRouter()

class PopulationAnalysisRequest(BaseModel):
    lat: float = Field(..., description="Latitude do centro da análise")
    lon: float = Field(..., description="Longitude do centro da análise")
    radius_km: float = Field(default=50, description="Raio da região em km")

class PopulationDensityMapRequest(BaseModel):
    bbox: Tuple[float, float, float, float] = Field(..., description="Bounding box (min_lon, min_lat, max_lon, max_lat)")
    resolution: int = Field(default=10, description="Resolução da grade (pontos por lado)")

@router.post("/region-analysis", summary="Análise demográfica de uma região")
def get_population_analysis(request: PopulationAnalysisRequest) -> Dict:
    """
    Obtém análise demográfica completa para uma região específica.
    
    Inclui:
    - Densidade populacional
    - Distribuição etária
    - Cidades próximas
    - Avaliação de vulnerabilidade
    - Análise de capacidade de evacuação
    """
    try:
        analysis = population_service.get_population_by_region(
            lat=request.lat,
            lon=request.lon,
            radius_km=request.radius_km
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise demográfica: {str(e)}")

@router.get("/region-analysis", summary="Análise demográfica de uma região (GET)")
def get_population_analysis_get(
    lat: float = Query(..., description="Latitude do centro da análise"),
    lon: float = Query(..., description="Longitude do centro da análise"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Obtém análise demográfica completa para uma região específica.
    """
    try:
        analysis = population_service.get_population_by_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise demográfica: {str(e)}")

@router.post("/density-map", summary="Gerar mapa de densidade populacional")
def get_population_density_map(request: PopulationDensityMapRequest) -> Dict:
    """
    Gera mapa de densidade populacional para uma área específica.
    
    Útil para:
    - Visualização de distribuição populacional
    - Identificação de áreas de alta densidade
    - Planejamento de evacuação
    - Análise de risco demográfico
    """
    try:
        density_map = population_service.get_population_density_map(
            bbox=request.bbox,
            resolution=request.resolution
        )
        
        return density_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mapa de densidade: {str(e)}")

@router.get("/density-map", summary="Gerar mapa de densidade populacional (GET)")
def get_population_density_map_get(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    resolution: int = Query(default=10, description="Resolução da grade (pontos por lado)")
) -> Dict:
    """
    Gera mapa de densidade populacional para uma área específica.
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        density_map = population_service.get_population_density_map(
            bbox=bbox,
            resolution=resolution
        )
        
        return density_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mapa de densidade: {str(e)}")

@router.get("/evacuation-capacity", summary="Análise de capacidade de evacuação")
def get_evacuation_capacity_analysis(
    lat: float = Query(..., description="Latitude do centro da análise"),
    lon: float = Query(..., description="Longitude do centro da análise"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Analisa capacidade de evacuação baseada na população local.
    
    Inclui:
    - Estimativa de veículos disponíveis
    - Capacidade total de transporte
    - Tempo estimado de evacuação
    - Viabilidade da evacuação
    - Recomendações específicas
    """
    try:
        capacity_analysis = population_service.get_evacuation_capacity_analysis(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        return capacity_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de capacidade: {str(e)}")

@router.get("/vulnerability-assessment", summary="Avaliação de vulnerabilidade populacional")
def get_vulnerability_assessment(
    lat: float = Query(..., description="Latitude do centro da análise"),
    lon: float = Query(..., description="Longitude do centro da análise"),
    radius_km: float = Query(default=50, description="Raio da região em km")
) -> Dict:
    """
    Avalia vulnerabilidade da população local.
    
    Considera:
    - Distribuição etária (crianças e idosos)
    - Densidade populacional
    - Acesso a serviços essenciais
    - Capacidade de evacuação
    - Necessidades especiais
    """
    try:
        # Obter análise demográfica
        pop_analysis = population_service.get_population_by_region(
            lat=lat,
            lon=lon,
            radius_km=radius_km
        )
        
        if not pop_analysis.get("success"):
            return pop_analysis
        
        # Extrair informações de vulnerabilidade
        vulnerability_data = pop_analysis.get("vulnerability_assessment", {})
        
        return {
            "success": True,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "vulnerability_assessment": vulnerability_data,
            "demographic_data": pop_analysis.get("demographics", {}),
            "nearby_cities": pop_analysis.get("nearby_cities", []),
            "recommendations": vulnerability_data.get("special_needs", {}),
            "assessment_timestamp": pop_analysis.get("data_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na avaliação de vulnerabilidade: {str(e)}")

@router.get("/demographic-statistics", summary="Estatísticas demográficas globais")
def get_demographic_statistics() -> Dict:
    """
    Obtém estatísticas demográficas globais por região.
    
    Inclui dados de:
    - América do Norte
    - Europa
    - Ásia
    - Distribuição etária global
    - Densidade populacional por região
    """
    try:
        # Obter dados simulados das regiões
        regions_data = population_service.simulated_population_data
        
        global_stats = {
            "total_population": sum([region["total_population"] for region in regions_data.values()]),
            "regions": {}
        }
        
        for region_name, region_data in regions_data.items():
            global_stats["regions"][region_name] = {
                "total_population": region_data["total_population"],
                "density_per_km2": region_data["density_per_km2"],
                "age_distribution": region_data["age_distribution"],
                "major_cities_count": len(region_data["major_cities"])
            }
        
        # Calcular estatísticas globais
        global_stats["global_age_distribution"] = {
            "0-14": sum([region["age_distribution"]["0-14"] * region["total_population"] for region in regions_data.values()]) / global_stats["total_population"],
            "15-64": sum([region["age_distribution"]["15-64"] * region["total_population"] for region in regions_data.values()]) / global_stats["total_population"],
            "65+": sum([region["age_distribution"]["65+"] * region["total_population"] for region in regions_data.values()]) / global_stats["total_population"]
        }
        
        return {
            "success": True,
            "global_statistics": global_stats,
            "data_source": "Simulated Global Demographics",
            "note": "Dados simulados para demonstração. Em produção, usar dados reais de censo.",
            "generated_at": population_service.get_population_by_region(0, 0, 1).get("data_timestamp")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas demográficas: {str(e)}")
