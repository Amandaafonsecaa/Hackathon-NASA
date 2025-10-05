from fastapi import FastAPI
from routers import neo_router, simulate_router, risk_router, geo_router, geojson_router, evacuation_router, report_router, health_router, environmental_router, satellite_router, earthdata_router

app = FastAPI(
    title="Simulador de Impacto de Asteroide API",
    description="Uma API para simular os efeitos de impactos de asteroides na Terra.",
    version="1.0.0"
)

app.include_router(neo_router.router, prefix="/api/v1/neo", tags=["NASA NEOs"])
app.include_router(simulate_router.router, prefix="/api/v1/simular", tags=["Simulação"])
app.include_router(risk_router.router, prefix="/api/v1/risco-local", tags=["Risco Local"])
app.include_router(geo_router.router, prefix="/api/v1/dados-geograficos", tags=["Dados Geográficos"])
app.include_router(geojson_router.router, prefix="/api/v1/geojson", tags=["GeoJSON - Zonas de Risco"])
app.include_router(evacuation_router.router, prefix="/api/v1/evacuacao", tags=["Rotas de Evacuação"])
app.include_router(report_router.router, prefix="/api/v1/relatorios", tags=["Relatórios Executivos"])
app.include_router(health_router.router, prefix="/api/v1/saude", tags=["Monitoramento de Saúde"])
app.include_router(environmental_router.router, prefix="/api/v1/ambiental", tags=["Dados Ambientais"])
app.include_router(satellite_router.router, prefix="/api/v1/satelite", tags=["Imagens de Satélite"])
app.include_router(earthdata_router.router, prefix="/api/v1/earthdata", tags=["Acesso Unificado NASA"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do Simulador de Impacto de Asteroide!"}