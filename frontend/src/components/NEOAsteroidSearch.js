import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Database, 
  AlertTriangle, 
  CheckCircle,
  Loader2,
  Info,
  Zap,
  Globe,
  Calendar,
  Target
} from 'lucide-react';
import { cosmosAPI } from '../services/apiService';

const NEOAsteroidSearch = ({ onAsteroidSelected, onSimulationData }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedAsteroid, setSelectedAsteroid] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingAsteroid, setIsLoadingAsteroid] = useState(false);
  const [error, setError] = useState(null);
  const [impactAnalysis, setImpactAnalysis] = useState(null);

  // Asteroides famosos conhecidos para facilitar a busca
  const famousAsteroids = [
    { id: '2000433', name: 'Eros (433 Eros)', description: 'Primeiro asteroide próximo à Terra descoberto' },
    { id: '99942', name: 'Apophis (99942 Apophis)', description: 'Asteroide potencialmente perigoso' },
    { id: '25143', name: 'Itokawa (25143 Itokawa)', description: 'Asteroide visitado pela sonda Hayabusa' },
    { id: '162173', name: 'Ryugu (162173 Ryugu)', description: 'Asteroide visitado pela sonda Hayabusa2' },
    { id: '101955', name: 'Bennu (101955 Bennu)', description: 'Asteroide visitado pela sonda OSIRIS-REx' },
    { id: '65803', name: 'Didymos (65803 Didymos)', description: 'Asteroide alvo da missão DART' }
  ];

  // Buscar dados de um asteroide específico
  const searchAsteroid = async (asteroidId) => {
    if (!asteroidId.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      console.log(`🔍 Buscando asteroide ${asteroidId}...`);
      
      // Buscar dados completos do asteroide
      const result = await cosmosAPI.getEnhancedAsteroidData(asteroidId);
      
      if (result.success && result.data) {
        console.log('✅ Asteroide encontrado:', result.data);
        setSelectedAsteroid(result.data);
        
        // Notificar componente pai sobre o asteroide selecionado
        if (onAsteroidSelected) {
          onAsteroidSelected(result.data);
        }
        
        // Extrair parâmetros para simulação
        extractSimulationParameters(result.data);
      } else {
        setError(`Asteroide ${asteroidId} não encontrado na base de dados da NASA.`);
        console.error('❌ Asteroide não encontrado:', result.error);
      }
    } catch (error) {
      setError(`Erro ao buscar asteroide: ${error.message}`);
      console.error('❌ Erro na busca:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Extrair parâmetros de simulação dos dados do asteroide
  const extractSimulationParameters = (asteroidData) => {
    try {
      const basicInfo = asteroidData.basic_info || {};
      const physicalData = asteroidData.physical_data || {};
      
      // Estimar diâmetro
      let diameter_m = null;
      if (physicalData.diameter_km) {
        diameter_m = physicalData.diameter_km * 1000;
      } else if (basicInfo.estimated_diameter?.meters) {
        const diameterData = basicInfo.estimated_diameter.meters;
        diameter_m = (diameterData.estimated_diameter_min + diameterData.estimated_diameter_max) / 2;
      }

      // Velocidade típica de impacto (17 km/s é uma média)
      const velocity_kms = 17.0;

      // Parâmetros de simulação
      const simulationParams = {
        diameter_m: diameter_m || 100, // Fallback para 100m
        velocity_kms: velocity_kms,
        impact_angle_deg: 45, // Ângulo padrão
        target_type: 'rocha',
        latitude: -3.7327, // Fortaleza como padrão
        longitude: -38.5270,
        asteroid_info: {
          id: basicInfo.neo_reference_id || 'Unknown',
          name: basicInfo.name || 'Unknown',
          is_potentially_hazardous: basicInfo.is_potentially_hazardous_asteroid || false,
          classification: asteroidData.classification || {}
        }
      };

      console.log('📊 Parâmetros extraídos:', simulationParams);
      
      // Notificar componente pai sobre os parâmetros
      if (onSimulationData) {
        onSimulationData(simulationParams);
      }

    } catch (error) {
      console.error('❌ Erro ao extrair parâmetros:', error);
    }
  };

  // Executar análise de impacto com dados reais
  const runImpactAnalysis = async () => {
    if (!selectedAsteroid) return;

    setIsLoadingAsteroid(true);
    setError(null);

    try {
      const asteroidId = selectedAsteroid.basic_info?.neo_reference_id;
      if (!asteroidId) {
        throw new Error('ID do asteroide não encontrado');
      }

      console.log(`🚀 Executando análise de impacto para ${asteroidId}...`);
      
      // Executar análise de impacto via backend
      const result = await cosmosAPI.request(`/neo/${asteroidId}/impact-analysis`, {
        method: 'GET',
        params: {
          impact_latitude: -3.7327, // Fortaleza
          impact_longitude: -38.5270,
          impact_angle_deg: 45,
          target_type: 'rocha'
        }
      });

      if (result.success) {
        console.log('✅ Análise de impacto concluída:', result.data);
        setImpactAnalysis(result.data);
        
        // Notificar componente pai sobre a análise
        if (onSimulationData) {
          onSimulationData(result.data);
        }
      } else {
        throw new Error(result.error || 'Erro na análise de impacto');
      }
    } catch (error) {
      setError(`Erro na análise de impacto: ${error.message}`);
      console.error('❌ Erro na análise:', error);
    } finally {
      setIsLoadingAsteroid(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-white/20 rounded-lg">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Busca de Asteroides Reais</h3>
            <p className="text-blue-100 text-sm">Dados catalogados pela NASA - Near Earth Objects (NEOs)</p>
          </div>
        </div>

        {/* Campo de busca */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Digite o ID do asteroide (ex: 2000433, 99942)"
              className="flex-1 p-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && searchAsteroid(searchTerm)}
            />
            <button
              onClick={() => searchAsteroid(searchTerm)}
              disabled={isSearching || !searchTerm.trim()}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-200 ${
                isSearching || !searchTerm.trim()
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  : 'bg-white text-blue-600 hover:bg-blue-50 hover:shadow-lg transform hover:scale-105'
              }`}
            >
              {isSearching ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Buscando...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Search className="w-4 h-4" />
                  <span>Buscar</span>
                </div>
              )}
            </button>
          </div>

          {/* Asteroides famosos */}
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-white mb-2">Asteroides Famosos:</h4>
            <div className="grid grid-cols-2 gap-2">
              {famousAsteroids.map((asteroid) => (
                <button
                  key={asteroid.id}
                  onClick={() => {
                    setSearchTerm(asteroid.id);
                    searchAsteroid(asteroid.id);
                  }}
                  className="text-left p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-sm"
                >
                  <div className="font-semibold text-white">{asteroid.name}</div>
                  <div className="text-blue-100 text-xs">{asteroid.description}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Erro */}
      {error && (
        <div className="bg-red-900/40 border border-red-500/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h4 className="text-lg font-semibold text-red-300">Erro</h4>
          </div>
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {/* Asteroide Selecionado */}
      {selectedAsteroid && (
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-green-300 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Asteroide Encontrado
            </h4>
            <button
              onClick={runImpactAnalysis}
              disabled={isLoadingAsteroid}
              className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
                isLoadingAsteroid
                  ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg transform hover:scale-105'
              }`}
            >
              {isLoadingAsteroid ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analisando...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span>Simular Impacto</span>
                </div>
              )}
            </button>
          </div>

          <div className="space-y-4">
            {/* Informações Básicas */}
            <div className="bg-gray-700 rounded-lg p-4">
              <h5 className="font-semibold mb-3 text-lg text-white">
                {selectedAsteroid.basic_info?.name || 'Nome não disponível'}
              </h5>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">ID NASA:</span>
                  <span className="text-white ml-2">{selectedAsteroid.basic_info?.neo_reference_id || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-400">Potencialmente Perigoso:</span>
                  <span className={`ml-2 font-semibold ${
                    selectedAsteroid.basic_info?.is_potentially_hazardous_asteroid 
                      ? 'text-red-400' 
                      : 'text-green-400'
                  }`}>
                    {selectedAsteroid.basic_info?.is_potentially_hazardous_asteroid ? 'SIM' : 'NÃO'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Classificação:</span>
                  <span className="text-white ml-2">{selectedAsteroid.classification?.spktype || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-gray-400">Última Observação:</span>
                  <span className="text-white ml-2">{selectedAsteroid.basic_info?.orbital_data?.last_observation_date || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Dados Físicos */}
            {selectedAsteroid.physical_data && (
              <div className="bg-gray-700 rounded-lg p-4">
                <h5 className="font-semibold mb-3 text-lg text-blue-300">Dados Físicos</h5>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Diâmetro:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.physical_data.diameter_km 
                        ? `${selectedAsteroid.physical_data.diameter_km.toFixed(2)} km`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Massa:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.physical_data.mass_kg 
                        ? `${(selectedAsteroid.physical_data.mass_kg / 1000).toFixed(2)} toneladas`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Período de Rotação:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.physical_data.rotation_period_hours 
                        ? `${selectedAsteroid.physical_data.rotation_period_hours.toFixed(2)} horas`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Albedo:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.physical_data.albedo 
                        ? selectedAsteroid.physical_data.albedo.toFixed(3)
                        : 'N/A'
                      }
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Dados Orbitais */}
            {selectedAsteroid.orbital_data && (
              <div className="bg-gray-700 rounded-lg p-4">
                <h5 className="font-semibold mb-3 text-lg text-purple-300">Dados Orbitais</h5>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Período Orbital:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.orbital_data.orbital_period_days 
                        ? `${selectedAsteroid.orbital_data.orbital_period_days.toFixed(2)} dias`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Excentricidade:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.orbital_data.eccentricity 
                        ? selectedAsteroid.orbital_data.eccentricity.toFixed(4)
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Inclinação:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.orbital_data.inclination_deg 
                        ? `${selectedAsteroid.orbital_data.inclination_deg.toFixed(2)}°`
                        : 'N/A'
                      }
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Distância Mínima:</span>
                    <span className="text-white ml-2">
                      {selectedAsteroid.orbital_data.minimum_orbit_intersection_distance_au 
                        ? `${selectedAsteroid.orbital_data.minimum_orbit_intersection_distance_au.toFixed(4)} AU`
                        : 'N/A'
                      }
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Análise de Impacto */}
      {impactAnalysis && (
        <div className="bg-gray-800 rounded-lg p-6">
          <h4 className="text-lg font-semibold mb-4 text-orange-300 flex items-center gap-2">
            <Target className="w-5 h-5" />
            Análise de Impacto Realizada
          </h4>
          
          <div className="bg-orange-900/40 border border-orange-500/50 rounded-lg p-4">
            <h5 className="font-semibold mb-3 text-lg text-orange-300">
              ✅ Simulação Baseada em Dados Reais da NASA
            </h5>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-200">
                  <strong>Asteroide:</strong> {impactAnalysis.asteroid_info?.name || 'N/A'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-200">
                  <strong>Diâmetro:</strong> {impactAnalysis.asteroid_info?.diameter_m?.toFixed(0)} metros
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-200">
                  <strong>Energia do Impacto:</strong> {impactAnalysis.impact_simulation?.energia?.equivalente_tnt_megatons?.toFixed(2)} Megatons TNT
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-200">
                  <strong>Magnitude Sísmica:</strong> {impactAnalysis.impact_simulation?.terremoto?.magnitude_richter?.toFixed(1)}
                </span>
              </div>
            </div>
            
            <div className="mt-4 p-3 bg-blue-900/30 rounded-lg">
              <p className="text-sm text-blue-200">
                💡 <strong>Dica:</strong> Esta simulação usa dados reais catalogados pela NASA. 
                Os parâmetros físicos e orbitais são baseados em observações astronômicas reais.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Informações sobre NEOs */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h4 className="text-lg font-semibold mb-4 text-blue-300 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Sobre Near Earth Objects (NEOs)
        </h4>
        
        <div className="space-y-3 text-sm text-gray-300">
          <p>
            <strong>NEOs</strong> são asteroides e cometas que têm órbitas que os levam para dentro de 1.3 unidades astronômicas (AU) do Sol.
          </p>
          <p>
            <strong>PHA (Potentially Hazardous Asteroids)</strong> são NEOs com diâmetro maior que 140 metros e que podem se aproximar da Terra a menos de 0.05 AU.
          </p>
          <p>
            <strong>Fonte dos Dados:</strong> NASA Near Earth Object Web Service (NeoWs) e JPL Small-Body Database (SBDB).
          </p>
        </div>
      </div>
    </div>
  );
};

export default NEOAsteroidSearch;
