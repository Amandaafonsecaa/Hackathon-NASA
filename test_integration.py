#!/usr/bin/env python3
"""
Script para testar a integração completa Frontend-Backend
"""

import requests
import json

def test_backend_response():
    """Testa se o backend está retornando dados corretos"""
    print("TESTANDO RESPOSTA DO BACKEND")
    print("=" * 50)
    
    url = "http://localhost:8000/api/v1/simular"
    data = {
        "diameter_m": 100,
        "velocity_kms": 35,
        "impact_angle_deg": 24,
        "target_type": "rocha"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Backend respondeu com sucesso!")
            print(f"Dados - Energia: {result['energia']['equivalente_tnt_megatons']} MT")
            print(f"Dados - Airburst: {result['cratera']['is_airburst']}")
            print(f"Dados - Cratera: {result['cratera']['diametro_final_km']} km")
            print(f"Dados - Fireball: {result['fireball']['raio_queimadura_3_grau_km']} km")
            print(f"Dados - Terremoto: {result['terremoto']['magnitude_richter']} Richter")
            print(f"Dados - Som: {result['onda_de_choque_e_vento']['nivel_som_1km_db']} dB")
            return result
        else:
            print(f"[ERRO] Erro no backend: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro ao conectar com backend: {e}")
        return None

def test_frontend_cors():
    """Testa se o CORS está funcionando"""
    print("\nTESTANDO CORS")
    print("=" * 50)
    
    try:
        # Simular requisição do frontend
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }
        
        response = requests.options("http://localhost:8000/api/v1/simular", headers=headers)
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("[OK] CORS configurado corretamente")
            print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        else:
            print("[ERRO] CORS nao configurado")
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar CORS: {e}")

def compare_data_structures():
    """Compara estrutura de dados esperada vs real"""
    print("\nCOMPARANDO ESTRUTURAS DE DADOS")
    print("=" * 50)
    
    backend_data = test_backend_response()
    
    if backend_data:
        print("\nESTRUTURA DO BACKEND:")
        print(f"   energia.equivalente_tnt_megatons: {backend_data['energia']['equivalente_tnt_megatons']}")
        print(f"   terremoto.magnitude_richter: {backend_data['terremoto']['magnitude_richter']}")
        print(f"   cratera.diametro_final_km: {backend_data['cratera']['diametro_final_km']}")
        print(f"   fireball.raio_queimadura_3_grau_km: {backend_data['fireball']['raio_queimadura_3_grau_km']}")
        print(f"   onda_de_choque_e_vento.nivel_som_1km_db: {backend_data['onda_de_choque_e_vento']['nivel_som_1km_db']}")
        print(f"   onda_de_choque_e_vento.pico_vento_ms: {backend_data['onda_de_choque_e_vento']['pico_vento_ms']}")
        
        print("\nESTRUTURA ESPERADA PELO FRONTEND:")
        print("   impact_energy_mt")
        print("   seismic_magnitude")
        print("   crater_diameter_km")
        print("   fireball_radius_km")
        print("   shockwave_intensity_db")
        print("   peak_winds_kmh")
        
        print("\nMAPEAMENTO CORRETO:")
        print(f"   impact_energy_mt = {backend_data['energia']['equivalente_tnt_megatons']}")
        print(f"   seismic_magnitude = {backend_data['terremoto']['magnitude_richter']}")
        print(f"   crater_diameter_km = {backend_data['cratera']['diametro_final_km']}")
        print(f"   fireball_radius_km = {backend_data['fireball']['raio_queimadura_3_grau_km']}")
        print(f"   shockwave_intensity_db = {backend_data['onda_de_choque_e_vento']['nivel_som_1km_db']}")
        print(f"   peak_winds_kmh = {backend_data['onda_de_choque_e_vento']['pico_vento_ms'] * 3.6}")

def main():
    """Função principal"""
    print("TESTE DE INTEGRACAO FRONTEND-BACKEND")
    print("=" * 60)
    
    # Testar backend
    test_backend_response()
    
    # Testar CORS
    test_frontend_cors()
    
    # Comparar estruturas
    compare_data_structures()
    
    print("\nPROXIMOS PASSOS:")
    print("1. Acesse http://localhost:3000")
    print("2. Execute uma simulacao")
    print("3. Verifique o console do navegador (F12)")
    print("4. Os dados devem vir do backend agora")

if __name__ == "__main__":
    main()
