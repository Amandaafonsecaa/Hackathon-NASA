#!/usr/bin/env python3
"""
Script de teste rápido para o backend COSMOS SENTINEL
"""

import requests
import time
import json


def test_endpoint(url, name):
    """Testa um endpoint específico"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Erro - {e}")
        return False


def main():
    """Função principal de teste"""
    print("🚀 COSMOS SENTINEL - TESTE DO BACKEND")
    print("=" * 50)

    base_url = "http://localhost:8000"

    endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/api/v1/neo/test", "NASA NEOs"),
        ("/api/v1/simular/test", "Simulação"),
        ("/api/v1/risco-local/test", "Risco Local"),
        ("/api/v1/evacuacao/test", "Evacuação"),
        ("/api/v1/saude/test", "Saúde"),
        ("/api/v1/ambiental/test", "Ambiental"),
        ("/api/v1/populacao/test", "População"),
        ("/api/v1/defesa-civil/test", "Defesa Civil"),
        ("/api/v1/traffic-ai/test", "IA Tráfego"),
        ("/api/v1/evacuation-ai/test", "IA Integrada"),
        ("/api/v1/test-all", "Teste Completo")
    ]

    print("🔍 Testando endpoints...")
    print("-" * 30)

    results = []
    for endpoint, name in endpoints:
        success = test_endpoint(f"{base_url}{endpoint}", name)
        results.append(success)
        time.sleep(0.1)  # Pequena pausa entre testes

    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (endpoint, name) in enumerate(endpoints):
        status = "✅ PASSOU" if results[i] else "❌ FALHOU"
        print(f"{status} - {name}")

    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} endpoints funcionando")

    if passed == total:
        print("🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
        print("✅ Backend pronto para uso!")
    else:
        print("⚠️  ALGUNS ENDPOINTS FALHARAM.")
        print("💡 Verifique se o servidor está rodando em http://localhost:8000")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
