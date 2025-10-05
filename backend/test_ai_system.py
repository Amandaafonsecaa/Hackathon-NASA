#!/usr/bin/env python3
"""
Script de teste rápido para o sistema de IA de evacuação.
Verifica se todos os componentes estão funcionando corretamente.
"""

import sys
import os
import time
import traceback

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todas as importações estão funcionando."""
    print("🔍 Testando importações...")
    
    try:
        from services.traffic_ai_service import traffic_ai_service
        print("  ✅ Traffic AI Service")
    except Exception as e:
        print(f"  ❌ Traffic AI Service: {e}")
        return False
    
    try:
        from services.traffic_assignment import coordination_system
        print("  ✅ Traffic Assignment (RL)")
    except Exception as e:
        print(f"  ❌ Traffic Assignment: {e}")
        return False
    
    try:
        from services.realtime_websocket import realtime_service
        print("  ✅ Realtime WebSocket")
    except Exception as e:
        print(f"  ❌ Realtime WebSocket: {e}")
        return False
    
    try:
        from services.integrated_evacuation_service import integrated_evacuation_service
        print("  ✅ Integrated Evacuation Service")
    except Exception as e:
        print(f"  ❌ Integrated Evacuation Service: {e}")
        return False
    
    try:
        from config.ai_config import DEFAULT_CONFIG
        print("  ✅ AI Configuration")
    except Exception as e:
        print(f"  ❌ AI Configuration: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Testa funcionalidades básicas dos serviços."""
    print("\n🧪 Testando funcionalidades básicas...")
    
    try:
        from services.traffic_ai_service import traffic_ai_service
        from config.ai_config import DEFAULT_CONFIG
        
        # Testar carregamento de rede (simulado)
        print("  🔄 Testando carregamento de rede viária...")
        # Nota: Este teste pode falhar se não houver internet ou OSMnx não estiver configurado
        # network_result = traffic_ai_service.load_road_network(
        #     center_point=(-23.5505, -46.6333),
        #     radius_km=5
        # )
        print("  ⚠️  Carregamento de rede pulado (requer internet)")
        
        # Testar geração de dados sintéticos ML
        print("  🤖 Testando geração de dados sintéticos ML...")
        X, y = traffic_ai_service._generate_synthetic_training_data()
        print(f"  ✅ Dados gerados: {len(X)} amostras, {X.shape[1]} features")
        
        # Testar configuração
        print("  ⚙️  Testando configurações...")
        config = DEFAULT_CONFIG
        print(f"  ✅ Configuração carregada: BPR α={config.bpr.alpha}, β={config.bpr.beta}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na funcionalidade básica: {e}")
        traceback.print_exc()
        return False

def test_ml_model():
    """Testa treinamento e predição do modelo ML."""
    print("\n🤖 Testando modelo ML...")
    
    try:
        from services.traffic_ai_service import traffic_ai_service
        
        # Treinar modelo
        print("  📚 Treinando modelo ML...")
        train_result = traffic_ai_service.train_ml_model(synthetic_data=True)
        
        if train_result["success"]:
            print(f"  ✅ Modelo treinado: score={train_result['test_score']:.3f}")
            
            # Testar predição
            print("  🔮 Testando predição...")
            features = {
                "hour": 14,
                "rainfall": 2,
                "visibility": 8,
                "wind_speed": 10,
                "grade": 3,
                "surface_type": 0,
                "lanes": 2
            }
            
            prediction = traffic_ai_service.predict_travel_time(features)
            print(f"  ✅ Predição: {prediction:.1f} segundos")
            
            return True
        else:
            print(f"  ❌ Erro no treinamento: {train_result['error']}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no modelo ML: {e}")
        traceback.print_exc()
        return False

def test_rl_controller():
    """Testa controlador RL."""
    print("\n🧠 Testando controlador RL...")
    
    try:
        from services.traffic_assignment import TrafficRLController, IntersectionState
        
        # Criar controlador
        controller = TrafficRLController("test_intersection", 4)
        print("  ✅ Controlador RL criado")
        
        # Testar estado
        state = IntersectionState(
            queue_lengths=[10, 8, 12, 6],
            flow_rates=[20, 18, 25, 15],
            waiting_times=[30, 25, 35, 20],
            phase_duration=0,
            time_of_day=8.0,
            weather_condition=0
        )
        
        # Testar seleção de ação
        action = controller.select_action(state, training=False)
        print(f"  ✅ Ação selecionada: {action}")
        
        # Testar cálculo de recompensa
        next_state = IntersectionState(
            queue_lengths=[8, 6, 10, 4],
            flow_rates=[25, 20, 30, 18],
            waiting_times=[20, 15, 25, 10],
            phase_duration=30,
            time_of_day=8.1,
            weather_condition=0
        )
        
        reward = controller.calculate_reward(state, next_state, action)
        print(f"  ✅ Recompensa calculada: {reward:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no controlador RL: {e}")
        traceback.print_exc()
        return False

def test_websocket_service():
    """Testa serviço WebSocket."""
    print("\n🌐 Testando serviço WebSocket...")
    
    try:
        from services.realtime_websocket import realtime_service, WebSocketMessage, MessageType
        
        # Testar criação de mensagem
        message = WebSocketMessage(
            message_type=MessageType.TRAFFIC_UPDATE.value,
            timestamp=time.time(),
            data={"test": "data"}
        )
        print("  ✅ Mensagem WebSocket criada")
        
        # Testar estatísticas
        stats = realtime_service.get_connection_stats()
        print(f"  ✅ Estatísticas: {stats['active_connections']} conexões")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no serviço WebSocket: {e}")
        traceback.print_exc()
        return False

def test_integrated_service():
    """Testa serviço integrado."""
    print("\n🔗 Testando serviço integrado...")
    
    try:
        from services.integrated_evacuation_service import integrated_evacuation_service
        
        # Testar listagem de cenários
        scenarios = integrated_evacuation_service.list_active_scenarios()
        print(f"  ✅ Cenários ativos: {scenarios['active_scenarios']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no serviço integrado: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal do teste."""
    print("🧭 COSMOS SENTINEL - TESTE DO SISTEMA DE IA")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Funcionalidades Básicas", test_basic_functionality),
        ("Modelo ML", test_ml_model),
        ("Controlador RL", test_rl_controller),
        ("Serviço WebSocket", test_websocket_service),
        ("Serviço Integrado", test_integrated_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"💥 {test_name}: ERRO CRÍTICO - {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        return 0
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
