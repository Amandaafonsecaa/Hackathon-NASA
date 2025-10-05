import requests
from core.config import settings
from typing import Dict, Optional

NASA_API_URL = "https://api.nasa.gov/neo/rest/v1/neo/"
SBDB_API_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"

def get_neo_data(asteroid_id: str) -> dict | None:
    """Busca dados básicos de um asteroide via NASA NeoWs API"""
    params = {"api_key": settings.NASA_API_KEY}
    try:
        response = requests.get(f"{NASA_API_URL}{asteroid_id}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API da NASA: {e}")
        return None

def get_sbdb_data(asteroid_id: str) -> Dict | None:
    """
    Busca dados orbitais precisos via JPL Small-Body Database (SBDB).
    Retorna parâmetros orbitais, físicos e de classificação.
    """
    try:
        # SBDB não requer API key, mas tem rate limiting
        response = requests.get(f"{SBDB_API_URL}", params={
            "des": asteroid_id,
            "sb-data": "all"
        })
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != "200":
            print(f"Erro na resposta do SBDB: {data.get('message', 'Erro desconhecido')}")
            return None
        
        return _parse_sbdb_data(data)
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API do SBDB: {e}")
        return None

def _parse_sbdb_data(sbdb_response: Dict) -> Dict:
    """Extrai e formata dados relevantes da resposta do SBDB"""
    try:
        data = sbdb_response.get("data", {})
        orbital_data = data.get("orbital_data", {})
        physical_data = data.get("physical_data", {})
        
        # Extrair parâmetros orbitais
        orbital_params = {
            "semimajor_axis_au": orbital_data.get("semimajor_axis", {}).get("value"),
            "eccentricity": orbital_data.get("eccentricity", {}).get("value"),
            "inclination_deg": orbital_data.get("inclination", {}).get("value"),
            "perihelion_distance_au": orbital_data.get("perihelion_distance", {}).get("value"),
            "aphelion_distance_au": orbital_data.get("aphelion_distance", {}).get("value"),
            "orbital_period_days": orbital_data.get("period", {}).get("value"),
            "perihelion_date": orbital_data.get("perihelion_date", {}).get("value"),
            "mean_anomaly_deg": orbital_data.get("mean_anomaly", {}).get("value"),
            "argument_of_perihelion_deg": orbital_data.get("argument_of_perihelion", {}).get("value"),
            "longitude_of_ascending_node_deg": orbital_data.get("longitude_of_ascending_node", {}).get("value")
        }
        
        # Extrair parâmetros físicos
        physical_params = {
            "diameter_km": physical_data.get("diameter", {}).get("value"),
            "diameter_uncertainty_km": physical_data.get("diameter", {}).get("uncertainty"),
            "rotation_period_hours": physical_data.get("rot_per", {}).get("value"),
            "albedo": physical_data.get("albedo", {}).get("value"),
            "spectral_type": physical_data.get("spec_T", {}).get("value"),
            "absolute_magnitude": physical_data.get("H", {}).get("value")
        }
        
        # Dados de classificação
        classification = {
            "object_type": data.get("object_type", "Unknown"),
            "pha_flag": data.get("pha", "N"),
            "neo_flag": data.get("neo", "N"),
            "orbit_class": orbital_data.get("orbit_class", {}).get("orbit_class_type", "Unknown")
        }
        
        # Dados de aproximação próximas
        close_approach_data = []
        if "close_approach_data" in data:
            for approach in data["close_approach_data"][:5]:  # Últimas 5 aproximações
                close_approach_data.append({
                    "date": approach.get("date"),
                    "distance_au": approach.get("dist", {}).get("value"),
                    "velocity_kms": approach.get("v_rel", {}).get("value"),
                    "orbiting_body": approach.get("orbiting_body")
                })
        
        return {
            "asteroid_id": data.get("des", "Unknown"),
            "name": data.get("full_name", "Unknown"),
            "orbital_parameters": orbital_params,
            "physical_parameters": physical_params,
            "classification": classification,
            "close_approaches": close_approach_data,
            "data_source": "JPL Small-Body Database",
            "last_updated": sbdb_response.get("signature", {}).get("source", "Unknown")
        }
        
    except Exception as e:
        print(f"Erro ao processar dados do SBDB: {e}")
        return None

def get_enhanced_asteroid_data(asteroid_id: str) -> Dict | None:
    """
    Combina dados do NeoWs e SBDB para fornecer informações completas sobre um asteroide.
    """
    try:
        # Buscar dados básicos do NeoWs
        neo_data = get_neo_data(asteroid_id)
        if not neo_data:
            return None
        
        # Buscar dados orbitais precisos do SBDB
        sbdb_data = get_sbdb_data(asteroid_id)
        
        # Combinar os dados
        enhanced_data = {
            "basic_info": {
                "id": neo_data.get("id"),
                "name": neo_data.get("name"),
                "neo_reference_id": neo_data.get("neo_reference_id"),
                "absolute_magnitude_h": neo_data.get("absolute_magnitude_h"),
                "estimated_diameter": neo_data.get("estimated_diameter"),
                "is_potentially_hazardous_asteroid": neo_data.get("is_potentially_hazardous_asteroid"),
                "close_approach_data": neo_data.get("close_approach_data", [])
            },
            "orbital_data": sbdb_data.get("orbital_parameters", {}) if sbdb_data else {},
            "physical_data": sbdb_data.get("physical_parameters", {}) if sbdb_data else {},
            "classification": sbdb_data.get("classification", {}) if sbdb_data else {},
            "data_sources": {
                "neows": "NASA Near Earth Object Web Service",
                "sbdb": "JPL Small-Body Database" if sbdb_data else None
            }
        }
        
        return enhanced_data
        
    except Exception as e:
        print(f"Erro ao combinar dados do asteroide: {e}")
        return None