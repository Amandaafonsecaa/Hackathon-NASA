import math
import numpy as np
from typing import Dict, List, Tuple

# --- Módulos de Cálculo Individuais (Refatorados como funções privadas) ---

def _calculate_energy_and_mass(diameter_m, velocity_kms, densidade_impactor=3000):
    v_ms = velocity_kms * 1000.0
    mass_kg = densidade_impactor * (math.pi / 6.0) * (diameter_m ** 3)
    energy_joules = 0.5 * mass_kg * v_ms ** 2
    return energy_joules, mass_kg

def _calculate_crater(energy_joules, diameter_m, velocity_kms, angulo_graus, tipo_terreno, densidade_impactor, rho_t):
    """
    Calcula cratera apenas para impactos diretos (não airburst).
    Para airburst, retorna valores zero pois não há cratera.
    """
    # Determinar se é airburst baseado no diâmetro e tipo de terreno
    is_airburst = diameter_m <= 150 and tipo_terreno != "oceano"
    
    if is_airburst:
        return {
            "diametro_final_km": 0.0,
            "profundidade_m": 0.0,
            "is_airburst": True,
            "explanation": "Airburst - explosão atmosférica sem cratera"
        }
    
    # Cálculo de cratera apenas para impactos diretos
    g = 9.81
    v_ms = velocity_kms * 1000
    # Fórmula de Holsapple-Schmidt simplificada
    D_t = 1.161 * (g ** -0.17) * ((densidade_impactor / rho_t) ** 0.333) * \
          ((v_ms * math.sin(math.radians(angulo_graus))) ** 0.83) * (diameter_m ** 0.78)
    D_f = 1.25 * D_t
    profundidade = 0.2 * D_f
    return {
        "diametro_final_km": D_f / 1000,
        "profundidade_m": profundidade,
        "is_airburst": False,
        "explanation": "Impacto direto - cratera formada"
    }

def _calculate_fireball(energy_joules, diameter_m, tipo_terreno):
    is_airburst = diameter_m <= 150 and tipo_terreno != "oceano"
    eta_thermal = 0.35 if is_airburst else 0.15
    E_thermal = eta_thermal * energy_joules
    E_tnt_tons = E_thermal / 4.184e9

    def raio_km_para_fluencia(F_joules_m2):
        return math.sqrt(E_thermal / (4 * math.pi * F_joules_m2)) / 1000
    
    # Fluências para queimaduras de 3º, 2º e 1º grau (J/m²)
    R_L3_km = raio_km_para_fluencia(5.0e5) # 3rd degree
    R_L2_km = raio_km_para_fluencia(2.5e5) # 2nd degree
    R_L1_km = raio_km_para_fluencia(1.2e5) # 1st degree

    return {
        "is_airburst": is_airburst,
        "energia_thermal_tnt_tons": E_tnt_tons,
        "raio_queimadura_3_grau_km": R_L3_km,
        "raio_queimadura_2_grau_km": R_L2_km,
        "raio_queimadura_1_grau_km": R_L1_km,
    }

def _calculate_shockwave_and_wind(energy_joules, diameter_m, tipo_terreno):
    is_airburst = diameter_m <= 150 and tipo_terreno != "oceano"
    eta_blast = 0.3 if is_airburst else 0.1
    E_blast = eta_blast * energy_joules
    W_tons = E_blast / 4.184e9

    Z_tab = {5: 17.0, 3: 24.0, 1: 50.0} # Distância reduzida para sobrepressão

    def radius_km_for_psi(psi):
        Z = Z_tab[psi]
        R_m = Z * (W_tons ** (1.0/3.0))
        return R_m / 1000.0

    radii_km = {
        "psi_5_predios_destruidos": radius_km_for_psi(5),
        "psi_3_casas_destruidas": radius_km_for_psi(3),
        "psi_1_janelas_quebradas": radius_km_for_psi(1)
    }

    rho_air = 1.225
    PSI_TO_PA = 6894.757
    def wind_ms_from_psi(psi):
        dP = psi * PSI_TO_PA
        return math.sqrt(max(0.0, 2.0 * dP / rho_air))

    peak_wind_ms = wind_ms_from_psi(5)
    
    if peak_wind_ms >= 89: ef = "EF5 (Danos incríveis)"
    elif peak_wind_ms >= 74: ef = "EF4 (Danos devastadores)"
    elif peak_wind_ms >= 60: ef = "EF3 (Danos severos)"
    else: ef = "EF2 ou inferior"

    P0_ref = 2e-5 # Pressão de referência audível em Pa
    P_max_pa = 5 * PSI_TO_PA
    db_level = 20 * math.log10(P_max_pa / P0_ref) if P_max_pa > P0_ref else 0
    
    return {
        "energia_explosao_tnt_tons": W_tons,
        "raios_sobrepressao_km": radii_km,
        "pico_vento_ms": peak_wind_ms,
        "escala_fujita_equivalente": ef,
        "nivel_som_1km_db": round(db_level, 1)
    }

