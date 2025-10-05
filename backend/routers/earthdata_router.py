from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from services import earthdata_service

router = APIRouter()

class DatasetSearchRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="Termo de busca")
    provider: Optional[str] = Field(default=None, description="Fornecedor dos dados")
    short_name: Optional[str] = Field(default=None, description="Nome curto do conjunto")
    limit: int = Field(default=10, description="Número máximo de resultados")

class DatasetDownloadRequest(BaseModel):
    concept_id: str = Field(..., description="ID do conjunto de dados")
    output_dir: str = Field(default="./data", description="Diretório de saída")
    bbox: Optional[Tuple[float, float, float, float]] = Field(default=None, description="Bounding box (min_lon, min_lat, max_lon, max_lat)")
    start_date: Optional[str] = Field(default=None, description="Data inicial (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="Data final (YYYY-MM-DD)")

class UnifiedDataAccessRequest(BaseModel):
    dataset_type: str = Field(..., description="Tipo de dataset (merra2, gpm_imerg, modis_terra, modis_aqua, tempo)")
    bbox: Tuple[float, float, float, float] = Field(..., description="Bounding box (min_lon, min_lat, max_lon, max_lat)")
    start_date: str = Field(..., description="Data inicial (YYYY-MM-DD)")
    end_date: str = Field(..., description="Data final (YYYY-MM-DD)")

@router.post("/authenticate", summary="Autenticar com Earthdata Login")
def authenticate_earthdata() -> Dict:
    """
    Autentica com Earthdata Login usando credenciais configuradas.
    
    Requer:
    - NASA_EARTHDATA_USERNAME
    - NASA_EARTHDATA_PASSWORD
    
    Configurados como variáveis de ambiente.
    """
    try:
        auth_result = earthdata_service.authenticate()
        return auth_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na autenticação: {str(e)}")

@router.get("/status", summary="Status dos serviços Earthdata")
def get_earthdata_status() -> Dict:
    """
    Retorna status dos serviços Earthdata e disponibilidade.
    """
    try:
        status = earthdata_service.get_service_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.post("/search-datasets", summary="Buscar conjuntos de dados")
def search_datasets(request: DatasetSearchRequest) -> Dict:
    """
    Busca conjuntos de dados disponíveis via CMR (Common Metadata Repository).
    
    Exemplos de busca:
    - Por palavra-chave: "precipitation"
    - Por fornecedor: "GES_DISC"
    - Por nome curto: "M2I1NXASM"
    """
    try:
        search_result = earthdata_service.search_datasets(
            query=request.query,
            provider=request.provider,
            short_name=request.short_name,
            limit=request.limit
        )
        
        return search_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de conjuntos: {str(e)}")

@router.get("/datasets", summary="Listar conjuntos de dados disponíveis")
def get_available_datasets() -> Dict:
    """
    Lista os conjuntos de dados disponíveis no sistema.
    """
    try:
        datasets = earthdata_service.available_datasets
        
        return {
            "success": True,
            "total_datasets": len(datasets),
            "datasets": datasets,
            "data_source": "NASA Earthdata",
            "note": "Conjuntos de dados principais para análise de impacto de asteroides"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter conjuntos: {str(e)}")

@router.get("/granules/{concept_id}", summary="Obter granulos de um conjunto")
def get_dataset_granules(
    concept_id: str,
    min_lon: Optional[float] = Query(default=None, description="Longitude mínima"),
    min_lat: Optional[float] = Query(default=None, description="Latitude mínima"),
    max_lon: Optional[float] = Query(default=None, description="Longitude máxima"),
    max_lat: Optional[float] = Query(default=None, description="Latitude máxima"),
    start_date: Optional[str] = Query(default=None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Data final (YYYY-MM-DD)"),
    limit: int = Query(default=10, description="Número máximo de resultados")
) -> Dict:
    """
    Obtém granulos (arquivos) de um conjunto de dados específico.
    """
    try:
        bbox = None
        if all([min_lon is not None, min_lat is not None, max_lon is not None, max_lat is not None]):
            bbox = (min_lon, min_lat, max_lon, max_lat)
        
        granules_result = earthdata_service.get_dataset_granules(
            concept_id=concept_id,
            bbox=bbox,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return granules_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter granulos: {str(e)}")

@router.post("/download", summary="Baixar conjunto de dados")
def download_dataset(request: DatasetDownloadRequest) -> Dict:
    """
    Baixa conjunto de dados via earthaccess.
    
    Nota: Requer autenticação prévia e earthaccess instalado.
    """
    try:
        download_result = earthdata_service.download_dataset(
            concept_id=request.concept_id,
            output_dir=request.output_dir,
            bbox=request.bbox,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return download_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no download: {str(e)}")

@router.post("/unified-access", summary="Acesso unificado a dados da NASA")
def get_unified_data_access(request: UnifiedDataAccessRequest) -> Dict:
    """
    Acesso unificado a dados da NASA via earthaccess.
    
    Tipos de dataset disponíveis:
    - merra2: Dados atmosféricos de reanálise
    - gpm_imerg: Dados de precipitação
    - modis_terra: Dados de superfície do MODIS Terra
    - modis_aqua: Dados de superfície do MODIS Aqua
    - tempo: Dados de qualidade do ar do TEMPO
    """
    try:
        unified_data = earthdata_service.get_unified_data_access(
            dataset_type=request.dataset_type,
            bbox=request.bbox,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return unified_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no acesso unificado: {str(e)}")

@router.get("/merra2", summary="Obter dados MERRA-2")
def get_merra2_data(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
) -> Dict:
    """
    Obtém dados atmosféricos do MERRA-2 para uma área e período específicos.
    
    Variáveis incluídas:
    - U2M, V2M: Componentes do vento a 2m
    - T2M: Temperatura a 2m
    - SLP: Pressão ao nível do mar
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        merra2_data = earthdata_service.get_unified_data_access(
            dataset_type="merra2",
            bbox=bbox,
            start_date=start_date,
            end_date=end_date
        )
        
        return merra2_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados MERRA-2: {str(e)}")

@router.get("/gpm-imerg", summary="Obter dados GPM IMERG")
def get_gpm_imerg_data(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
) -> Dict:
    """
    Obtém dados de precipitação do GPM IMERG para uma área e período específicos.
    
    Variáveis incluídas:
    - precipitationCal: Precipitação calibrada
    - precipitationUncal: Precipitação não calibrada
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        gpm_data = earthdata_service.get_unified_data_access(
            dataset_type="gpm_imerg",
            bbox=bbox,
            start_date=start_date,
            end_date=end_date
        )
        
        return gpm_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados GPM IMERG: {str(e)}")

@router.get("/modis-terra", summary="Obter dados MODIS Terra")
def get_modis_terra_data(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
) -> Dict:
    """
    Obtém dados de superfície do MODIS Terra para uma área e período específicos.
    
    Variáveis incluídas:
    - sur_refl_b01-b07: Reflectância de superfície em múltiplas bandas
    - NDVI: Índice de vegetação normalizado
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        modis_data = earthdata_service.get_unified_data_access(
            dataset_type="modis_terra",
            bbox=bbox,
            start_date=start_date,
            end_date=end_date
        )
        
        return modis_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados MODIS Terra: {str(e)}")

@router.get("/tempo", summary="Obter dados TEMPO")
def get_tempo_data(
    min_lon: float = Query(..., description="Longitude mínima"),
    min_lat: float = Query(..., description="Latitude mínima"),
    max_lon: float = Query(..., description="Longitude máxima"),
    max_lat: float = Query(..., description="Latitude máxima"),
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)")
) -> Dict:
    """
    Obtém dados de qualidade do ar do TEMPO para uma área e período específicos.
    
    Variáveis incluídas:
    - NO2_AI: Índice de qualidade do ar para NO2
    - Aerosol_Optical_Depth: Profundidade óptica de aerossóis
    """
    try:
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        tempo_data = earthdata_service.get_unified_data_access(
            dataset_type="tempo",
            bbox=bbox,
            start_date=start_date,
            end_date=end_date
        )
        
        return tempo_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados TEMPO: {str(e)}")

@router.get("/data-sources", summary="Listar fontes de dados da NASA")
def get_nasa_data_sources() -> Dict:
    """
    Lista todas as fontes de dados da NASA disponíveis no sistema.
    """
    try:
        nasa_apis = earthdata_service.nasa_apis
        
        return {
            "success": True,
            "total_sources": len(nasa_apis),
            "nasa_apis": nasa_apis,
            "description": "APIs da NASA integradas no sistema",
            "authentication_required": True,
            "note": "Alguns endpoints requerem autenticação Earthdata Login"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter fontes de dados: {str(e)}")
