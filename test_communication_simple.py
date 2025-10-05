#!/usr/bin/env python3
"""
Script simplificado para testar a comunicação entre Frontend e Backend
"""

import requests
import json

def test_backend():
    """Testa se o backend está funcionando"""
    print("TESTE DE COMUNICACAO FRONTEND <-> BACKEND")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Testar endpoints principais
    endpoints = [
        "/",
        "/health", 
        "/api/v1/test-all",
        "/api/v1/neo/test",
        "/api/v1/simular/test"
    ]
    
    print("\nTestando endpoints do backend:")
    print("-" * 40)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {endpoint} - Status: {response.status_code}")
                print(f"     Resposta: {str(data)[:100]}...")
            else:
                print(f"[ERRO] {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"[ERRO] {endpoint} - Falha: {e}")
    
    print("\n" + "=" * 60)

def test_frontend_connection():
    """Testa se o frontend pode se conectar ao backend"""
    print("SIMULANDO CHAMADAS DO FRONTEND")
    print("=" * 60)
    
    # Simular chamadas que o frontend faria
    api_calls = [
        {
            "name": "Teste de Conexao",
            "url": "http://localhost:8000/api/v1/"
        },
        {
            "name": "Dados de Asteroide", 
            "url": "http://localhost:8000/api/v1/neo/test"
        },
        {
            "name": "Simulacao de Impacto",
            "url": "http://localhost:8000/api/v1/simular/test"
        }
    ]
    
    for call in api_calls:
        try:
            print(f"\nTestando: {call['name']}")
            response = requests.get(call['url'], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Sucesso - Status: {response.status_code}")
                print(f"     Dados recebidos: {str(data)[:150]}...")
            else:
                print(f"[ERRO] Falha - Status: {response.status_code}")
                
        except Exception as e:
            print(f"[ERRO] Falha na conexao: {e}")

def check_services():
    """Verifica se os serviços estão rodando"""
    print("VERIFICANDO SERVICOS")
    print("=" * 60)
    
    # Verificar backend
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Backend rodando em http://localhost:8000")
        else:
            print("[ERRO] Backend nao esta respondendo corretamente")
    except:
        print("[ERRO] Backend nao esta acessivel")
    
    # Verificar frontend
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("[OK] Frontend rodando em http://localhost:3000")
        else:
            print("[ERRO] Frontend nao esta respondendo corretamente")
    except:
        print("[ERRO] Frontend nao esta acessivel")

def main():
    """Função principal"""
    print("COSMOS SENTINEL - TESTE DE COMUNICACAO")
    print("=" * 60)
    
    # Verificar serviços
    check_services()
    
    # Testar backend
    test_backend()
    
    # Testar comunicação frontend-backend
    test_frontend_connection()
    
    print("\nRESUMO:")
    print("=" * 60)
    print("1. Se todos os testes passaram, o frontend deve conseguir")
    print("   se comunicar com o backend normalmente.")
    print("2. Se houver erros, verifique se ambos os serviços estao rodando.")
    print("3. Acesse http://localhost:3000 para ver o frontend.")
    print("4. Acesse http://localhost:8000/docs para ver a API do backend.")

if __name__ == "__main__":
    main()