def _calculate_earthquake(energy_joules):
    eta_s = 5e-4
    E_sismica = eta_s * energy_joules
    M = (2/3) * math.log10(E_sismica) - 3.2
    return {
        "magnitude_richter": round(M, 1),
        "distancia_sentida_km": round(10 ** ((0.5 * M) - 0.8), 0)
    }

def _calculate_tsunami(energy_joules, diameter_m, tipo_terreno, depth_ocean_m=4000):
    """
    Calcula os efeitos de tsunami para impactos oceânicos.
    Baseado em modelos de Ward & Asphaug (2000) e Gisler et al. (2003).
    """
    if tipo_terreno != "oceano":
        return {
            "tsunami_generated": False,
            "wave_height_m": 0,
            "runup_distance_km": 0,
            "coastal_impact": "Nenhum tsunami gerado"
        }
    
    # Parâmetros do impacto oceânico
    v_ms = 17000  # Velocidade típica de impacto
    rho_water = 1000  # Densidade da água
    rho_impactor = 3000  # Densidade do impactor
    
    # Cálculo da altura da onda inicial
    # Baseado no modelo de Ward & Asphaug
    mass_kg = rho_impactor * (math.pi / 6.0) * (diameter_m ** 3)
    momentum = mass_kg * v_ms
    
    # Altura da onda inicial (simplificada)
    H0 = 0.5 * (momentum / (rho_water * depth_ocean_m)) ** 0.5
    
    # Propagação da onda (considerando dispersão)
    # Para distâncias típicas de 100-1000 km
    distances_km = [100, 200, 500, 1000]
    wave_heights = []
    
    for dist in distances_km:
        # Atenuação com a distância (lei de potência)
        H = H0 * (100 / dist) ** 0.5
        wave_heights.append({
            "distance_km": dist,
            "wave_height_m": max(0.1, H)
        })
    
    # Runup máximo (altura da onda na costa)
    max_runup = H0 * 2.0  # Fator de amplificação na costa
    
    return {
        "tsunami_generated": True,
        "initial_wave_height_m": round(H0, 2),
        "max_runup_m": round(max_runup, 2),
        "wave_propagation": wave_heights,
        "coastal_impact": f"Tsunami com runup de até {max_runup:.1f}m na costa"
    }

