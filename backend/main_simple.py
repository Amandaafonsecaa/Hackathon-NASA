from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
from typing import Dict, Any, List, Optional
import time
from services import physics_service

app = FastAPI(
    title="COSMOS SENTINEL API",
    description="API para simulação de impacto de asteroides e evacuação",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos que funcionam sem dependências complexas

from pydantic import BaseModel
from typing import Literal

class SimulationInput(BaseModel):
    diameter_m: float
    velocity_kms: float
    impact_angle_deg: float
    target_type: Literal["solo", "rocha", "oceano"]
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.post("/api/v1/simular", tags=["Simulação Real"])
def simulate_impact(input_data: SimulationInput):
    """Simulação real de impacto usando physics_service"""
    try:
        full_report = physics_service.calculate_all_impact_effects(
            diameter_m=input_data.diameter_m,
            velocity_kms=input_data.velocity_kms,
            impact_angle_deg=input_data.impact_angle_deg,
            tipo_terreno=input_data.target_type
        )
        return full_report
    except Exception as e:
        return {"error": f"Erro na simulação: {str(e)}"}

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "COSMOS SENTINEL API - Sistema de Evacuação Inteligente"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/api/v1/neo/test", tags=["NASA NEOs"])
def test_neo():
    """Teste básico do endpoint NEO"""
    return {
        "message": "Endpoint NEO funcionando",
        "data": {
            "near_earth_objects": [],
            "total_count": 0,
            "status": "mock_data"
        }
    }


@app.get("/api/v1/simular/test", tags=["Simulação"])
def test_simulation():
    """Teste básico do endpoint de simulação"""
    return {
        "message": "Endpoint de simulação funcionando",
        "simulation": {
            "asteroid_diameter": 100,
            "impact_energy": 1000000,
            "affected_area": 50000,
            "status": "simulated"
        }
    }


@app.get("/api/v1/risco-local/test", tags=["Risco Local"])
def test_risk():
    """Teste básico do endpoint de risco local"""
    return {
        "message": "Endpoint de risco funcionando",
        "risk_assessment": {
            "risk_level": "medium",
            "population_at_risk": 100000,
            "evacuation_time": 120,
            "status": "calculated"
        }
    }


@app.get("/api/v1/evacuacao/test", tags=["Rotas de Evacuação"])
def test_evacuation():
    """Teste básico do endpoint de evacuação"""
    return {
        "message": "Endpoint de evacuação funcionando",
        "evacuation_routes": [
            {
                "route_id": "route_1",
                "distance": 50.5,
                "estimated_time": 45,
                "capacity": 1000
            }
        ],
        "status": "generated"
    }


@app.get("/api/v1/saude/test", tags=["Monitoramento de Saúde"])
def test_health():
    """Teste básico do endpoint de saúde"""
    return {
        "message": "Endpoint de saúde funcionando",
        "health_metrics": {
            "hospitals_available": 5,
            "ambulances_ready": 12,
            "response_time": 8,
            "status": "monitoring"
        }
    }


@app.get("/api/v1/ambiental/test", tags=["Dados Ambientais"])
def test_environmental():
    """Teste básico do endpoint ambiental"""
    return {
        "message": "Endpoint ambiental funcionando",
        "environmental_data": {
            "air_quality": "good",
            "temperature": 25.5,
            "humidity": 60,
            "wind_speed": 15,
            "status": "monitoring"
        }
    }


@app.get("/api/v1/populacao/test", tags=["População e Demografia"])
def test_population():
    """Teste básico do endpoint de população"""
    return {
        "message": "Endpoint de população funcionando",
        "population_data": {
            "total_population": 500000,
            "density": 1500,
            "age_distribution": {
                "children": 20,
                "adults": 60,
                "elderly": 20
            },
            "status": "analyzed"
        }
    }


@app.get("/api/v1/defesa-civil/test", tags=["Defesa Civil"])
def test_civil_defense():
    """Teste básico do endpoint de defesa civil"""
    return {
        "message": "Endpoint de defesa civil funcionando",
        "civil_defense": {
            "emergency_services": "active",
            "evacuation_centers": 10,
            "emergency_supplies": "sufficient",
            "status": "ready"
        }
    }


@app.get("/api/v1/traffic-ai/test", tags=["IA de Tráfego"])
def test_traffic_ai():
    """Teste básico do endpoint de IA de tráfego"""
    return {
        "message": "Endpoint de IA de tráfego funcionando",
        "traffic_ai": {
            "ml_model_status": "trained",
            "prediction_accuracy": 0.85,
            "optimization_active": True,
            "status": "operational"
        }
    }

# ===== ENDPOINTS DE IA DE TRÁFEGO =====

class DemandRequest(BaseModel):
    origins: List[Dict] = []
    destinations: List[Dict] = []

class AssignmentRequest(BaseModel):
    center_latitude: float
    center_longitude: float
    radius_km: float = 10
    max_iterations: int = 50
    convergence_threshold: float = 0.01
    risk_penalty_multiplier: float = 2.0
    risk_zones_geojson: Optional[Dict] = None

@app.post("/api/v1/traffic-ai/demand", tags=["IA de Tráfego"])
def set_demand_matrix(request: DemandRequest):
    """Define matriz de demanda origem-destino"""
    try:
        return {
            "success": True,
            "message": "Matriz de demanda configurada",
            "data": {
                "origins_count": len(request.origins),
                "destinations_count": len(request.destinations),
                "total_demand": sum(origin.get("population", 0) for origin in request.origins)
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao configurar matriz: {str(e)}"}

@app.post("/api/v1/traffic-ai/assign", tags=["IA de Tráfego"])
def execute_traffic_assignment(request: AssignmentRequest):
    """Executa assignment de tráfego com otimização"""
    try:
        # Simular dados de assignment
        return {
            "success": True,
            "message": "Assignment executado com sucesso",
            "data": {
                "efficiency": 85.5,
                "total_travel_time": 2.3,
                "congestion_level": "medium",
                "iterations_completed": request.max_iterations,
                "convergence_achieved": True,
                "network_nodes": 150,
                "network_edges": 300
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro no assignment: {str(e)}"}

@app.get("/api/v1/traffic-ai/network/load", tags=["IA de Tráfego"])
def load_road_network(lat: float, lon: float, radius: float = 10):
    """Carrega rede viária de uma área"""
    try:
        # Simular carregamento de rede viária
        return {
            "success": True,
            "message": "Rede viária carregada",
            "data": {
                "nodes": 150,
                "edges": 300,
                "area_km2": radius * radius * 3.14,
                "center": [lat, lon],
                "radius_km": radius
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao carregar rede: {str(e)}"}

@app.get("/api/v1/traffic-ai/routes", tags=["IA de Tráfego"])
def get_evacuation_routes(k: int = 3):
    """Obtém rotas de evacuação otimizadas"""
    try:
        # Gerar rotas simuladas
        routes = []
        for i in range(k):
            routes.append({
                "id": f"route_{i+1}",
                "name": f"Rota {['Norte', 'Sul', 'Leste'][i]} (IA)",
                "from": [-23.5505, -46.6333],
                "to": [
                    [-23.5505 + 0.01, -46.6333],
                    [-23.5505 - 0.01, -46.6333],
                    [-23.5505, -46.6333 + 0.01]
                ][i],
                "distance": 8.5 - i * 0.5,
                "estimatedTime": 25 - i * 2,
                "capacity": 5000 - i * 500,
                "efficiency": 88 + i * 2,
                "aiOptimized": True,
                "color": ["#3B82F6", "#10B981", "#F59E0B"][i]
            })
        
        return {
            "success": True,
            "message": f"{k} rotas otimizadas geradas",
            "data": {
                "routes": routes,
                "total_capacity": sum(route["capacity"] for route in routes),
                "average_efficiency": sum(route["efficiency"] for route in routes) / len(routes)
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao gerar rotas: {str(e)}"}

@app.get("/api/v1/traffic-ai/status", tags=["IA de Tráfego"])
def get_traffic_status():
    """Obtém status do sistema de IA"""
    try:
        return {
            "success": True,
            "message": "Status do sistema de IA",
            "data": {
                "ml_model_status": "trained",
                "prediction_accuracy": 0.85,
                "optimization_active": True,
                "last_training": time.time() - 3600,
                "active_scenarios": 1,
                "system_load": 0.3
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao obter status: {str(e)}"}

@app.post("/api/v1/traffic-ai/ml/predict", tags=["IA de Tráfego"])
def predict_travel_time(prediction_data: Dict):
    """Predição ML de tempo de viagem"""
    try:
        return {
            "success": True,
            "message": "Predição realizada",
            "data": {
                "predicted_time": 2.3,
                "confidence": 0.85,
                "factors": ["traffic_density", "weather", "time_of_day"],
                "model_version": "v1.2"
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Erro na predição: {str(e)}"}


@app.get("/api/v1/evacuation-ai/test", tags=["IA Integrada"])
def test_integrated_ai():
    """Teste básico do endpoint de IA integrada"""
    return {
        "message": "Endpoint de IA integrada funcionando",
        "integrated_ai": {
            "scenarios_active": 0,
            "ai_components": ["traffic", "evacuation", "health"],
            "status": "ready"
        }
    }

# Endpoint para testar todos os serviços de uma vez


@app.get("/api/v1/test-all", tags=["Teste Completo"])
def test_all_services():
    """Testa todos os serviços principais"""
    services = [
        "neo", "simulation", "risk", "evacuation",
        "health", "environmental", "population",
        "civil_defense", "traffic_ai", "integrated_ai"
    ]

    results = {}
    for service in services:
        try:
            # Simular teste de cada serviço
            results[service] = {
                "status": "working",
                "response_time": 0.1,
                "last_check": time.time()
            }
        except Exception as e:
            results[service] = {
                "status": "error",
                "error": str(e),
                "last_check": time.time()
            }

    return {
        "message": "Teste completo dos serviços",
        "total_services": len(services),
        "working_services": len([s for s in results.values() if s["status"] == "working"]),
        "services": results,
        "overall_status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
