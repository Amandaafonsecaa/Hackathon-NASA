"""
Exemplo de uso da IA para evacuação sem congestionamento.
Demonstra como usar todos os componentes do sistema integrado.
"""

import asyncio
import requests
import json
import time
from typing import Dict, List

# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"
EVACUATION_AI_URL = f"{API_BASE_URL}/evacuation-ai"
TRAFFIC_AI_URL = f"{API_BASE_URL}/traffic-ai"
WEBSOCKET_URL = "ws://localhost:8000/api/v1/ws/traffic"

def create_sample_evacuation_request() -> Dict:
    """Cria request de exemplo para análise de evacuação."""
    
    # Dados do asteroide
    asteroid_data = {
        "impact_latitude": -23.5505,  # São Paulo
        "impact_longitude": -46.6333,
        "asteroid_diameter_m": 500,  # 500 metros
        "asteroid_velocity_kms": 20,  # 20 km/s
        "impact_angle_deg": 45,
        "terrain_type": "rock",
        "wind_speed_ms": 10,
        "wind_direction_deg": 0,
        "evacuation_radius_km": 25
    }
    
    # Áreas populacionais (simuladas)
    population_areas = [
        {
            "id": "area_001",
            "name": "Centro de São Paulo",
            "population": 50000,
            "latitude": -23.5505,
            "longitude": -46.6333,
            "priority": 1
        },
        {
            "id": "area_002", 
            "name": "Zona Sul",
            "population": 30000,
            "latitude": -23.5805,
            "longitude": -46.6533,
            "priority": 1
        },
        {
            "id": "area_003",
            "name": "Zona Norte",
            "population": 25000,
            "latitude": -23.5205,
            "longitude": -46.6133,
            "priority": 2
        },
        {
            "id": "area_004",
            "name": "Zona Oeste",
            "population": 20000,
            "latitude": -23.5705,
            "longitude": -46.6733,
            "priority": 2
        }
    ]
    
    # Pontos de evacuação
    evacuation_points = [
        {
            "id": "shelter_001",
            "name": "Abrigo Central",
            "type": "shelter",
            "capacity": 5000,
            "latitude": -23.6005,
            "longitude": -46.6833
        },
        {
            "id": "hospital_001",
            "name": "Hospital Municipal",
            "type": "hospital",
            "capacity": 2000,
            "latitude": -23.5805,
            "longitude": -46.7033
        },
        {
            "id": "safe_zone_001",
            "name": "Zona Segura Norte",
            "type": "safe_zone",
            "capacity": 10000,
            "latitude": -23.4805,
            "longitude": -46.5933
        },
        {
            "id": "safe_zone_002",
            "name": "Zona Segura Sul",
            "type": "safe_zone", 
            "capacity": 8000,
            "latitude": -23.6205,
            "longitude": -46.6933
        }
    ]
    
    return {
        **asteroid_data,
        "population_areas": population_areas,
        "evacuation_points": evacuation_points,
        "enable_ml_predictions": True,
        "enable_rl_control": True,
        "enable_realtime_updates": True
    }

def run_evacuation_analysis():
    """Executa análise completa de evacuação."""
    
    print("🚀 Iniciando análise de evacuação com IA...")
    
    # Criar request
    request_data = create_sample_evacuation_request()
    
    # Enviar request
    print("📡 Enviando request para API...")
    response = requests.post(
        f"{EVACUATION_AI_URL}/analyze",
        json=request_data,
        timeout=300  # 5 minutos timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("✅ Análise concluída com sucesso!")
        print(f"⏱️  Tempo de execução: {result['execution_time_seconds']:.2f}s")
        print(f"🆔 ID do cenário: {result['scenario_id']}")
        
        # Mostrar resultados principais
        print("\n📊 RESULTADOS DA ANÁLISE:")
        print("=" * 50)
        
        # Simulação de impacto
        impact = result['impact_simulation']
        print(f"💥 Energia do impacto: {impact['energy_megatons']:.1f} MT")
        print(f"🕳️  Diâmetro da cratera: {impact['crater_diameter_km']:.2f} km")
        print(f"🌊 Tsunami gerado: {'Sim' if impact['tsunami_generated'] else 'Não'}")
        
        # Análise de tráfego
        traffic = result['traffic_analysis']
        print(f"🛣️  Nós da rede: {traffic['network_stats'].get('nodes', 0)}")
        print(f"🛣️  Arestas da rede: {traffic['network_stats'].get('edges', 0)}")
        print(f"👥 Demanda total: {traffic['demand_stats']['total_demand']:.0f} veículos")
        print(f"🔄 Iterações do assignment: {traffic['assignment_results']['iterations']}")
        print(f"✅ Convergiu: {'Sim' if traffic['assignment_results']['converged'] else 'Não'}")
        print(f"⚠️  Gargalos detectados: {traffic['assignment_results']['bottlenecks']}")
        
        # Rotas de evacuação
        routes = result['evacuation_routes']
        print(f"🗺️  Pares OD: {routes['total_od_pairs']}")
        print(f"🛣️  Rotas por par: {routes['routes_per_pair']}")
        
        # Controladores RL
        rl = result['rl_controllers']
        print(f"🚦 Interseções controladas: {rl['total_intersections']}")
        
        # Recomendações
        recs = result['recommendations']
        print(f"⏰ Tempo estimado de evacuação: {recs['estimated_evacuation_time']}")
        print(f"🔄 Evacuação escalonada recomendada: {'Sim' if recs['staggering_recommended'] else 'Não'}")
        
        return result['scenario_id']
        
    else:
        print(f"❌ Erro na análise: {response.status_code}")
        print(f"Detalhes: {response.text}")
        return None

def check_scenario_status(scenario_id: str):
    """Verifica status de um cenário."""
    
    print(f"\n📋 Verificando status do cenário {scenario_id}...")
    
    response = requests.get(f"{EVACUATION_AI_URL}/scenario/{scenario_id}/status")
    
    if response.status_code == 200:
        status = response.json()
        
        print("📊 STATUS DO CENÁRIO:")
        print("=" * 30)
        
        components = status['status']
        for component, status_val in components.items():
            icon = "✅" if status_val else "❌"
            print(f"{icon} {component}: {status_val}")
        
        stats = status['statistics']
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"👥 Demanda total: {stats['total_demand']:.0f}")
        print(f"🔄 Iterações: {stats['assignment_iterations']}")
        print(f"🛣️  Rotas: {stats['routes_count']}")
        print(f"⚠️  Gargalos: {stats['bottlenecks']}")
        
    else:
        print(f"❌ Erro ao verificar status: {response.status_code}")

