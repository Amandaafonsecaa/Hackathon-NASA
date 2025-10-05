import requests
from core.config import settings
from typing import Dict, Optional

class NasaService:
    def __init__(self):
        self.api_key = getattr(settings, 'NASA_API_KEY', 'DEMO_KEY')
        self.base_url = "https://api.nasa.gov/neo/rest/v1/neo/"

    def get_neo_data(self, asteroid_id: str) -> dict | None:
        """Busca dados básicos de um asteroide via NASA NeoWs API"""
        params = {"api_key": self.api_key}
        try:
            response = requests.get(f"{self.base_url}{asteroid_id}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados NEO: {e}")
            return None

    def get_sbdb_data(self, asteroid_id: str) -> dict | None:
        """Busca dados orbitais precisos via JPL SBDB"""
        try:
            response = requests.get(f"https://ssd-api.jpl.nasa.gov/sbdb.api", 
                                  params={"des": asteroid_id})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados SBDB: {e}")
            return None

    def get_enhanced_asteroid_data(self, asteroid_id: str) -> dict | None:
        """Combina dados do NeoWs e SBDB"""
        try:
            neows_data = self.get_neo_data(asteroid_id)
            sbdb_data = self.get_sbdb_data(asteroid_id)
            
            if not neows_data:
                return None
            
            enhanced_data = {
                "basic_info": neows_data,
                "orbital_data": sbdb_data,
                "data_sources": {
                    "neows": "NASA Near Earth Object Web Service",
                    "sbdb": "JPL Small-Body Database" if sbdb_data else None
                }
            }
            
            return enhanced_data
            
        except Exception as e:
            print(f"Erro ao combinar dados do asteroide: {e}")
            return None

# Instância global do serviço
nasa_service = NasaService()