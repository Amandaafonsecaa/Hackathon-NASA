#!/usr/bin/env python3
"""
Script simples para testar apenas o backend
"""

import subprocess
import time
import os
import sys
import requests

def test_backend():
    """Testa apenas o backend"""
    print("TESTE DO BACKEND COSMOS SENTINEL")
    print("=" * 50)
    
    # Verificar se o arquivo existe
    if not os.path.exists("backend/main_simple.py"):
        print("[ERRO] Arquivo main_simple.py não encontrado no backend!")
        return False
    
    print("[OK] Arquivo main_simple.py encontrado!")
    
    # Mudar para diretório backend
    print("[INFO] Mudando para diretório backend...")
    os.chdir('backend')
    
    try:
        # Tentar iniciar o servidor
        print("[INFO] Iniciando servidor backend...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main_simple:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar servidor iniciar
        print("[INFO] Aguardando servidor iniciar...")
        time.sleep(5)
        
        # Verificar se está funcionando
        print("[INFO] Testando conexão...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("[SUCCESS] Backend funcionando!")
                print(f"Resposta: {response.json()}")
                return True
            else:
                print(f"[ERRO] Backend respondeu com status: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERRO] Não foi possível conectar ao backend: {e}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao iniciar backend: {e}")
        return False
    finally:
        # Voltar para diretório pai
        os.chdir('..')

if __name__ == "__main__":
    success = test_backend()
    if success:
        print("\n[SUCCESS] Teste do backend concluído com sucesso!")
    else:
        print("\n[ERRO] Teste do backend falhou!")
    sys.exit(0 if success else 1)
