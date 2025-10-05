import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import { cosmosAPI } from '../services/apiService';
import 'leaflet/dist/leaflet.css';

// Configurar ícones do Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const AsteroidDashboard = () => {
  // Estados principais - Design Original IMPACTOR-2025
  const [asteroidDiameter, setAsteroidDiameter] = useState(100); // metros
  const [impactVelocity, setImpactVelocity] = useState(35); // km/s
  const [impactAngle, setImpactAngle] = useState(24); // graus
  const [latitude, setLatitude] = useState(-3.7327);
  const [longitude, setLongitude] = useState(-38.5270);
  const [mitigationStrategy, setMitigationStrategy] = useState('Nenhuma');
  const [deflectionTime, setDeflectionTime] = useState(15); // dias
  const [timeToImpact, setTimeToImpact] = useState(72); // horas
  const [populationAtRisk, setPopulationAtRisk] = useState(2.5); // milhões
  const [safeSimulationResults, setSimulationResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [usingBackend, setUsingBackend] = useState(false);

  // Testar conexão com backend
  useEffect(() => {
    const testBackendConnection = async () => {
      try {
        const result = await cosmosAPI.testConnection();
        setBackendConnected(result.success);
        } catch (error) {
        setBackendConnected(false);
      }
    };
    
    testBackendConnection();
  }, []);

  // Função para executar simulação
  const runSimulation = async () => {
    setLoading(true);
    
    try {
      // Sempre tentar usar o backend primeiro
      const simulationData = {
        diameter_m: asteroidDiameter,
        velocity_kms: impactVelocity,
        impact_angle_deg: impactAngle,
        target_type: 'rocha',
        latitude: latitude,
        longitude: longitude
      };
      
      console.log('Enviando dados para simulação:', simulationData);
      
      const result = await cosmosAPI.simulateImpact(simulationData);
      
      console.log('Resultado da API:', result);
      
      if (result.success && result.data) {
        console.log('Dados recebidos do backend:', result.data);
        
        // Mapear dados do backend para estrutura esperada pelo frontend
        const backendData = result.data;
        const mappedData = {
          impact_energy_mt: backendData.energia?.equivalente_tnt_megatons || 0,
          seismic_magnitude: backendData.terremoto?.magnitude_richter || 0,
          crater_diameter_km: backendData.cratera?.diametro_final_km || 0,
          fireball_radius_km: backendData.fireball?.raio_queimadura_3_grau_km || 0,
          shockwave_intensity_db: backendData.onda_de_choque_e_vento?.nivel_som_1km_db || 0,
          peak_winds_kmh: (backendData.onda_de_choque_e_vento?.pico_vento_ms || 0) * 3.6, // converter m/s para km/h
          impact_type: backendData.cratera?.is_airburst ? 'AIRBURST' : 'IMPACTO DIRETO',
          // Calcular vítimas baseado na energia
          fireball_victims: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 3000),
          burn_victims: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 8000),
          shockwave_victims: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 5000),
          burned_trees: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 1000),
          collapsed_houses: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 1500),
          fallen_trees: Math.round((backendData.energia?.equivalente_tnt_megatons || 0) * 2000),
          frequency: (backendData.energia?.equivalente_tnt_megatons || 0) > 20 ? '1 em 500 anos' : 
                    (backendData.energia?.equivalente_tnt_megatons || 0) > 10 ? '1 em 1000 anos' : '1 em 2000 anos'
        };
        
        console.log('Dados mapeados:', mappedData);
        setSimulationResults(mappedData);
        setUsingBackend(true);
      } else {
        console.log('Backend não respondeu, usando cálculo local baseado nos parâmetros');
        // Cálculo local baseado nos parâmetros reais
        const energy = Math.pow(asteroidDiameter / 100, 3) * Math.pow(impactVelocity / 20, 2) * 0.5;
        
        // Determinar tipo de impacto baseado no diâmetro (lógica científica correta)
        const isAirburst = asteroidDiameter <= 150; // Asteroides <= 150m geralmente explodem na atmosfera
        const impactType = isAirburst ? 'AIRBURST' : 'IMPACTO DIRETO';
        
        // Calcular cratera apenas para impactos diretos
        const craterSize = isAirburst ? 0 : asteroidDiameter * 0.02; // 2% do diâmetro apenas para impactos diretos
        const fireballRadius = asteroidDiameter * 0.01; // Raio da bola de fogo independente do tipo
        
        const results = {
          impact_energy_mt: Math.round(energy * 10) / 10,
          seismic_magnitude: Math.round((Math.log10(energy) + 4) * 10) / 10,
          crater_diameter_km: Math.round(craterSize * 10) / 10,
          fireball_radius_km: Math.round(fireballRadius * 10) / 10,
          shockwave_intensity_db: Math.round(120 + (energy * 2)),
          peak_winds_kmh: Math.round(200 + (energy * 10)),
          impact_type: impactType,
          fireball_victims: Math.round(energy * 3000),
          burn_victims: Math.round(energy * 8000),
          shockwave_victims: Math.round(energy * 5000),
          burned_trees: Math.round(energy * 1000),
          collapsed_houses: Math.round(energy * 1500),
          fallen_trees: Math.round(energy * 2000),
          frequency: energy > 20 ? '1 em 500 anos' : energy > 10 ? '1 em 1000 anos' : '1 em 2000 anos'
        };
        
        setSimulationResults(results);
        setUsingBackend(false);
      }
      } catch (error) {
      console.error('Erro ao executar simulação:', error);
      
      // Fallback com cálculo baseado nos parâmetros
      const energy = Math.pow(asteroidDiameter / 100, 3) * Math.pow(impactVelocity / 20, 2) * 0.5;
      
      // Determinar tipo de impacto baseado no diâmetro (lógica científica correta)
      const isAirburst = asteroidDiameter <= 150; // Asteroides <= 150m geralmente explodem na atmosfera
      const impactType = isAirburst ? 'AIRBURST' : 'IMPACTO DIRETO';
      
      // Calcular cratera apenas para impactos diretos
      const craterSize = isAirburst ? 0 : asteroidDiameter * 0.02; // 2% do diâmetro apenas para impactos diretos
      const fireballRadius = asteroidDiameter * 0.01; // Raio da bola de fogo independente do tipo
      
      const results = {
        impact_energy_mt: Math.round(energy * 10) / 10,
        seismic_magnitude: Math.round((Math.log10(energy) + 4) * 10) / 10,
        crater_diameter_km: Math.round(craterSize * 10) / 10,
        fireball_radius_km: Math.round(fireballRadius * 10) / 10,
        shockwave_intensity_db: Math.round(120 + (energy * 2)),
        peak_winds_kmh: Math.round(200 + (energy * 10)),
        impact_type: impactType,
        fireball_victims: Math.round(energy * 3000),
        burn_victims: Math.round(energy * 8000),
        shockwave_victims: Math.round(energy * 5000),
        burned_trees: Math.round(energy * 1000),
        collapsed_houses: Math.round(energy * 1500),
        fallen_trees: Math.round(energy * 2000),
        frequency: energy > 20 ? '1 em 500 anos' : energy > 10 ? '1 em 1000 anos' : '1 em 2000 anos'
      };
      
      setSimulationResults(results);
      setUsingBackend(false);
    } finally {
      setLoading(false);
    }
  };

  // Verificação de segurança para safeSimulationResults
  const safeSimulationResults = safeSimulationResults || {
    impact_energy_mt: 0,
    seismic_magnitude: 0,
    crater_diameter_km: 0,
    fireball_radius_km: 0,
    shockwave_intensity_db: 0,
    peak_winds_kmh: 0,
    impact_type: 'IMPACTO DIRETO',
    fireball_victims: 0,
    burn_victims: 0,
    shockwave_victims: 0,
    burned_trees: 0,
    collapsed_houses: 0,
    fallen_trees: 0,
    frequency: 'N/A'
  };

  return (
    <div className="min-h-screen bg-blue-900 text-white">
      {/* Header */}
      <div className="bg-blue-800 border-b border-blue-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-2xl font-bold text-white">IMPACTOR-2025</h1>
              <p className="text-blue-200 text-sm">NASA Space Apps Challenge</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
          <div className="text-right">
              <div className="text-sm text-blue-200">STATUS: MONITORAMENTO ATIVO</div>
              <div className="text-sm text-green-400">CONEXÃO: ONLINE</div>
              {safeSimulationResults && (
                <div className={`text-xs mt-1 ${usingBackend ? 'text-green-400' : 'text-yellow-400'}`}>
                  {usingBackend ? '✓ Backend API' : '⚠ Cálculo Local'}
              </div>
            )}
            </div>
              <button
                onClick={() => window.location.href = '?dashboard=government'}
              className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-white font-medium"
              >
              Dashboard Governamental
              </button>
            </div>
          </div>
        </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* PAINEL ESQUERDO - Parâmetros de Simulação */}
          <div className="space-y-6">
            
            <div className="bg-blue-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-6">Parâmetros de Simulação</h2>
              
              <div className="space-y-6">
                
                {/* Diâmetro do Asteroide */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Diâmetro do Asteroide: {asteroidDiameter}m
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="1000"
                    value={asteroidDiameter}
                    onChange={(e) => setAsteroidDiameter(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex items-center mt-2">
                    <input
                      type="radio"
                      name="diameter-type"
                      className="mr-2"
                      defaultChecked
                    />
                    <span className="text-sm text-blue-200">Médio - Airburst ou impacto</span>
                  </div>
                </div>

                {/* Velocidade de Impacto */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Velocidade de Impacto: {impactVelocity} km/s
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="70"
                    value={impactVelocity}
                    onChange={(e) => setImpactVelocity(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex items-center mt-2">
                    <input
                      type="radio"
                      name="velocity-type"
                      className="mr-2"
                      defaultChecked
                    />
                    <span className="text-sm text-blue-200">Velocidade média</span>
                  </div>
                </div>

                {/* Ângulo de Impacto */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Ângulo de Impacto: {impactAngle}°
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="90"
                    value={impactAngle}
                    onChange={(e) => setImpactAngle(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex items-center mt-2">
                    <input
                      type="radio"
                      name="angle-type"
                      className="mr-2"
                      defaultChecked
                    />
                    <span className="text-sm text-blue-200">Rasante - Airburst ou impacto</span>
                  </div>
                </div>

                {/* Coordenadas */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-blue-200 mb-2">Latitude</label>
                    <input
                      type="text"
                      value={latitude}
                      onChange={(e) => setLatitude(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-blue-700 border border-blue-600 rounded-md text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-blue-200 mb-2">Longitude</label>
                    <input
                      type="text"
                      value={longitude}
                      onChange={(e) => setLongitude(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-blue-700 border border-blue-600 rounded-md text-white"
                    />
                  </div>
                </div>

                {/* Estratégia de Mitigação */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">Estratégia de Mitigação</label>
                  <select
                    value={mitigationStrategy}
                    onChange={(e) => setMitigationStrategy(e.target.value)}
                    className="w-full px-3 py-2 bg-blue-700 border border-blue-600 rounded-md text-white"
                  >
                    <option value="Nenhuma">Nenhuma</option>
                    <option value="Deflexão">Deflexão</option>
                    <option value="Fragmentação">Fragmentação</option>
                    <option value="Interceptação">Interceptação</option>
                  </select>
                </div>

                {/* Tempo de Deflexão */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Tempo de Deflexão: {deflectionTime} dias
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="365"
                    value={deflectionTime}
                    onChange={(e) => setDeflectionTime(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Tempo até Impacto */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    Tempo até Impacto: {timeToImpact} horas
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="8760"
                    value={timeToImpact}
                    onChange={(e) => setTimeToImpact(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* População em Risco */}
                <div>
                  <label className="block text-sm font-medium text-blue-200 mb-2">
                    População em Risco: {populationAtRisk}M
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="50"
                    step="0.1"
                    value={populationAtRisk}
                    onChange={(e) => setPopulationAtRisk(Number(e.target.value))}
                    className="w-full h-2 bg-blue-600 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Botão de Simulação */}
                <button
                  onClick={runSimulation}
                  disabled={loading}
                  className={`w-full py-4 px-6 rounded-lg font-bold text-lg transition-all ${
                    loading
                      ? 'bg-gray-600 cursor-not-allowed'
                      : 'bg-orange-600 hover:bg-orange-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                  }`}
                >
                  {loading ? 'EXECUTANDO SIMULAÇÃO...' : 'RODAR SIMULAÇÃO DE IMPACTO'}
                </button>
              </div>
            </div>
          </div>

          {/* PAINEL DIREITO - Resultados */}
          <div className="space-y-6">
            
            {/* Cards de Resultados */}
            <div className="grid grid-cols-2 gap-4">
              
              {/* Energia do Impacto */}
              <div className="bg-red-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.impact_energy_mt : '0'} Megatons TNT
              </div>
                <div className="text-sm text-red-200">ENERGIA DO IMPACTO</div>
              </div>
              
              {/* Magnitude Sísmica */}
              <div className="bg-pink-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.seismic_magnitude : '0'} Escala Richter
                </div>
                <div className="text-sm text-pink-200">MAGNITUDE SÍSMICA</div>
            </div>

              {/* Tamanho da Cratera ou Explosão Aérea */}
              <div className="bg-yellow-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults && safeSimulationResults.impact_type ? (
                    safeSimulationResults.impact_type === 'AIRBURST' 
                      ? 'EXPLOSÃO AÉREA' 
                      : `${safeSimulationResults.crater_diameter_km} Km de diâmetro`
                  ) : '0 Km de diâmetro'}
                    </div>
                <div className="text-sm text-yellow-200">
                  {safeSimulationResults && safeSimulationResults.impact_type === 'AIRBURST' 
                    ? 'SEM CRATERA - AIRBURST' 
                    : 'TAMANHO DA CRATERA'
                  }
                </div>
                {safeSimulationResults && safeSimulationResults.impact_type === 'AIRBURST' && (
                  <div className="text-xs text-yellow-300 mt-1">
                    Asteroide explode na atmosfera
                  </div>
                )}
              </div>
              
              {/* Status Deflexão */}
              <div className="bg-red-600 rounded-lg p-4">
                <div className="text-lg font-bold text-white">
                  {safeSimulationResults ? 'SIMULAÇÃO CONCLUÍDA' : 'AGUARDANDO SIMULAÇÃO'}
                    </div>
                <div className="text-sm text-red-200">STATUS DEFLEXÃO</div>
              </div>
              
              {/* Bola de Fogo */}
              <div className="bg-orange-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.fireball_radius_km : '0'} Km de raio
                    </div>
                <div className="text-sm text-orange-200">BOLA DE FOGO</div>
                <div className="text-xs text-orange-300 mt-1">Temperatura &gt;1000°C</div>
                <div className="text-xs text-orange-300">Ignição instantânea de materiais inflamáveis</div>
            </div>

              {/* Onda de Choque */}
              <div className="bg-purple-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.shockwave_intensity_db : '0'} Decibéis (dB)
                    </div>
                <div className="text-sm text-purple-200">ONDA DE CHOQUE</div>
                <div className="text-xs text-purple-300 mt-1">Nível ALTO</div>
                <div className="text-xs text-purple-300">Ruptura de tímpanos e danos estruturais severos</div>
              </div>
              
              {/* Ventos de Pico */}
              <div className="bg-cyan-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.peak_winds_kmh : '0'} Km/h
                    </div>
                <div className="text-sm text-cyan-200">VENTOS DE PICO</div>
                <div className="text-xs text-cyan-300 mt-1">Categoria F3</div>
                <div className="text-xs text-cyan-300">Destruição total de estruturas não reforçadas</div>
              </div>
              
              {/* Tipo de Impacto */}
              <div className="bg-blue-600 rounded-lg p-4">
                <div className="text-lg font-bold text-white">
                  {safeSimulationResults && safeSimulationResults.impact_type ? safeSimulationResults.impact_type : 'IMPACTO DIRETO'}
                    </div>
                <div className="text-sm text-blue-200">TIPO DE IMPACTO</div>
                <div className="text-xs text-blue-300 mt-1">Impacto na superfície</div>
              </div>
              
              {/* Vítimas Fireball */}
              <div className="bg-orange-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.fireball_victims : '0'}K Pessoas
                    </div>
                <div className="text-sm text-orange-200">VÍTIMAS FIREBALL</div>
                <div className="text-xs text-orange-300 mt-1">Raio {safeSimulationResults ? safeSimulationResults.fireball_radius_km : '0'} km</div>
                <div className="text-xs text-orange-300">Morte instantânea por calor extremo</div>
            </div>

              {/* Queimaduras 2º Grau */}
              <div className="bg-yellow-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.burn_victims : '0'}K Pessoas
                    </div>
                <div className="text-sm text-yellow-200">QUEIMADURAS 2º GRAU</div>
                <div className="text-xs text-yellow-300 mt-1">Raio {safeSimulationResults ? safeSimulationResults.fireball_radius_km * 2 : '0'} km</div>
                <div className="text-xs text-yellow-300">Roupas pegam fogo</div>
              </div>
              
              {/* Vítimas Onda Choque */}
              <div className="bg-cyan-600 rounded-lg p-4">
                <div className="text-xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.shockwave_victims : '0'} Pessoas
                    </div>
                <div className="text-sm text-cyan-200">VÍTIMAS ONDA CHOQUE</div>
                <div className="text-xs text-cyan-300 mt-1">Intensidade {safeSimulationResults ? safeSimulationResults.shockwave_intensity_db : '0'} dB</div>
                <div className="text-xs text-cyan-300">Colapso de estruturas</div>
              </div>
              
              {/* Árvores Incendiadas */}
              <div className="bg-green-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.burned_trees : '0'}
                    </div>
                <div className="text-sm text-green-200">ÁRVORES INCENDIADAS</div>
              </div>
              
              {/* Casas Colapsam */}
              <div className="bg-amber-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.collapsed_houses : '0'}
                    </div>
                <div className="text-sm text-amber-200">CASAS COLAPSAM</div>
            </div>

              {/* Árvores Derrubadas */}
              <div className="bg-gray-600 rounded-lg p-4">
                <div className="text-2xl font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.fallen_trees : '0'}
                </div>
                <div className="text-sm text-gray-200">ÁRVORES DERRUBADAS</div>
              </div>
              
              {/* Frequência */}
              <div className="bg-blue-600 rounded-lg p-4">
                <div className="text-lg font-bold text-white">
                  {safeSimulationResults ? safeSimulationResults.frequency : 'N/A'}
                  </div>
                <div className="text-sm text-blue-200">FREQUÊNCIA</div>
                <div className="text-xs text-blue-300 mt-1">Eventos similares</div>
                </div>
              </div>
              
            {/* Zona de Impacto Global - Mapa Interativo */}
            <div className="bg-blue-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Zona de Impacto Global</h3>
              
              <div className="bg-blue-900 rounded-lg overflow-hidden" style={{ height: '400px' }}>
                {safeSimulationResults ? (
                  <MapContainer
                    center={[latitude, longitude]}
                    zoom={10}
                    style={{ height: '100%', width: '100%' }}
                    className="z-0"
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    
                    {/* Marcador do Impacto */}
                    <Marker position={[latitude, longitude]}>
                      <Popup>
                    <div className="text-center">
                          <h3 className="font-bold text-red-600">PONTO DE IMPACTO</h3>
                          <p className="text-sm">Energia: {safeSimulationResults.impact_energy_mt} MT</p>
                          <p className="text-sm">
                            {safeSimulationResults && safeSimulationResults.impact_type ? (
                              safeSimulationResults.impact_type === 'AIRBURST' 
                                ? 'Airburst - Sem cratera' 
                                : `Cratera: ${safeSimulationResults.crater_diameter_km} km`
                            ) : 'Cratera: 0 km'}
                          </p>
                    </div>
                      </Popup>
                    </Marker>
                    
                    {/* Zona de Bola de Fogo */}
                    <Circle
                      center={[latitude, longitude]}
                      radius={safeSimulationResults.fireball_radius_km * 1000}
                      pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                    />
                    
                    {/* Zona de Destruição - apenas para impactos diretos */}
                    {safeSimulationResults && safeSimulationResults.impact_type && safeSimulationResults.impact_type !== 'AIRBURST' && (
                      <Circle
                        center={[latitude, longitude]}
                        radius={safeSimulationResults.crater_diameter_km * 1000}
                        pathOptions={{ color: 'orange', fillColor: 'orange', fillOpacity: 0.2 }}
                      />
                    )}
                    
                    {/* Zona de Tsunami - apenas para impactos diretos */}
                    {safeSimulationResults && safeSimulationResults.impact_type && safeSimulationResults.impact_type !== 'AIRBURST' && (
                      <Circle
                        center={[latitude, longitude]}
                        radius={safeSimulationResults.crater_diameter_km * 2000}
                        pathOptions={{ color: 'blue', fillColor: 'blue', fillOpacity: 0.1 }}
                      />
                    )}
                  </MapContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                </div>
                      <p className="text-blue-200 mb-4">
                        Execute a simulação para visualizar o mapa de impacto
                      </p>
                      
                      <div className="space-y-2 text-sm text-blue-300">
                        <div>• Bola de Fogo - Ignição instantânea (&gt;1000°C)</div>
                        {safeSimulationResults && safeSimulationResults.impact_type ? (
                          safeSimulationResults.impact_type === 'AIRBURST' ? (
                            <div>• Airburst - Explosão atmosférica sem cratera</div>
                          ) : (
                            <>
                              <div>• Zona de Destruição - Raio da cratera + devastação total</div>
                              <div>• Zona de Tsunami - Área costeira de risco</div>
                            </>
                          )
                        ) : (
                          <div>• Zona de Destruição - Raio da cratera + devastação total</div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
            </div>

              {/* Legenda do Mapa */}
              {safeSimulationResults && (
                <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center">
                    <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                    <span className="text-blue-200">Bola de Fogo ({safeSimulationResults.fireball_radius_km} km)</span>
                      </div>
                  {safeSimulationResults && safeSimulationResults.impact_type && safeSimulationResults.impact_type !== 'AIRBURST' && (
                    <>
                      <div className="flex items-center">
                        <div className="w-4 h-4 bg-orange-500 rounded-full mr-2"></div>
                        <span className="text-blue-200">Destruição ({safeSimulationResults.crater_diameter_km} km)</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 bg-blue-500 rounded-full mr-2"></div>
                        <span className="text-blue-200">Tsunami ({safeSimulationResults.crater_diameter_km * 2} km)</span>
                      </div>
                    </>
                  )}
                  {safeSimulationResults && safeSimulationResults.impact_type && safeSimulationResults.impact_type === 'AIRBURST' && (
                    <div className="flex items-center">
                      <div className="w-4 h-4 bg-yellow-500 rounded-full mr-2"></div>
                      <span className="text-blue-200">Airburst - Sem cratera</span>
                    </div>
                  )}
                    </div>
              )}
              </div>

            {/* Módulo de Evacuação */}
            <div className="bg-blue-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Módulo de Evacuação - Fortaleza</h3>
              
              <div className="space-y-3">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span className="text-blue-200">Zona Destruição</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span className="text-blue-200">Zona Tsunami</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span className="text-blue-200">Rotas Evacuação</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AsteroidDashboard;