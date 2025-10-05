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

def install_backend_dependencies():
    """Instala dependências do backend"""
    print("[INFO] Instalando dependências do backend...")
    try:
        os.chdir('backend')
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Dependências do backend instaladas!")
            return True
        else:
            print(f"[ERRO] Erro ao instalar dependências: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao instalar dependências: {e}")
        return False
    finally:
        os.chdir('..')

def install_frontend_dependencies():
    """Instala dependências do frontend"""
    print("[INFO] Instalando dependências do frontend...")
    try:
        os.chdir('frontend')
        result = subprocess.run([
            "cmd", "/c", "npm", "install"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Dependências do frontend instaladas!")
            return True
        else:
            print(f"[ERRO] Erro ao instalar dependências: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao instalar dependências: {e}")
        return False
    finally:
        os.chdir('..')

def start_backend():
    """Inicia o servidor backend"""
    print("[INFO] Iniciando Backend COSMOS SENTINEL...")
    try:
        # Salvar diretório atual
        original_dir = os.getcwd()
        
        # Mudar para diretório backend
        os.chdir('backend')
        
        # Iniciar servidor backend
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main_simple:app", 
            "--host", "0.0.0.0", 
            "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Voltar para diretório original
        os.chdir(original_dir)
        
        # Aguardar servidor iniciar
        time.sleep(3)
        
        # Verificar se está funcionando
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("[OK] Backend iniciado com sucesso!")
                return process
            else:
                print("[ERRO] Backend não respondeu corretamente")
                return None
        except:
            print("[ERRO] Backend não está acessível")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Inicia o servidor frontend"""
    print("[INFO] Iniciando Frontend COSMOS SENTINEL...")
    try:
        # Salvar diretório atual
        original_dir = os.getcwd()
        
        # Mudar para diretório frontend
        os.chdir('frontend')
        
        # Iniciar servidor frontend React
        process = subprocess.Popen([
            "cmd", "/c", "npm", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Voltar para diretório original
        os.chdir(original_dir)
        
        # Aguardar servidor iniciar
        time.sleep(5)
        
        print("[OK] Frontend iniciado com sucesso!")
        return process
        
    except Exception as e:
        print(f"[ERRO] Erro ao iniciar frontend: {e}")
        return None

def main():
    """Função principal"""
    print("COSMOS SENTINEL - Sistema Completo")
    print("=" * 60)
    
    # Verificar estrutura de diretórios
    if not os.path.exists("backend/main_simple.py"):
        print("[ERRO] Arquivo main_simple.py não encontrado no backend!")
        return False
    
    if not os.path.exists("frontend/public/index.html"):
        print("[ERRO] Arquivo index.html não encontrado no frontend!")
        return False
    
    # Instalar dependências
    print("\n[INFO] Instalando dependências...")
    if not install_backend_dependencies():
        print("[ERRO] Falha ao instalar dependências do backend")
        return False
    
    if not install_frontend_dependencies():
        print("[ERRO] Falha ao instalar dependências do frontend")
        return False
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("[ERRO] Falha ao iniciar backend")
        return False
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("[ERRO] Falha ao iniciar frontend")
        backend_process.terminate()
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] COSMOS SENTINEL INICIADO COM SUCESSO!")
    print("=" * 60)
    print("Frontend: http://localhost:3000")
    print("Backend:  http://localhost:8001")
    print("API Docs: http://localhost:8001/docs")
    print("\nPressione Ctrl+C para parar tudo")
    
    # Abrir navegador
    time.sleep(2)
    webbrowser.open('http://localhost:3000')
    
    try:
        # Manter servidores rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            if backend_process.poll() is not None:
                print("[ERRO] Backend parou inesperadamente")
                break
                
            if frontend_process.poll() is not None:
                print("[ERRO] Frontend parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n[INFO] Parando COSMOS SENTINEL...")
        
        # Parar processos
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("[OK] Backend parado")
            
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("[OK] Frontend parado")
            
        print("[SUCCESS] Sistema parado com sucesso!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
