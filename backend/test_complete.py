#!/usr/bin/env python3
"""
Script completo para testar o backend COSMOS SENTINEL
Inicia o servidor e testa todos os endpoints
"""

import subprocess
import time
import requests
import sys
import os


def start_server():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando servidor FastAPI...")
    try:
        # Iniciar servidor em background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "main_simple:app",
            "--host", "0.0.0.0",
            "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Aguardar servidor iniciar
        time.sleep(3)

        # Verificar se o servidor está rodando
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso!")
                return process
            else:
                print("❌ Servidor não respondeu corretamente")
                return None
        except:
            print("❌ Servidor não está acessível")
            return None

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None


def test_endpoints():
    """Testa todos os endpoints"""
    print("\n🔍 Testando endpoints...")
    print("-" * 40)

    base_url = "http://localhost:8001"

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

    results = []
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                results.append(True)
            else:
                print(f"❌ {name}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: Erro - {e}")
            results.append(False)

        time.sleep(0.1)

    return results


def main():
    """Função principal"""
    print("🧭 COSMOS SENTINEL - TESTE COMPLETO DO BACKEND")
    print("=" * 60)

    # Verificar se estamos no diretório correto
    if not os.path.exists("main_simple.py"):
        print("❌ Arquivo main_simple.py não encontrado!")
        print("💡 Execute este script no diretório backend/")
        return False

    # Iniciar servidor
    server_process = start_server()
    if not server_process:
        print("❌ Não foi possível iniciar o servidor")
        return False

    try:
        # Testar endpoints
        results = test_endpoints()

        # Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)

        passed = sum(results)
        total = len(results)

        print(f"🎯 RESULTADO FINAL: {passed}/{total} endpoints funcionando")

        if passed == total:
            print("🎉 TODOS OS ENDPOINTS ESTÃO FUNCIONANDO!")
            print("✅ Backend COSMOS SENTINEL está pronto para uso!")
            print("\n🌐 Acesse: http://localhost:8001")
            print("📚 Documentação: http://localhost:8001/docs")
        else:
            print("⚠️  ALGUNS ENDPOINTS FALHARAM.")
            print("💡 Verifique os erros acima.")

        return passed == total

    finally:
        # Parar servidor
        if server_process:
            print("\n🛑 Parando servidor...")
            server_process.terminate()
            server_process.wait()
            print("✅ Servidor parado.")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
