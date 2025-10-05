from fastapi import APIRouter
from services import geo_service

router = APIRouter()

@router.get("/", summary="Verificar risco em uma coordenada")
def check_risk(lat: float, lon: float, crater_km: float = 1.0):
    risk_data = geo_service.check_local_risk(lat, lon, crater_km)
    return risk_data