def test_traffic_ai_components():
    """Testa componentes individuais da IA de tráfego."""
    
    print("\n🧪 Testando componentes da IA de tráfego...")
    
    # 1. Carregar rede viária
    print("1. Carregando rede viária...")
    response = requests.get(
        f"{TRAFFIC_AI_URL}/network/load",
        params={
            "center_latitude": -23.5505,
            "center_longitude": -46.6333,
            "radius_km": 15
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Rede carregada: {result['stats']['nodes']} nós, {result['stats']['edges']} arestas")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # 2. Treinar modelo ML
    print("2. Treinando modelo ML...")
    response = requests.post(f"{TRAFFIC_AI_URL}/ml/train")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Modelo treinado: score={result['test_score']:.3f}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # 3. Fazer predição ML
    print("3. Fazendo predição ML...")
    prediction_request = {
        "features": {
            "hour": 14,
            "rainfall": 2,
            "visibility": 8,
            "wind_speed": 10,
            "grade": 3,
            "surface_type": 0,
            "lanes": 2
        }
    }
    
    response = requests.post(
        f"{TRAFFIC_AI_URL}/ml/predict",
        json=prediction_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Tempo previsto: {result['predicted_travel_time_minutes']:.1f} minutos")
    else:
        print(f"   ❌ Erro: {response.status_code}")
    
    # 4. Verificar status do sistema
    print("4. Verificando status do sistema...")
    response = requests.get(f"{TRAFFIC_AI_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Status: {result['status']}")
        print(f"   📊 Conexões ativas: {result['components']['coordination_system']['intersections_count']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")

def test_websocket_connection():
    """Testa conexão WebSocket."""
    
    print("\n🌐 Testando WebSocket...")
    
    try:
        import websockets
        
        async def websocket_test():
            uri = WEBSOCKET_URL + "?client_id=example_client"
            
            async with websockets.connect(uri) as websocket:
                print("   ✅ Conectado ao WebSocket")
                
                # Inscrever em atualizações
                await websocket.send(json.dumps({
                    "type": "subscribe",
                    "data": {"subscription_type": "traffic_updates"}
                }))
                print("   ✅ Inscrito em atualizações de tráfego")
                
                # Enviar heartbeat
                await websocket.send(json.dumps({
                    "type": "heartbeat",
                    "data": {}
                }))
                print("   ✅ Heartbeat enviado")
                
                # Aguardar algumas mensagens
                for i in range(3):
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"   📨 Mensagem {i+1}: {data['message_type']}")
                
                print("   ✅ WebSocket funcionando corretamente")
        
        # Executar teste
        asyncio.run(websocket_test())
        
    except ImportError:
        print("   ⚠️  websockets não instalado, pulando teste WebSocket")
    except Exception as e:
        print(f"   ❌ Erro no WebSocket: {e}")

def update_scenario_example(scenario_id: str):
    """Exemplo de atualização de cenário."""
    
    print(f"\n🔄 Atualizando cenário {scenario_id}...")
    
    # Simular novas condições
    updates = {
        "scenario_id": scenario_id,
        "weather_update": {
            "hour": 18,
            "rainfall": 5,
            "visibility": 4,
            "wind_speed": 15
        },
        "traffic_incidents": [
            {
                "type": "accident",
                "location": {"latitude": -23.5605, "longitude": -46.6433},
                "severity": "medium",
                "estimated_resolution": "30min"
            }
        ]
    }
    
    response = requests.post(
        f"{EVACUATION_AI_URL}/update-scenario",
        json=updates
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Cenário atualizado: {result['updates_applied']}")
    else:
        print(f"   ❌ Erro na atualização: {response.status_code}")

def main():
    """Função principal do exemplo."""
    
    print("🧭 COSMOS SENTINEL - IA PARA EVACUAÇÃO INTELIGENTE")
    print("=" * 60)
    print("Este exemplo demonstra o uso completo do sistema de IA")
    print("para evacuação sem congestionamento.")
    print("=" * 60)
    
    try:
        # 1. Executar análise completa
        scenario_id = run_evacuation_analysis()
        
        if scenario_id:
            # 2. Verificar status
            check_scenario_status(scenario_id)
            
            # 3. Testar componentes individuais
            test_traffic_ai_components()
            
            # 4. Testar WebSocket
            test_websocket_connection()
            
            # 5. Exemplo de atualização
            update_scenario_example(scenario_id)
            
            print("\n🎉 Exemplo concluído com sucesso!")
            print(f"📋 Cenário criado: {scenario_id}")
            print("🌐 WebSocket ativo para atualizações em tempo real")
            print("📊 Sistema pronto para evacuação inteligente")
            
        else:
            print("\n❌ Falha na análise inicial")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar à API")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
