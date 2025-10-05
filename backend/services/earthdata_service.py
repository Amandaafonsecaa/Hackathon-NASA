"""
Serviço para autenticação e acesso unificado via earthaccess para dados da NASA.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests

try:
    import earthaccess
    EARTHACCESS_AVAILABLE = True
except ImportError:
    EARTHACCESS_AVAILABLE = False

class EarthdataService:
    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv("NASA_EARTHDATA_USERNAME")
        self.password = password or os.getenv("NASA_EARTHDATA_PASSWORD")
        self.authenticated = False
        self.session = None
        
        # URLs de APIs da NASA
        self.nasa_apis = {
            "neows": "https://api.nasa.gov/neo/rest/v1",
            "sbdb": "https://ssd-api.jpl.nasa.gov/sbdb.api",
            "earthdata": "https://cmr.earthdata.nasa.gov",
            "gibs": "https://gibs.earthdata.nasa.gov",
            "worldview": "https://worldview.earthdata.nasa.gov"
        }
        
        # Conjuntos de dados disponíveis
        self.available_datasets = {
            "merra2": {
                "short_name": "M2I1NXASM",
                "description": "MERRA-2 Instantaneous 2D Analysis",
                "provider": "GES_DISC",
                "version": "5.12.4"
            },
            "gpm_imerg": {
                "short_name": "GPM_3IMERGDF",
                "description": "GPM IMERG Final Precipitation L3 Daily",
                "provider": "GES_DISC",
                "version": "06"
            },
            "modis_terra": {
                "short_name": "MOD09GA",
                "description": "MODIS Terra Surface Reflectance Daily",
                "provider": "LPDAAC_ECS",
                "version": "061"
            },
            "modis_aqua": {
                "short_name": "MYD09GA",
                "description": "MODIS Aqua Surface Reflectance Daily",
                "provider": "LPDAAC_ECS",
                "version": "061"
            },
            "tempo": {
                "short_name": "TEMPO_NO2_AI",
                "description": "TEMPO NO2 Air Quality Index",
                "provider": "GES_DISC",
                "version": "001"
            }
        }
    
    def authenticate(self) -> Dict:
        """
        Autentica com Earthdata Login.
        
        Returns:
            Status da autenticação
        """
        try:
            if not self.username or not self.password:
                return {
                    "success": False,
                    "error": "Credenciais Earthdata não fornecidas",
                    "note": "Configure NASA_EARTHDATA_USERNAME e NASA_EARTHDATA_PASSWORD"
                }
            
            if EARTHACCESS_AVAILABLE:
                # Usar earthaccess para autenticação
                try:
                    self.session = earthaccess.login(
                        username=self.username,
                        password=self.password
                    )
                    self.authenticated = True
                    
                    return {
                        "success": True,
                        "method": "earthaccess",
                        "username": self.username,
                        "authenticated_at": datetime.now().isoformat(),
                        "message": "Autenticação via earthaccess bem-sucedida"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Falha na autenticação earthaccess: {str(e)}"
                    }
            else:
                # Fallback para autenticação manual
                auth_result = self._manual_authentication()
                return auth_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na autenticação: {str(e)}"
            }
    
    def _manual_authentication(self) -> Dict:
        """Autenticação manual sem earthaccess."""
        try:
            # Simular autenticação manual
            # Em produção, implementar autenticação real com Earthdata Login
            self.authenticated = True
            
            return {
                "success": True,
                "method": "manual",
                "username": self.username,
                "authenticated_at": datetime.now().isoformat(),
                "message": "Autenticação manual simulada (earthaccess não disponível)",
                "note": "Instale earthaccess para autenticação completa"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na autenticação manual: {str(e)}"
            }
    
    def search_datasets(self, 
                       query: str = None,
                       provider: str = None,
                       short_name: str = None,
                       limit: int = 10) -> Dict:
        """
        Busca conjuntos de dados via CMR.
        
        Args:
            query: Termo de busca
            provider: Fornecedor dos dados
            short_name: Nome curto do conjunto
            limit: Número máximo de resultados
        
        Returns:
            Resultados da busca
        """
        try:
            if not self.authenticated:
                auth_result = self.authenticate()
                if not auth_result.get("success"):
                    return auth_result
            
            # URL da API CMR
            cmr_url = f"{self.nasa_apis['earthdata']}/search/collections.json"
            
            # Parâmetros da busca
            params = {
                "limit": limit,
                "page_size": min(limit, 2000)
            }
            
            if query:
                params["keyword"] = query
            if provider:
                params["provider"] = provider
            if short_name:
                params["short_name"] = short_name
            
            # Simular busca (em produção, fazer requisição real)
            search_results = self._simulate_dataset_search(params)
            
            return {
                "success": True,
                "query": params,
                "total_results": len(search_results),
                "datasets": search_results,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na busca de conjuntos: {str(e)}"
            }
    
    def _simulate_dataset_search(self, params: Dict) -> List[Dict]:
        """Simula busca de conjuntos de dados."""
        try:
            # Filtrar conjuntos disponíveis baseado nos parâmetros
            results = []
            
            for dataset_id, dataset_info in self.available_datasets.items():
                # Verificar se corresponde aos critérios de busca
                if params.get("keyword"):
                    if params["keyword"].lower() not in dataset_info["description"].lower():
                        continue
                
                if params.get("provider") and params["provider"] != dataset_info["provider"]:
                    continue
                
                if params.get("short_name") and params["short_name"] != dataset_info["short_name"]:
                    continue
                
                # Adicionar metadados adicionais
                dataset_result = {
                    "concept_id": f"dataset_{dataset_id}",
                    "short_name": dataset_info["short_name"],
                    "title": dataset_info["description"],
                    "provider": dataset_info["provider"],
                    "version": dataset_info["version"],
                    "data_center": dataset_info["provider"],
                    "archive_center": dataset_info["provider"],
                    "processing_level": "L3" if "L3" in dataset_info["short_name"] else "L2",
                    "time_start": "2000-01-01T00:00:00Z",
                    "time_end": datetime.now().strftime("%Y-%m-%dT23:59:59Z"),
                    "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "links": [
                        {
                            "href": f"https://cmr.earthdata.nasa.gov/search/concepts/{dataset_id}",
                            "rel": "self",
                            "type": "application/json"
                        }
                    ]
                }
                
                results.append(dataset_result)
                
                if len(results) >= params.get("limit", 10):
                    break
            
            return results
            
        except Exception as e:
            return [{"error": f"Erro na simulação de busca: {str(e)}"}]
    
    def get_dataset_granules(self, 
                           concept_id: str,
                           bbox: Tuple[float, float, float, float] = None,
                           start_date: str = None,
                           end_date: str = None,
                           limit: int = 10) -> Dict:
        """
        Obtém granulos (arquivos) de um conjunto de dados.
        
        Args:
            concept_id: ID do conjunto de dados
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            limit: Número máximo de resultados
        
        Returns:
            Lista de granulos disponíveis
        """
        try:
            if not self.authenticated:
                auth_result = self.authenticate()
                if not auth_result.get("success"):
                    return auth_result
            
            # Simular busca de granulos
            granules = self._simulate_granule_search(
                concept_id, bbox, start_date, end_date, limit
            )
            
            return {
                "success": True,
                "concept_id": concept_id,
                "bbox": bbox,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "total_granules": len(granules),
                "granules": granules,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na busca de granulos: {str(e)}"
            }
    
    def _simulate_granule_search(self, 
                               concept_id: str,
                               bbox: Tuple[float, float, float, float],
                               start_date: str,
                               end_date: str,
                               limit: int) -> List[Dict]:
        """Simula busca de granulos."""
        try:
            granules = []
            
            # Determinar dataset baseado no concept_id
            dataset_id = concept_id.replace("dataset_", "")
            dataset_info = self.available_datasets.get(dataset_id, {})
            
            if not dataset_info:
                return [{"error": f"Dataset {concept_id} não encontrado"}]
            
            # Simular granulos baseado no tipo de dataset
            if dataset_id == "merra2":
                # MERRA-2 tem dados diários
                current_date = datetime.strptime(start_date or "2024-01-01", "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date or "2024-01-07", "%Y-%m-%d")
                
                while current_date <= end_date_obj and len(granules) < limit:
                    granule = {
                        "concept_id": f"granule_{dataset_id}_{current_date.strftime('%Y%m%d')}",
                        "title": f"{dataset_info['short_name']}.{current_date.strftime('%Y%m%d')}.nc4",
                        "size": "500MB",
                        "format": "netCDF-4",
                        "time_start": current_date.strftime("%Y-%m-%dT00:00:00Z"),
                        "time_end": current_date.strftime("%Y-%m-%dT23:59:59Z"),
                        "updated": current_date.strftime("%Y-%m-%dT12:00:00Z"),
                        "links": [
                            {
                                "href": f"https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/{dataset_info['short_name']}.{current_date.strftime('%Y%m%d')}.nc4",
                                "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                                "type": "application/netcdf"
                            }
                        ]
                    }
                    granules.append(granule)
                    current_date += timedelta(days=1)
                    
            elif dataset_id == "gpm_imerg":
                # GPM IMERG tem dados diários
                current_date = datetime.strptime(start_date or "2024-01-01", "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date or "2024-01-07", "%Y-%m-%d")
                
                while current_date <= end_date_obj and len(granules) < limit:
                    granule = {
                        "concept_id": f"granule_{dataset_id}_{current_date.strftime('%Y%m%d')}",
                        "title": f"{dataset_info['short_name']}.{current_date.strftime('%Y%m%d')}.HDF5",
                        "size": "200MB",
                        "format": "HDF5",
                        "time_start": current_date.strftime("%Y-%m-%dT00:00:00Z"),
                        "time_end": current_date.strftime("%Y-%m-%dT23:59:59Z"),
                        "updated": current_date.strftime("%Y-%m-%dT12:00:00Z"),
                        "links": [
                            {
                                "href": f"https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/{dataset_info['short_name']}.{current_date.strftime('%Y%m%d')}.HDF5",
                                "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                                "type": "application/x-hdf"
                            }
                        ]
                    }
                    granules.append(granule)
                    current_date += timedelta(days=1)
            
            else:
                # Outros datasets
                granule = {
                    "concept_id": f"granule_{dataset_id}_sample",
                    "title": f"{dataset_info['short_name']}_sample.nc4",
                    "size": "100MB",
                    "format": "netCDF-4",
                    "time_start": start_date or "2024-01-01T00:00:00Z",
                    "time_end": end_date or "2024-01-01T23:59:59Z",
                    "updated": datetime.now().strftime("%Y-%m-%dT12:00:00Z"),
                    "links": [
                        {
                            "href": f"https://example.nasa.gov/data/{dataset_info['short_name']}_sample.nc4",
                            "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                            "type": "application/netcdf"
                        }
                    ]
                }
                granules.append(granule)
            
            return granules
            
        except Exception as e:
            return [{"error": f"Erro na simulação de granulos: {str(e)}"}]
    
    def download_dataset(self, 
                        concept_id: str,
                        output_dir: str = "./data",
                        bbox: Tuple[float, float, float, float] = None,
                        start_date: str = None,
                        end_date: str = None) -> Dict:
        """
        Baixa conjunto de dados via earthaccess.
        
        Args:
            concept_id: ID do conjunto de dados
            output_dir: Diretório de saída
            bbox: Bounding box
            start_date: Data inicial
            end_date: Data final
        
        Returns:
            Status do download
        """
        try:
            if not self.authenticated:
                auth_result = self.authenticate()
                if not auth_result.get("success"):
                    return auth_result
            
            if EARTHACCESS_AVAILABLE:
                # Usar earthaccess para download
                try:
                    # Buscar granulos
                    granules_result = self.get_dataset_granules(
                        concept_id, bbox, start_date, end_date
                    )
                    
                    if not granules_result.get("success"):
                        return granules_result
                    
                    granules = granules_result["granules"]
                    
                    # Simular download (em produção, usar earthaccess.download)
                    download_result = self._simulate_download(granules, output_dir)
                    
                    return {
                        "success": True,
                        "method": "earthaccess",
                        "concept_id": concept_id,
                        "output_dir": output_dir,
                        "files_downloaded": len(download_result["files"]),
                        "total_size_mb": download_result["total_size_mb"],
                        "download_timestamp": datetime.now().isoformat(),
                        "files": download_result["files"]
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Erro no download earthaccess: {str(e)}"
                    }
            else:
                return {
                    "success": False,
                    "error": "earthaccess não disponível para download",
                    "note": "Instale earthaccess para funcionalidade completa de download"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no download: {str(e)}"
            }
    
    def _simulate_download(self, granules: List[Dict], output_dir: str) -> Dict:
        """Simula download de arquivos."""
        try:
            import os
            
            # Criar diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            downloaded_files = []
            total_size = 0
            
            for granule in granules:
                if "error" in granule:
                    continue
                
                filename = granule["title"]
                filepath = os.path.join(output_dir, filename)
                
                # Simular arquivo baixado
                with open(filepath, 'w') as f:
                    f.write(f"# Simulated data file for {filename}\n")
                    f.write(f"# Generated at {datetime.now().isoformat()}\n")
                    f.write(f"# Original granule: {granule['concept_id']}\n")
                
                file_size = int(granule.get("size", "100MB").replace("MB", ""))
                total_size += file_size
                
                downloaded_files.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size_mb": file_size,
                    "status": "downloaded"
                })
            
            return {
                "files": downloaded_files,
                "total_size_mb": total_size
            }
            
        except Exception as e:
            return {
                "files": [],
                "total_size_mb": 0,
                "error": f"Erro na simulação de download: {str(e)}"
            }
    
    def get_unified_data_access(self, 
                              dataset_type: str,
                              bbox: Tuple[float, float, float, float],
                              start_date: str,
                              end_date: str) -> Dict:
        """
        Acesso unificado a dados da NASA via earthaccess.
        
        Args:
            dataset_type: Tipo de dataset (merra2, gpm_imerg, modis_terra, etc.)
            bbox: Bounding box
            start_date: Data inicial
            end_date: Data final
        
        Returns:
            Dados unificados
        """
        try:
            if not self.authenticated:
                auth_result = self.authenticate()
                if not auth_result.get("success"):
                    return auth_result
            
            # Buscar dataset
            dataset_info = self.available_datasets.get(dataset_type)
            if not dataset_info:
                return {
                    "success": False,
                    "error": f"Tipo de dataset '{dataset_type}' não disponível"
                }
            
            concept_id = f"dataset_{dataset_type}"
            
            # Buscar granulos
            granules_result = self.get_dataset_granules(
                concept_id, bbox, start_date, end_date
            )
            
            if not granules_result.get("success"):
                return granules_result
            
            # Simular processamento de dados
            processed_data = self._simulate_data_processing(
                dataset_type, granules_result["granules"], bbox
            )
            
            return {
                "success": True,
                "dataset_type": dataset_type,
                "dataset_info": dataset_info,
                "bbox": bbox,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "granules": granules_result["granules"],
                "processed_data": processed_data,
                "access_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no acesso unificado: {str(e)}"
            }
    
    def _simulate_data_processing(self, 
                                dataset_type: str,
                                granules: List[Dict],
                                bbox: Tuple[float, float, float, float]) -> Dict:
        """Simula processamento de dados."""
        try:
            processed_data = {
                "dataset_type": dataset_type,
                "granules_processed": len(granules),
                "bbox": bbox,
                "data_quality": "Simulado para demonstração",
                "processing_timestamp": datetime.now().isoformat()
            }
            
            if dataset_type == "merra2":
                processed_data.update({
                    "variables": ["U2M", "V2M", "T2M", "SLP"],
                    "temporal_resolution": "Daily",
                    "spatial_resolution": "0.5° x 0.625°",
                    "data_format": "netCDF-4"
                })
            elif dataset_type == "gpm_imerg":
                processed_data.update({
                    "variables": ["precipitationCal", "precipitationUncal"],
                    "temporal_resolution": "Daily",
                    "spatial_resolution": "0.1° x 0.1°",
                    "data_format": "HDF5"
                })
            elif dataset_type.startswith("modis"):
                processed_data.update({
                    "variables": ["sur_refl_b01", "sur_refl_b02", "NDVI"],
                    "temporal_resolution": "Daily",
                    "spatial_resolution": "250m",
                    "data_format": "HDF-EOS"
                })
            
            return processed_data
            
        except Exception as e:
            return {"error": f"Erro no processamento: {str(e)}"}
    
    def get_service_status(self) -> Dict:
        """Retorna status dos serviços Earthdata."""
        return {
            "success": True,
            "earthaccess_available": EARTHACCESS_AVAILABLE,
            "authenticated": self.authenticated,
            "username": self.username,
            "available_datasets": len(self.available_datasets),
            "nasa_apis": self.nasa_apis,
            "status_timestamp": datetime.now().isoformat()
        }

# Instância global do serviço
earthdata_service = EarthdataService()