def _calculate_atmospheric_dispersion(energy_joules, diameter_m, tipo_terreno, wind_speed_ms=10, wind_direction_deg=0):
    """
    Calcula a dispersão atmosférica de poluentes após airburst.
    Baseado em modelos de dispersão gaussiana e dados de vento.
    """
    if tipo_terreno == "oceano" or diameter_m > 150:
        return {
            "atmospheric_dispersion": False,
            "pollutant_plume": None,
            "air_quality_impact": "Dispersão atmosférica limitada"
        }
    
    # Parâmetros da explosão aérea
    is_airburst = diameter_m <= 150
    if not is_airburst:
        return {
            "atmospheric_dispersion": False,
            "pollutant_plume": None,
            "air_quality_impact": "Não é airburst - dispersão limitada"
        }
    
    # Cálculo da pluma de poluentes
    # NOx, partículas finas, etc.
    eta_airburst = 0.35  # Fração de energia para airburst
    E_airburst = eta_airburst * energy_joules
    
    # Altura da explosão (baseada no diâmetro)
    burst_height_km = diameter_m / 1000.0 * 10  # Altura proporcional ao tamanho
    
    # Cálculo da pluma de dispersão
    # Modelo gaussiano simplificado
    sigma_y = 0.1 * burst_height_km  # Desvio padrão lateral
    sigma_z = 0.05 * burst_height_km  # Desvio padrão vertical
    
    # Zonas de concentração de poluentes
    concentration_zones = []
    for distance_km in [10, 25, 50, 100, 200]:
        # Concentração decai com a distância
        concentration = math.exp(-(distance_km ** 2) / (2 * sigma_y ** 2))
        
        # Classificação de risco baseada na concentração
        if concentration > 0.8:
            risk_level = "Crítico"
        elif concentration > 0.5:
            risk_level = "Alto"
        elif concentration > 0.2:
            risk_level = "Moderado"
        else:
            risk_level = "Baixo"
        
        concentration_zones.append({
            "distance_km": distance_km,
            "concentration_factor": round(concentration, 3),
            "risk_level": risk_level,
            "pollutants": ["NOx", "PM2.5", "PM10", "Ozone"]
        })
    
    return {
        "atmospheric_dispersion": True,
        "burst_height_km": round(burst_height_km, 2),
        "plume_dispersion": {
            "sigma_y_km": round(sigma_y, 2),
            "sigma_z_km": round(sigma_z, 2),
            "wind_speed_ms": wind_speed_ms,
            "wind_direction_deg": wind_direction_deg
        },
        "concentration_zones": concentration_zones,
        "air_quality_impact": f"Pluma de poluentes até {max([z['distance_km'] for z in concentration_zones])}km"
    }

# --- Função Principal do Serviço ---

def calculate_all_impact_effects(
    diameter_m: float, 
    velocity_kms: float, 
    impact_angle_deg: float,
    tipo_terreno: str,
    densidade_impactor: int = 3000,
    wind_speed_ms: float = 10,
    wind_direction_deg: float = 0
):
    """
    Orquestra todos os cálculos de impacto e retorna um relatório unificado.
    Inclui cálculos de tsunami e dispersão atmosférica.
    """
    densidades_alvo = {"solo": 2000, "rocha": 2500, "oceano": 1000}
    rho_t = densidades_alvo.get(tipo_terreno, 2000)

    # Calcular energia uma única vez
    energy_joules, mass_kg = _calculate_energy_and_mass(diameter_m, velocity_kms, densidade_impactor)
    
    # Executar todos os módulos de cálculo
    crater_results = _calculate_crater(energy_joules, diameter_m, velocity_kms, impact_angle_deg, tipo_terreno, densidade_impactor, rho_t)
    fireball_results = _calculate_fireball(energy_joules, diameter_m, tipo_terreno)
    shockwave_results = _calculate_shockwave_and_wind(energy_joules, diameter_m, tipo_terreno)
    earthquake_results = _calculate_earthquake(energy_joules)
    tsunami_results = _calculate_tsunami(energy_joules, diameter_m, tipo_terreno)
    dispersion_results = _calculate_atmospheric_dispersion(energy_joules, diameter_m, tipo_terreno, wind_speed_ms, wind_direction_deg)

    # Compilar relatório final
    return {
        "inputs": {
            "diametro_m": diameter_m, 
            "velocidade_kms": velocity_kms, 
            "angulo_graus": impact_angle_deg,
            "tipo_terreno": tipo_terreno, 
            "densidade_impactor_kgm3": densidade_impactor,
            "wind_speed_ms": wind_speed_ms,
            "wind_direction_deg": wind_direction_deg
        },
        "energia": {
            "energia_total_joules": f"{energy_joules:.2e}",
            "equivalente_tnt_megatons": round(energy_joules / 4.184e15, 2),
            "equivalente_bombas_hiroshima": round(energy_joules / (15 * 4.184e12))
        },
        "cratera": crater_results,
        "fireball": fireball_results,
        "onda_de_choque_e_vento": shockwave_results,
        "terremoto": earthquake_results,
        "tsunami": tsunami_results,
        "dispersao_atmosferica": dispersion_results
    }