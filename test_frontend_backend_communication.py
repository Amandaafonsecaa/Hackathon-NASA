#!/usr/bin/env python3
"""
Script para testar a comunicação entre Frontend e Backend
"""

import requests
import json
import time

def test_backend_endpoints():
    """Testa todos os endpoints do backend"""
    base_url = "http://localhost:8001"
    
    print("TESTANDO COMUNICACAO FRONTEND <-> BACKEND")
    print("=" * 60)
    
    # Lista de endpoints para testar
    endpoints = [
        "/",
        "/health",
        "/api/v1/test-all",
        "/api/v1/neo/test",
        "/api/v1/simular/test",
        "/api/v1/risco-local/test",
        "/api/v1/evacuacao/test",
        "/api/v1/saude/test",
        "/api/v1/ambiental/test",
        "/api/v1/populacao/test",
        "/api/v1/defesa-civil/test",
        "/api/v1/traffic-ai/test",
        "/api/v1/evacuation-ai/test"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\nTestando: {endpoint}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Status: {response.status_code}")
                print(f"Dados: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                results[endpoint] = {"status": "OK", "data": data}
            else:
                print(f"[ERRO] Status: {response.status_code}")
                results[endpoint] = {"status": "ERROR", "code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Erro de conexao: {e}")
            results[endpoint] = {"status": "CONNECTION_ERROR", "error": str(e)}
        except Exception as e:
            print(f"[ERRO] Erro: {e}")
            results[endpoint] = {"status": "ERROR", "error": str(e)}
    
    return results

def test_frontend_api_calls():
    """Simula chamadas que o frontend faria"""
    print("\nSIMULANDO CHAMADAS DO FRONTEND")
    print("=" * 60)
    
    base_url = "http://localhost:8001/api/v1"
    
    # Simular chamadas que o frontend faz
    frontend_calls = [
        {
            "name": "Teste de Conexão",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "Dados de Asteroide",
            "url": f"{base_url}/neo/test",
            "method": "GET"
        },
        {
            "name": "Simulação de Impacto",
            "url": f"{base_url}/simular/test",
            "method": "GET"
        },
        {
            "name": "Análise de Risco",
            "url": f"{base_url}/risco-local/test",
            "method": "GET"
        },
        {
            "name": "Rotas de Evacuação",
            "url": f"{base_url}/evacuacao/test",
            "method": "GET"
        }
    ]
    
    for call in frontend_calls:
        try:
            print(f"\n🎯 {call['name']}")
            print(f"   URL: {call['url']}")
            
            if call['method'] == 'GET':
                response = requests.get(call['url'], timeout=5)
            else:
                response = requests.post(call['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso: {response.status_code}")
                print(f"   📄 Dados: {json.dumps(data, indent=2, ensure_ascii=False)[:150]}...")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Falha: {e}")

def check_cors_headers():
    """Verifica se o backend tem CORS configurado"""
    print("\n🔒 VERIFICANDO CORS (Cross-Origin Resource Sharing)")
    print("=" * 60)
    
    try:
        # Simular requisição do frontend (origem diferente)
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:8001/health", headers=headers)
        
        print(f"Status OPTIONS: {response.status_code}")
        print("Headers CORS:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS configurado")
        else:
            print("⚠️  CORS pode não estar configurado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar CORS: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE DE COMUNICAÇÃO COSMOS SENTINEL")
    print("=" * 60)
    
    # Verificar se o backend está rodando
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend está rodando")
        else:
            print("❌ Backend não está respondendo corretamente")
            return
    except:
        print("❌ Backend não está acessível")
        print("   Certifique-se de que o backend está rodando em http://localhost:8001")
        return
    
    # Executar testes
    backend_results = test_backend_endpoints()
    test_frontend_api_calls()
    check_cors_headers()
    
    # Resumo
    print("\n📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = len(backend_results)
    successful_tests = len([r for r in backend_results.values() if r.get("status") == "OK"])
    
    print(f"Total de endpoints testados: {total_tests}")
    print(f"Endpoints funcionando: {successful_tests}")
    print(f"Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O frontend deve conseguir se comunicar com o backend")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} endpoints com problemas")
        print("❌ Pode haver problemas na comunicação frontend-backend")

if __name__ == "__main__":
    main()
