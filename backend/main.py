from fastapi import FastAPI
from routers import neo_router, simulate_router, risk_router, geo_router, geojson_router, evacuation_router, report_router, health_router, environmental_router, satellite_router, earthdata_router, population_router, civil_defense_router, traffic_ai_router, websocket_router, integrated_evacuation_router

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
app.include_router(population_router.router, prefix="/api/v1/populacao", tags=["População e Demografia"])
app.include_router(civil_defense_router.router, prefix="/api/v1/defesa-civil", tags=["Defesa Civil"])
app.include_router(traffic_ai_router.router, prefix="/api/v1/traffic-ai", tags=["IA de Tráfego e Evacuação"])
app.include_router(websocket_router.router, prefix="/api/v1", tags=["WebSocket - Tempo Real"])
app.include_router(integrated_evacuation_router.router, prefix="/api/v1/evacuation-ai", tags=["🧭 IA Integrada para Evacuação"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do Simulador de Impacto de Asteroide!"}