#!/usr/bin/env python3
"""
Script para testar integração com frontend.
Verifica todos os endpoints que o frontend pode usar.
"""

import requests
import time
import json

def test_endpoint(url, name, expected_status=200):
    """Testa um endpoint específico"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK (Status: {response.status_code})")
            return True
        else:
            print(f"❌ {name}: Status {response.status_code} (esperado: {expected_status})")
            return False
    except Exception as e:
        print(f"❌ {name}: Erro - {e}")
        return False

def test_cors():
    """Testa CORS para diferentes origens"""
    print("\n🌐 Testando CORS...")
    
    origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    cors_working = 0
    
    for origin in origins:
        try:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = requests.options(
                "http://localhost:8001/api/v1/connection-test",
                headers=headers,
                timeout=5
            )
            
            if response.status_code in [200, 204]:
                print(f"✅ CORS para {origin}: OK")
                cors_working += 1
            else:
                print(f"❌ CORS para {origin}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ CORS para {origin}: Erro - {e}")
    
    return cors_working == len(origins)

def main():
    """Função principal de teste"""
    print("🌐 COSMOS SENTINEL - TESTE DE INTEGRAÇÃO COM FRONTEND")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Endpoints que o frontend pode usar
    endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/api/v1/", "API Root"),
        ("/api/v1/connection-test", "Teste de Conexão"),
        ("/api/v1/system-info", "Informações do Sistema"),
        ("/api/v1/test-all", "Teste Completo"),
        ("/api/v1/neo/test", "NASA NEOs"),
        ("/api/v1/simular/test", "Simulação"),
        ("/api/v1/risco-local/test", "Risco Local"),
        ("/api/v1/evacuacao/test", "Evacuação"),
        ("/api/v1/saude/test", "Saúde"),
        ("/api/v1/ambiental/test", "Ambiental"),
        ("/api/v1/populacao/test", "População"),
        ("/api/v1/defesa-civil/test", "Defesa Civil"),
        ("/api/v1/traffic-ai/test", "IA Tráfego"),
        ("/api/v1/evacuation-ai/test", "IA Integrada")
    ]
    
    print("🔍 Testando endpoints principais...")
    print("-" * 40)
    
    results = []
    for endpoint, name in endpoints:
        success = test_endpoint(f"{base_url}{endpoint}", name)
        results.append(success)
        time.sleep(0.1)
    
    # Testar CORS
    cors_ok = test_cors()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (endpoint, name) in enumerate(endpoints):
        status = "✅ PASSOU" if results[i] else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\n🌐 CORS: {'✅ FUNCIONANDO' if cors_ok else '❌ PROBLEMAS'}")
    print(f"🎯 RESULTADO FINAL: {passed}/{total} endpoints funcionando")
    
    if passed == total and cors_ok:
        print("\n🎉 INTEGRAÇÃO COM FRONTEND PERFEITA!")
        print("✅ Backend pronto para uso com frontend!")
        print("\n📋 Endpoints disponíveis para o frontend:")
        print("   - http://localhost:8001/api/v1/")
        print("   - http://localhost:8001/api/v1/connection-test")
        print("   - http://localhost:8001/api/v1/system-info")
        print("   - http://localhost:8001/docs (documentação)")
        
        print("\n🔧 Configuração CORS:")
        print("   - Origens permitidas: localhost:3000, 3001, 5173, 8080")
        print("   - Métodos: GET, POST, PUT, DELETE, OPTIONS")
        print("   - Headers: * (todos)")
        
        return True
    else:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:")
        if not cors_ok:
            print("   - CORS não configurado corretamente")
        if passed < total:
            print(f"   - {total - passed} endpoints com problemas")
        print("\n💡 Verifique se o servidor está rodando com main_fixed.py")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
