#!/usr/bin/env python3
"""
Script para testar o COSMOS SENTINEL completo
"""

import requests
import time
import webbrowser
import subprocess
import sys
import os

def test_backend():
    """Testa se o backend está funcionando"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando")
            return True
        else:
            print("❌ Backend com problemas")
            return False
    except:
        print("❌ Backend offline")
        return False

def test_frontend():
    """Testa se o frontend está funcionando"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend funcionando")
            return True
        else:
            print("❌ Frontend com problemas")
            return False
    except:
        print("❌ Frontend offline")
        return False

def main():
    """Função principal"""
    print("🧭 COSMOS SENTINEL - TESTE COMPLETO")
    print("=" * 50)
    
    print("🔍 Verificando serviços...")
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 50)
    
    if backend_ok and frontend_ok:
        print("🎉 SISTEMA COMPLETO FUNCIONANDO!")
        print("\n🌐 Acesse o sistema:")
        print("   Frontend: http://localhost:3000")
        print("   Backend:  http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        
        # Abrir navegador
        print("\n🚀 Abrindo navegador...")
        webbrowser.open('http://localhost:3000')
        
        return True
    else:
        print("⚠️  ALGUNS SERVIÇOS NÃO ESTÃO FUNCIONANDO")
        print("\n💡 Para iniciar os serviços:")
        print("   1. Backend:  cd backend && uvicorn main_simple:app --host 0.0.0.0 --port 8000")
        print("   2. Frontend: cd frontend && python -m http.server 3000")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
