#!/usr/bin/env python3
"""
Script para iniciar o COSMOS SENTINEL completo (Backend + Frontend)
"""

import subprocess
import time
import webbrowser
import os
import sys
import threading
import requests

def start_backend():
    """Inicia o servidor backend"""
    print("🚀 Iniciando Backend COSMOS SENTINEL...")
    try:
        # Mudar para diretório backend
        os.chdir('../backend')
        
        # Iniciar servidor backend
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main_simple:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar servidor iniciar
        time.sleep(3)
        
        # Verificar se está funcionando
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado com sucesso!")
                return process
            else:
                print("❌ Backend não respondeu corretamente")
                return None
        except:
            print("❌ Backend não está acessível")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o servidor frontend"""
    print("🌐 Iniciando Frontend COSMOS SENTINEL...")
    try:
        # Mudar para diretório frontend
        os.chdir('../frontend')
        
        # Iniciar servidor frontend
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar servidor iniciar
        time.sleep(2)
        
        print("✅ Frontend iniciado com sucesso!")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def main():
    """Função principal"""
    print("🧭 COSMOS SENTINEL - Sistema Completo")
    print("=" * 60)
    
    # Verificar estrutura de diretórios
    if not os.path.exists("../backend/main_simple.py"):
        print("❌ Arquivo main_simple.py não encontrado no backend!")
        return False
    
    if not os.path.exists("../frontend/index.html"):
        print("❌ Arquivo index.html não encontrado no frontend!")
        return False
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Falha ao iniciar backend")
        return False
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Falha ao iniciar frontend")
        backend_process.terminate()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 COSMOS SENTINEL INICIADO COM SUCESSO!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend:  http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n🛑 Pressione Ctrl+C para parar tudo")
    
    # Abrir navegador
    time.sleep(2)
    webbrowser.open('http://localhost:3000')
    
    try:
        # Manter servidores rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            if backend_process.poll() is not None:
                print("❌ Backend parou inesperadamente")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Parando COSMOS SENTINEL...")
        
        # Parar processos
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend parado")
            
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ Frontend parado")
            
        print("🎯 Sistema parado com sucesso!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
