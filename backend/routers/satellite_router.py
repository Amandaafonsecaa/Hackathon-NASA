from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from services import satellite_imagery_service

router = APIRouter()

class SatelliteImageryRequest(BaseModel):
    layer_type: str = Field(..., description="Tipo de camada (clouds, fires, aerosols, precipitation, temperature, vegetation)")
    bbox: Tuple[float, float, float, float] = Field(..., description="Bounding box (min_lon, min_lat, max_lon, max_lat)")
    date: Optional[str] = Field(default=None, description="Data no formato YYYY-MM-DD")
    format_type: str = Field(default="png", description="Formato da imagem (png, jpg)")
    width: int = Field(default=512, description="Largura da imagem")
    height: int = Field(default=512, description="Altura da imagem")

class MultiLayerAnalysisRequest(BaseModel):
    bbox: Tuple[float, float, float, float] = Field(..., description="Bounding box (min_lon, min_lat, max_lon, max_lat)")
    layers: Optional[List[str]] = Field(default=None, description="Lista de camadas a analisar")
    date: Optional[str] = Field(default=None, description="Data no formato YYYY-MM-DD")

@router.post("/imagery", summary="Obter imagens de satélite")
def get_satellite_imagery(request: SatelliteImageryRequest) -> Dict:
    """
    Obtém imagens de satélite via GIBS + Worldview.
    
    Camadas disponíveis:
    - clouds: Cobertura de nuvens
    - fires: Detecção de incêndios
    - aerosols: Profundidade óptica de aerossóis
    - precipitation: Precipitação
    - temperature: Temperatura
    - vegetation: Índice de vegetação
    """
    try:
        imagery_data = satellite_imagery_service.get_satellite_imagery(
            layer_type=request.layer_type,
            bbox=request.bbox,
            date=request.date,
            format_type=request.format_type,
            width=request.width,
            height=request.height
        )
        
        return imagery_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter imagens de satélite: {str(e)}")

@router.post("/multi-layer-analysis", summary="Análise multi-camada")
def get_multi_layer_analysis(request: MultiLayerAnalysisRequest) -> Dict:
    """
    Obtém análise combinada de múltiplas camadas de satélite.
    
    Útil para:
    - Avaliar condições gerais da área
    - Identificar fatores que afetam evacuação
    - Detectar riscos ambientais
    - Gerar recomendações operacionais
    """
    try:
        analysis_data = satellite_imagery_service.get_multi_layer_analysis(
            bbox=request.bbox,
            layers=request.layers,
            date=request.date
        )
        
        return analysis_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise multi-camada: {str(e)}")

@router.get("/layers", summary="Listar camadas disponíveis")
def get_available_layers() -> Dict:
    """
    Retorna informações sobre as camadas de satélite disponíveis.
    """
    try:
        layers_info = satellite_imagery_service.get_available_layers()
        return layers_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter camadas: {str(e)}")

@router.get("/clouds", summary="Obter dados de cobertura de nuvens")
def get_cloud_cover(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de cobertura de nuvens para uma área específica.
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        cloud_data = satellite_imagery_service.get_satellite_imagery(
            layer_type="clouds",
            bbox=bbox,
            date=date
        )
        
        return cloud_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de nuvens: {str(e)}")

@router.get("/fires", summary="Obter dados de detecção de incêndios")
def get_fire_detection(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de detecção de incêndios para uma área específica.
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        fire_data = satellite_imagery_service.get_satellite_imagery(
            layer_type="fires",
            bbox=bbox,
            date=date
        )
        
        return fire_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de incêndios: {str(e)}")

@router.get("/precipitation", summary="Obter dados de precipitação")
def get_precipitation_data(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de precipitação por satélite para uma área específica.
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        precip_data = satellite_imagery_service.get_satellite_imagery(
            layer_type="precipitation",
            bbox=bbox,
            date=date
        )
        
        return precip_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de precipitação: {str(e)}")

@router.get("/evacuation-conditions", summary="Avaliar condições de evacuação")
def assess_evacuation_conditions(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Avalia condições de evacuação baseadas em dados de satélite.
    
    Considera:
    - Cobertura de nuvens (visibilidade)
    - Precipitação (condições de estrada)
    - Incêndios ativos (obstáculos)
    - Aerossóis (qualidade do ar)
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        # Análise multi-camada focada em evacuação
        evacuation_layers = ["clouds", "precipitation", "fires", "aerosols"]
        
        analysis_data = satellite_imagery_service.get_multi_layer_analysis(
            bbox=bbox,
            layers=evacuation_layers,
            date=date
        )
        
        if analysis_data.get("success"):
            combined_analysis = analysis_data.get("combined_analysis", {})
            
            # Extrair informações específicas para evacuação
            evacuation_assessment = {
                "evacuation_feasibility": combined_analysis.get("evacuation_factors", {}).get("difficulty_level", "Unknown"),
                "evacuation_score": combined_analysis.get("evacuation_factors", {}).get("evacuation_difficulty_score", 0),
                "visibility_conditions": combined_analysis.get("overall_conditions", {}).get("visibility", "Unknown"),
                "weather_conditions": combined_analysis.get("overall_conditions", {}).get("weather", "Unknown"),
                "environmental_risks": combined_analysis.get("environmental_risks", []),
                "recommendations": combined_analysis.get("recommendations", []),
                "factors": combined_analysis.get("evacuation_factors", {}).get("factors", [])
            }
            
            analysis_data["evacuation_assessment"] = evacuation_assessment
        
        return analysis_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na avaliação de evacuação: {str(e)}")
