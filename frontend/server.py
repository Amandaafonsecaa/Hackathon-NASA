#!/usr/bin/env python3
"""
Servidor simples para servir o frontend do COSMOS SENTINEL
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os
import sys

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Função principal"""
    print("🌐 COSMOS SENTINEL - Servidor Frontend")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("index.html"):
        print("❌ Arquivo index.html não encontrado!")
        print("💡 Execute este script no diretório frontend/")
        return False
    
    port = 3000
    
    try:
        # Criar servidor
        server = HTTPServer(('localhost', port), CORSRequestHandler)
        
        print(f"🚀 Servidor iniciado em http://localhost:{port}")
        print("📱 Frontend disponível em:")
        print(f"   http://localhost:{port}")
        print("\n💡 Certifique-se de que o backend está rodando em http://localhost:8000")
        print("\n🛑 Pressione Ctrl+C para parar o servidor")
        
        # Abrir navegador automaticamente
        webbrowser.open(f'http://localhost:{port}')
        
        # Iniciar servidor
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
