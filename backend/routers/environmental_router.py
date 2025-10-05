from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from services import usgs_service, atmospheric_service, air_quality_service

router = APIRouter()

class EnvironmentalAnalysisRequest(BaseModel):
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    buffer_km: float = Field(default=10, description="Raio da área em km")
    date: Optional[str] = Field(default=None, description="Data no formato YYYY-MM-DD")

@router.post("/comprehensive-analysis", summary="Análise ambiental abrangente")
def comprehensive_environmental_analysis(request: EnvironmentalAnalysisRequest) -> Dict:
    """
    Realiza análise ambiental abrangente incluindo:
    - Dados de elevação e topografia
    - Condições atmosféricas
    - Qualidade do ar
    - Dados geológicos
    """
    try:
        # Obter dados de elevação
        elevation_data = usgs_service.get_elevation_data(
            request.latitude, 
            request.longitude, 
            request.buffer_km
        )
        
        # Obter dados atmosféricos
        atmospheric_data = atmospheric_service.get_merra2_data(
            request.latitude, 
            request.longitude, 
            request.date
        )
        
        # Obter dados de precipitação
        precipitation_data = atmospheric_service.get_gpm_precipitation(
            request.latitude, 
            request.longitude, 
            request.date
        )
        
        # Obter dados de qualidade do ar
        air_quality_data = air_quality_service.get_airnow_data(
            request.latitude, 
            request.longitude, 
            request.date
        )
        
        # Obter dados geológicos
        geologic_data = usgs_service.get_geologic_data(
            request.latitude, 
            request.longitude, 
            request.buffer_km
        )
        
        return {
            "success": True,
            "coordinates": [request.longitude, request.latitude],
            "buffer_km": request.buffer_km,
            "date": request.date,
            "elevation_data": elevation_data,
            "atmospheric_data": atmospheric_data,
            "precipitation_data": precipitation_data,
            "air_quality_data": air_quality_data,
            "geologic_data": geologic_data,
            "analysis_timestamp": atmospheric_service.get_current_timestamp()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise ambiental: {str(e)}")

@router.get("/elevation", summary="Obter dados de elevação")
def get_elevation_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    buffer_km: float = Query(default=5, description="Raio da área em km")
) -> Dict:
    """
    Obtém dados de elevação e análise topográfica para uma localização.
    """
    try:
        elevation_data = usgs_service.get_elevation_data(latitude, longitude, buffer_km)
        return elevation_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de elevação: {str(e)}")

@router.get("/geology", summary="Obter dados geológicos")
def get_geologic_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    buffer_km: float = Query(default=5, description="Raio da área em km")
) -> Dict:
    """
    Obtém dados geológicos para uma localização.
    """
    try:
        geologic_data = usgs_service.get_geologic_data(latitude, longitude, buffer_km)
        return geologic_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados geológicos: {str(e)}")

@router.post("/tsunami-analysis", summary="Análise de impacto de tsunami")
def analyze_tsunami_impact(
    latitude: float = Query(..., description="Latitude do ponto de impacto"),
    longitude: float = Query(..., description="Longitude do ponto de impacto"),
    tsunami_height_m: float = Query(..., description="Altura estimada do tsunami em metros")
) -> Dict:
    """
    Analisa o impacto de tsunami baseado na topografia local.
    """
    try:
        tsunami_analysis = usgs_service.analyze_tsunami_impact_terrain(
            latitude, longitude, tsunami_height_m
        )
        return tsunami_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de tsunami: {str(e)}")

@router.get("/atmospheric/wind", summary="Obter dados de vento")
def get_wind_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de vento e condições atmosféricas.
    """
    try:
        atmospheric_data = atmospheric_service.get_merra2_data(latitude, longitude, date)
        
        if atmospheric_data.get("success"):
            wind_data = atmospheric_data["data"]
            return {
                "success": True,
                "coordinates": [longitude, latitude],
                "date": date,
                "wind_data": {
                    "wind_speed_ms": wind_data.get("WIND_SPEED", {}).get("value", 0),
                    "wind_direction_deg": wind_data.get("WIND_DIRECTION", {}).get("value", 0),
                    "u_component_ms": wind_data.get("U2M", {}).get("value", 0),
                    "v_component_ms": wind_data.get("V2M", {}).get("value", 0)
                }
            }
        else:
            return atmospheric_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de vento: {str(e)}")

@router.get("/atmospheric/temperature", summary="Obter dados de temperatura")
def get_temperature_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    date: str = Query(default=None, description="Data no formato YYYY-MM-DD")
) -> Dict:
    """
    Obtém dados de temperatura e pressão atmosférica.
    """
    try:
        atmospheric_data = atmospheric_service.get_merra2_data(latitude, longitude, date)
        
        if atmospheric_data.get("success"):
            temp_data = atmospheric_data["data"]
            return {
                "success": True,
                "coordinates": [longitude, latitude],
                "date": date,
                "temperature_data": {
                    "temperature_2m_c": temp_data.get("T2M", {}).get("value", 0),
                    "sea_level_pressure_hpa": temp_data.get("SLP", {}).get("value", 0)
                }
            }
        else:
            return atmospheric_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados de temperatura: {str(e)}")

@router.get("/data-sources", summary="Listar fontes de dados ambientais")
def get_environmental_data_sources() -> Dict:
    """
    Retorna informações sobre as fontes de dados ambientais disponíveis.
    """
    data_sources = {
        "elevation": {
            "source": "USGS National Map",
            "description": "Modelos de elevação digital (DEM) de alta resolução",
            "coverage": "Estados Unidos",
            "resolution": "1-30 metros",
            "update_frequency": "Anual"
        },
        "geology": {
            "source": "USGS Geologic Map Service",
            "description": "Dados geológicos e mapas de unidades rochosas",
            "coverage": "Estados Unidos",
            "resolution": "1:100,000 a 1:1,000,000",
            "update_frequency": "Conforme necessário"
        },
        "atmospheric": {
            "source": "MERRA-2 Reanalysis",
            "description": "Dados atmosféricos de reanálise (vento, temperatura, pressão)",
            "coverage": "Global",
            "resolution": "0.5° x 0.625°",
            "update_frequency": "Diário"
        },
        "precipitation": {
            "source": "GPM IMERG",
            "description": "Dados de precipitação por satélite",
            "coverage": "Global",
            "resolution": "0.1° x 0.1°",
            "update_frequency": "Quase tempo real"
        },
        "air_quality": {
            "source": "AirNow / OpenAQ",
            "description": "Dados de qualidade do ar de estações terrestres",
            "coverage": "América do Norte / Global",
            "resolution": "Pontual",
            "update_frequency": "Tempo real"
        }
    }
    
    return {
        "success": True,
        "total_sources": len(data_sources),
        "data_sources": data_sources,
        "note": "Alguns dados são simulados para demonstração. Em produção, usar dados reais das APIs."
    }
