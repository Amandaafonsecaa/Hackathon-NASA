from fastapi import APIRouter, HTTPException, Query
from services import nasa_service
from typing import Optional

router = APIRouter()

@router.get("/{asteroid_id}", summary="Buscar dados básicos de um asteroide por ID")
def get_asteroid_data(asteroid_id: str):
    """
    Busca dados básicos de um asteroide via NASA NeoWs API.
    """
    data = nasa_service.get_neo_data(asteroid_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Asteroide com ID {asteroid_id} não encontrado.")
    return data

@router.get("/{asteroid_id}/orbital", summary="Buscar dados orbitais precisos via JPL SBDB")
def get_asteroid_orbital_data(asteroid_id: str):
    """
    Busca dados orbitais precisos de um asteroide via JPL Small-Body Database (SBDB).
    Inclui parâmetros orbitais, físicos e de classificação.
    """
    data = nasa_service.get_sbdb_data(asteroid_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Dados orbitais para asteroide {asteroid_id} não encontrados.")
    return data

@router.get("/{asteroid_id}/enhanced", summary="Buscar dados completos combinados (NeoWs + SBDB)")
def get_enhanced_asteroid_data(asteroid_id: str):
    """
    Combina dados do NASA NeoWs e JPL SBDB para fornecer informações completas sobre um asteroide.
    Inclui dados básicos, orbitais, físicos e de classificação.
    """
    data = nasa_service.get_enhanced_asteroid_data(asteroid_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Dados completos para asteroide {asteroid_id} não encontrados.")
    return data

@router.get("/near-earth", summary="Listar asteroides próximos à Terra")
def get_near_earth_asteroids(
    start_date: str = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data final (YYYY-MM-DD)"),
    limit: int = Query(default=20, description="Número máximo de resultados")
):
    """
    Lista asteroides próximos à Terra em um período específico.
    """
    try:
        import requests
        from datetime import datetime
        
        # Validar formato das datas
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")
        
        # Buscar dados via NASA NeoWs API
        api_key = getattr(settings, 'NASA_API_KEY', 'DEMO_KEY')
        url = f"https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Processar dados e extrair asteroides
        asteroids = []
        for date, asteroids_data in data.get("near_earth_objects", {}).items():
            for asteroid in asteroids_data[:limit]:
                asteroids.append({
                    "id": asteroid.get("neo_reference_id"),
                    "name": asteroid.get("name"),
                    "is_potentially_hazardous": asteroid.get("is_potentially_hazardous_asteroid", False),
                    "estimated_diameter": asteroid.get("estimated_diameter", {}),
                    "close_approach_data": asteroid.get("close_approach_data", [{}])[0],
                    "orbital_data": asteroid.get("orbital_data", {}),
                    "date": date
                })
        
        return {
            "success": True,
            "data": {
                "asteroids": asteroids[:limit],
                "total_count": len(asteroids),
                "date_range": {
                    "start": start_date,
                    "end": end_date
                },
                "source": "NASA NeoWs API"
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados da NASA: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/{asteroid_id}/impact-analysis", summary="Análise de impacto baseada em dados reais")
def get_asteroid_impact_analysis(
    asteroid_id: str,
    impact_latitude: float = Query(..., description="Latitude do ponto de impacto simulado"),
    impact_longitude: float = Query(..., description="Longitude do ponto de impacto simulado"),
    impact_angle_deg: float = Query(default=45, description="Ângulo de impacto em graus (90 = vertical)"),
    target_type: str = Query(default="rocha", description="Tipo de terreno (solo, rocha, oceano)")
):
    """
    Realiza análise de impacto baseada em dados reais de um asteroide.
    Combina dados orbitais precisos com simulação de impacto.
    """
    # Buscar dados completos do asteroide
    asteroid_data = nasa_service.get_enhanced_asteroid_data(asteroid_id)
    if not asteroid_data:
        raise HTTPException(status_code=404, detail=f"Asteroide {asteroid_id} não encontrado.")
    
    # Extrair parâmetros para simulação
    physical_data = asteroid_data.get("physical_data", {})
    basic_info = asteroid_data.get("basic_info", {})
    
    # Estimar diâmetro (usar dados do SBDB se disponível, senão usar NeoWs)
    diameter_m = None
    if physical_data.get("diameter_km"):
        diameter_m = physical_data["diameter_km"] * 1000
    elif basic_info.get("estimated_diameter"):
        # Usar diâmetro médio estimado
        diameter_data = basic_info["estimated_diameter"]
        if diameter_data.get("meters"):
            avg_diameter = (diameter_data["meters"]["estimated_diameter_min"] + 
                          diameter_data["meters"]["estimated_diameter_max"]) / 2
            diameter_m = avg_diameter
    
    if not diameter_m:
        raise HTTPException(
            status_code=400, 
            detail="Não foi possível determinar o diâmetro do asteroide para a simulação."
        )
    
    # Velocidade típica de impacto (17 km/s é uma média)
    velocity_kms = 17.0
    
    # Executar simulação de impacto
    from services import physics_service
    impact_results = physics_service.calculate_all_impact_effects(
        diameter_m=diameter_m,
        velocity_kms=velocity_kms,
        impact_angle_deg=impact_angle_deg,
        tipo_terreno=target_type
    )
    
    # Gerar zonas de risco GeoJSON
    from services import geojson_service
    risk_zones = geojson_service.generate_impact_risk_zones(
        impact_lat=impact_latitude,
        impact_lon=impact_longitude,
        physics_results=impact_results
    )
    
    return {
        "asteroid_info": {
            "id": asteroid_id,
            "name": asteroid_data.get("basic_info", {}).get("name", "Unknown"),
            "diameter_m": diameter_m,
            "is_potentially_hazardous": asteroid_data.get("basic_info", {}).get("is_potentially_hazardous_asteroid", False),
            "classification": asteroid_data.get("classification", {})
        },
        "impact_simulation": impact_results,
        "risk_zones_geojson": risk_zones,
        "impact_coordinates": [impact_longitude, impact_latitude]
    }