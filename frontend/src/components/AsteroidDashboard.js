import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { cosmosAPI } from '../services/apiService';
import AIRouteOptimizer from './AIRouteOptimizer';
import NEOAsteroidSearch from './NEOAsteroidSearch';
import ScientificReport from './ScientificReport';

// Ícones do Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Componente para controlar o mapa
function MapController({ isFullscreen, simulationData }) {
  const map = useMap();
  
  useEffect(() => {
    if (isFullscreen) {
      map.invalidateSize();
    }
  }, [isFullscreen, map]);

  // Remover zoom automático que estava causando problemas
  return null;
}

// Componente para capturar cliques no mapa
function MapClickHandler({ onMapClick }) {
  const map = useMap();
  
  useEffect(() => {
    const handleClick = (e) => {
      onMapClick(e);
    };
    
    map.on('click', handleClick);
    
    return () => {
      map.off('click', handleClick);
    };
  }, [map, onMapClick]);
  
  return null;
}

// Componente do relógio
function Clock() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="text-sm font-mono text-white">
      {time.toLocaleTimeString('pt-BR', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })}
    </div>
  );
}

// Componente principal
function AsteroidDashboard() {
  // Estados principais
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [apiStatus, setApiStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [darkMode, setDarkMode] = useState(false);
  
  // Estados de simulação
  const [simulationData, setSimulationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [aiOptimizedRoutes, setAiOptimizedRoutes] = useState([]);
  const [safeZones, setSafeZones] = useState([]);
  const [optimalRoutes, setOptimalRoutes] = useState([]);
  
  // Estados de filtros
  const [severityFilter, setSeverityFilter] = useState('all');
  const [zoneFilter, setZoneFilter] = useState('all');
  const [timeFilter, setTimeFilter] = useState('24h');
  
  // Estados do formulário de simulação
  const [simulationForm, setSimulationForm] = useState({
    diameter_m: 100,
    velocity_kms: 35,
    impact_angle_deg: 24,
    target_type: 'rocha',
    latitude: -3.7327,
    longitude: -38.5270
  });
  
  // Estados de alertas
  const [alerts, setAlerts] = useState([]);
  const [alertCounter, setAlertCounter] = useState(0);
  
  // Estados de evacuação
  const [dangerZones, setDangerZones] = useState([]);
  const [evacuationRoutes, setEvacuationRoutes] = useState([]);
  const [shelters, setShelters] = useState([]);
  
  // Estado para controlar visibilidade das zonas de impacto
  const [showImpactZones, setShowImpactZones] = useState(true);
  
  // Estados para busca de asteroides reais
  const [selectedAsteroid, setSelectedAsteroid] = useState(null);
  const [useRealAsteroidData, setUseRealAsteroidData] = useState(false);
  
  // Estado para controlar o modo de simulação
  const [simulationMode, setSimulationMode] = useState('custom'); // 'custom' ou 'neo'
  
  // Estado para controlar a visualização do relatório científico
  const [showScientificReport, setShowScientificReport] = useState(false);
  
  // Estado para feedback visual de clique no mapa
  const [mapClickFeedback, setMapClickFeedback] = useState(null);
  
  // Estado para controlar se o mapa está travado após simulação
  const [isMapLocked, setIsMapLocked] = useState(false);

  // Coordenadas padrão
  const [center, setCenter] = useState([-3.7327, -38.5270]);

  // Atualizar centro quando coordenadas mudarem
  useEffect(() => {
    setCenter([simulationForm.latitude, simulationForm.longitude]);
  }, [simulationForm.latitude, simulationForm.longitude]);

  // Função para lidar com clique no mapa
  const handleMapClick = useCallback((e) => {
    // Verificar se o mapa está travado
    if (isMapLocked) {
      console.log('🔒 Mapa travado - clique ignorado');
      return;
    }
    
    const { lat, lng } = e.latlng;
    
    // Atualizar formulário com novas coordenadas
    setSimulationForm(prev => ({
      ...prev,
      latitude: lat,
      longitude: lng
    }));
    
    // Atualizar centro do mapa
    setCenter([lat, lng]);
    
    // Feedback visual temporário
    setMapClickFeedback({
      position: [lat, lng],
      timestamp: Date.now()
    });
    
    // Limpar feedback após 2 segundos
    setTimeout(() => {
      setMapClickFeedback(null);
    }, 2000);
    
    console.log('📍 Nova posição de impacto:', { lat, lng });
  }, [isMapLocked]);

  // Função para lidar com asteroide selecionado
  const handleAsteroidSelected = useCallback((asteroidData) => {
    console.log('🪨 Asteroide selecionado:', asteroidData);
    setSelectedAsteroid(asteroidData);
    setUseRealAsteroidData(true);
  }, []);

  // Função para lidar com dados de simulação de asteroide real
  const handleAsteroidSimulationData = useCallback((simulationData) => {
    console.log('📊 Dados de simulação do asteroide:', simulationData);
    
    // Atualizar formulário com dados reais se disponíveis
    if (simulationData.diameter_m) {
      setSimulationForm(prev => ({
        ...prev,
        diameter_m: simulationData.diameter_m,
        velocity_kms: simulationData.velocity_kms || prev.velocity_kms,
        impact_angle_deg: simulationData.impact_angle_deg || prev.impact_angle_deg,
        target_type: simulationData.target_type || prev.target_type,
        latitude: simulationData.latitude || prev.latitude,
        longitude: simulationData.longitude || prev.longitude
      }));
    }

    // Se temos dados de simulação completos, usar diretamente
    if (simulationData.impact_simulation) {
      const data = simulationData.impact_simulation;
      const mappedData = {
        impact_energy_mt: data.energia?.equivalente_tnt_megatons || 0,
        seismic_magnitude: data.terremoto?.magnitude_richter || 0,
        crater_diameter_km: data.cratera?.diametro_final_km || 0,
        fireball_radius_km: data.fireball?.raio_queimadura_3_grau_km || 0,
        shockwave_intensity_db: data.onda_de_choque_e_vento?.nivel_som_1km_db || 0,
        peak_winds_kmh: (data.onda_de_choque_e_vento?.pico_vento_ms || 0) * 3.6,
        impact_type: data.cratera?.is_airburst ? 'AIRBURST' : 'IMPACTO DIRETO',
        timestamp: new Date(),
        asteroid_info: simulationData.asteroid_info
      };

      console.log('🎯 Dados mapeados do asteroide real:', mappedData);
      setSimulationData(mappedData);
      generateZonesAndRoutes(mappedData);
      generateAlerts(mappedData);
    }
  }, []);

  // Verificar status da API
  const checkApiStatus = useCallback(async () => {
    try {
      const connected = await cosmosAPI.testConnection();
      setApiStatus(connected ? 'online' : 'offline');
        } catch (error) {
      setApiStatus('offline');
    }
  }, []);

  // Gerar zonas e rotas
  const generateZonesAndRoutes = useCallback((data) => {
    if (!data.fireball_radius_km) return;

    const radius = data.fireball_radius_km;
    
    // Zonas de perigo por nível
    const dangerLevels = [
      { level: 'critical', radius: radius * 0.3, color: 'red', opacity: 0.8 },
      { level: 'high', radius: radius * 0.6, color: 'orange', opacity: 0.6 },
      { level: 'medium', radius: radius * 0.9, color: 'yellow', opacity: 0.4 }
    ];

    setDangerZones(dangerLevels);

    // Zonas seguras
    const safeRadius = radius * 2;
    const safeZonesData = [
      {
        id: 1,
        name: "Abrigo Norte",
        position: [center[0] + (safeRadius / 111), center[1]],
        capacity: 5000,
        distance: safeRadius,
        type: 'shelter'
      },
      {
        id: 2,
        name: "Abrigo Sul",
        position: [center[0] - (safeRadius / 111), center[1]],
        capacity: 3000,
        distance: safeRadius,
        type: 'shelter'
      },
      {
        id: 3,
        name: "Zona Segura Leste",
        position: [center[0], center[1] + (safeRadius / 111)],
        capacity: 8001,
        distance: safeRadius,
        type: 'safe_zone'
      },
      {
        id: 4,
        name: "Zona Segura Oeste",
        position: [center[0], center[1] - (safeRadius / 111)],
        capacity: 6000,
        distance: safeRadius,
        type: 'safe_zone'
      }
    ];

    setSafeZones(safeZonesData);
    setShelters(safeZonesData.filter(zone => zone.type === 'shelter'));

    // Rotas de evacuação
    const routes = safeZonesData.map(zone => ({
      id: zone.id,
      name: zone.name,
      from: center,
      to: zone.position,
      distance: zone.distance,
      estimatedTime: Math.round(zone.distance / 30),
      capacity: zone.capacity,
      status: 'active'
    }));

    setEvacuationRoutes(routes);
  }, [center]);

  // Gerar alertas
  const generateAlerts = useCallback((data) => {
    const timestamp = Date.now();
    const baseId = `${timestamp}_${alertCounter}`;
    
    const newAlerts = [
      {
        id: `${baseId}_impact`,
        type: 'impact',
        severity: 'critical',
        message: `Impacto detectado: ${data.impact_energy_mt.toFixed(2)} MT`,
        timestamp: new Date(),
        location: 'Centro da cidade'
      },
      {
        id: `${baseId}_evacuation`,
        type: 'evacuation',
        severity: 'high',
        message: `Evacuação iniciada para zona de ${data.fireball_radius_km.toFixed(2)} km`,
        timestamp: new Date(),
        location: 'Todas as zonas afetadas'
      },
      {
        id: `${baseId}_seismic`,
        type: 'seismic',
        severity: 'medium',
        message: `Terremoto magnitude ${data.seismic_magnitude.toFixed(1)} detectado`,
        timestamp: new Date(),
        location: 'Região metropolitana'
      }
    ];

    setAlertCounter(prev => prev + 1);
    setAlerts(prev => [...newAlerts, ...prev].slice(0, 10));
  }, [alertCounter]);

  // Executar simulação
  const runSimulation = useCallback(async () => {
    // Prevenir múltiplas execuções simultâneas
    if (isSimulating || loading) {
      console.log('Simulação já em andamento, ignorando...');
      return;
    }

    setIsSimulating(true);
    setLoading(true);
    
    try {
      console.log('Iniciando simulação com dados:', simulationForm);
      
      const result = await cosmosAPI.simulateImpact({
        diameter_m: simulationForm.diameter_m,
        velocity_kms: simulationForm.velocity_kms,
        impact_angle_deg: simulationForm.impact_angle_deg,
        target_type: simulationForm.target_type,
        latitude: simulationForm.latitude,
        longitude: simulationForm.longitude
      });

      console.log('Resultado da simulação:', result);
      
      if (result.success && result.data) {
        const data = result.data;
        const mappedData = {
          impact_energy_mt: data.energia?.equivalente_tnt_megatons || 0,
          seismic_magnitude: data.terremoto?.magnitude_richter || 0,
          crater_diameter_km: data.cratera?.diametro_final_km || 0,
          fireball_radius_km: data.fireball?.raio_queimadura_3_grau_km || 0,
          shockwave_intensity_db: data.onda_de_choque_e_vento?.nivel_som_1km_db || 0,
          peak_winds_kmh: (data.onda_de_choque_e_vento?.pico_vento_ms || 0) * 3.6,
          impact_type: data.cratera?.is_airburst ? 'AIRBURST' : 'IMPACTO DIRETO',
          timestamp: new Date()
        };

        console.log('Dados mapeados:', mappedData);
        setSimulationData(mappedData);
        generateZonesAndRoutes(mappedData);
        generateAlerts(mappedData);
        
        // Travar o mapa após simulação bem-sucedida
        setIsMapLocked(true);
        console.log('🔒 Mapa travado após simulação');
      } else {
        console.error('Erro na resposta da API:', result.error);
        // Criar dados de fallback para demonstração
        const fallbackData = {
          impact_energy_mt: simulationForm.diameter_m * 0.1,
          seismic_magnitude: Math.log10(simulationForm.diameter_m) + 2,
          crater_diameter_km: simulationForm.diameter_m / 1000,
          fireball_radius_km: simulationForm.diameter_m / 500,
          shockwave_intensity_db: 120 + (simulationForm.velocity_kms * 2),
          peak_winds_kmh: simulationForm.velocity_kms * 10,
          impact_type: simulationForm.diameter_m <= 150 ? 'AIRBURST' : 'IMPACTO DIRETO',
          timestamp: new Date()
        };
        
        console.log('Usando dados de fallback:', fallbackData);
        setSimulationData(fallbackData);
        generateZonesAndRoutes(fallbackData);
        generateAlerts(fallbackData);
        
        // Travar o mapa após simulação com fallback
        setIsMapLocked(true);
        console.log('🔒 Mapa travado após simulação (fallback)');
      }
      } catch (error) {
      console.error('Erro na simulação:', error);
      
      // Criar dados de fallback em caso de erro
      const fallbackData = {
        impact_energy_mt: simulationForm.diameter_m * 0.1,
        seismic_magnitude: Math.log10(simulationForm.diameter_m) + 2,
        crater_diameter_km: simulationForm.diameter_m / 1000,
        fireball_radius_km: simulationForm.diameter_m / 500,
        shockwave_intensity_db: 120 + (simulationForm.velocity_kms * 2),
        peak_winds_kmh: simulationForm.velocity_kms * 10,
        impact_type: simulationForm.diameter_m <= 150 ? 'AIRBURST' : 'IMPACTO DIRETO',
        timestamp: new Date()
      };
      
      console.log('Usando dados de fallback após erro:', fallbackData);
      setSimulationData(fallbackData);
      generateZonesAndRoutes(fallbackData);
      generateAlerts(fallbackData);
      
      // Travar o mapa após simulação com erro
      setIsMapLocked(true);
      console.log('🔒 Mapa travado após simulação (erro)');
    } finally {
      setLoading(false);
      setIsSimulating(false);
    }
  }, [simulationForm, generateZonesAndRoutes, generateAlerts, isSimulating, loading]);

  // Função para nova simulação (libera o mapa)
  const handleNewSimulation = useCallback(() => {
    // Liberar o mapa
    setIsMapLocked(false);
    
    // Limpar dados da simulação anterior
    setSimulationData(null);
    setDangerZones([]);
    setEvacuationRoutes([]);
    setShelters([]);
    setSafeZones([]);
    setOptimalRoutes([]);
    setAiOptimizedRoutes([]);
    setAlerts([]);
    
    // Limpar feedback de clique
    setMapClickFeedback(null);
    
    console.log('🔄 Nova simulação iniciada - mapa liberado');
  }, []);

  // Função para atualizar rotas otimizadas por IA
  const handleAIRoutesUpdate = useCallback((data) => {
    console.log('🧠 Dados recebidos do AIRouteOptimizer:', data);
    
    // Verificar se são rotas ou safe zones
    if (Array.isArray(data)) {
      // Se todos os itens têm propriedades de rota otimizada
      if (data.length > 0 && (data[0].route_coordinates || data[0].total_distance_km)) {
        setOptimalRoutes(data);
      }
      // Se todos os itens têm propriedades de rota simples
      else if (data.length > 0 && (data[0].from || data[0].distance)) {
        setAiOptimizedRoutes(data);
      } 
      // Se todos os itens têm propriedades de safe zone
      else if (data.length > 0 && (data[0].safety_score || data[0].distance_from_impact_km)) {
        setSafeZones(data);
      }
    }
  }, []);

  // Atualização automática apenas do status da API
  useEffect(() => {
    const interval = setInterval(() => {
      checkApiStatus();
      setLastUpdate(new Date());
      // Removido runSimulation() para evitar loop infinito
    }, 15000);

    return () => clearInterval(interval);
  }, [checkApiStatus]);

  // Inicialização
  useEffect(() => {
    checkApiStatus();
    // Removido runSimulation() automático - usuário deve clicar no botão
  }, [checkApiStatus]);

  // Filtrar alertas
  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter !== 'all' && alert.severity !== severityFilter) return false;
    if (timeFilter === '1h' && Date.now() - alert.timestamp.getTime() > 3600000) return false;
    if (timeFilter === '24h' && Date.now() - alert.timestamp.getTime() > 86400000) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 text-gray-900">
      {/* Header Fixo */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl">🌌</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-blue-600 bg-clip-text text-transparent">COSMOS SENTINEL</h1>
                  <p className="text-sm text-gray-600">Sistema de Evacuação Inteligente</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-4">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  apiStatus === 'online' 
                    ? 'bg-green-100 text-green-800 border border-green-200' 
                    : apiStatus === 'connecting'
                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                    : 'bg-red-100 text-red-800 border border-red-200'
                }`}>
                  {apiStatus === 'online' ? '🟢 Backend Online' : 
                   apiStatus === 'connecting' ? '🟡 Conectando' : '🔴 Backend Offline'}
              </div>
                <Clock className="w-5 h-5 text-gray-600" />
            </div>
          </div>
        </div>
      </header>

      {/* Layout Principal */}
      <div className="pt-20 flex h-screen">
        {/* Painel Lateral - Responsivo */}
        <aside className="w-80 border-r border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm hidden lg:block">
          <div className="p-6 h-full flex flex-col overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200">
            <h2 className="text-lg font-semibold mb-6 text-gray-800">Filtros e Controles</h2>
            
            {/* Seletor de Modo de Simulação */}
            <div className="mb-6">
              <h3 className="text-md font-semibold text-purple-600 mb-3">Modo de Simulação</h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSimulationMode('custom')}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 ${
                    simulationMode === 'custom'
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-lg">⚙️</span>
                    <span>Personalizada</span>
                  </div>
                </button>
                <button
                  onClick={() => setSimulationMode('neo')}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all duration-200 ${
                    simulationMode === 'neo'
                      ? 'bg-purple-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-lg">🪨</span>
                    <span>NEOs Reais</span>
                  </div>
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {simulationMode === 'custom' 
                  ? 'Configure parâmetros manualmente para simulação personalizada'
                  : 'Use dados reais de asteroides catalogados pela NASA'
                }
              </p>
            </div>
            
            {/* Formulário de Simulação - Personalizada */}
            {simulationMode === 'custom' && (
            <div className="space-y-4 flex-1">
              <h3 className="text-md font-semibold text-blue-600">Parâmetros do Meteoro</h3>
              
              {/* Presets Rápidos */}
              <div className="mb-4">
                <h4 className="text-sm font-medium mb-2 text-purple-400">Presets Rápidos</h4>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      setSimulationForm({
                        diameter_m: 50,
                        velocity_kms: 20,
                        impact_angle_deg: 45,
                        target_type: 'solo',
                        latitude: -3.7327,
                        longitude: -38.5270
                      });
                    }}
                    className="text-xs p-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-all duration-150 ease-in-out transform hover:scale-105 preset-button"
                  >
                    Pequeno
                  </button>
                  <button
                    onClick={() => {
                      setSimulationForm({
                        diameter_m: 200,
                        velocity_kms: 50,
                        impact_angle_deg: 30,
                        target_type: 'rocha',
                        latitude: -3.7327,
                        longitude: -38.5270
                      });
                    }}
                    className="text-xs p-2 bg-orange-600 hover:bg-orange-700 text-white rounded transition-all duration-150 ease-in-out transform hover:scale-105 preset-button"
                  >
                    Médio
                  </button>
                  <button
                    onClick={() => {
                      setSimulationForm({
                        diameter_m: 500,
                        velocity_kms: 70,
                        impact_angle_deg: 15,
                        target_type: 'oceano',
                        latitude: -3.7327,
                        longitude: -38.5270
                      });
                    }}
                    className="text-xs p-2 bg-red-600 hover:bg-red-700 text-white rounded transition-all duration-150 ease-in-out transform hover:scale-105 preset-button"
                  >
                    Grande
                  </button>
                  <button
                    onClick={() => {
                      setSimulationForm({
                        diameter_m: 1000,
                        velocity_kms: 90,
                        impact_angle_deg: 5,
                        target_type: 'rocha',
                        latitude: -3.7327,
                        longitude: -38.5270
                      });
                    }}
                    className="text-xs p-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-all duration-150 ease-in-out transform hover:scale-105 preset-button"
                  >
                    Catastrófico
                  </button>
                </div>
              </div>
              
                <div>
                <label className="block text-sm font-medium mb-2">
                  Diâmetro (metros)
                  </label>
                  <input
                  type="number"
                  min="1"
                  max="10000"
                  step="1"
                  value={simulationForm.diameter_m}
                  onChange={(e) => setSimulationForm(prev => ({
                    ...prev,
                    diameter_m: parseFloat(e.target.value) || 0
                  }))}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                  placeholder="Ex: 100"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Tamanho do meteoro em metros
                </p>
                </div>

                <div>
                <label className="block text-sm font-medium mb-2">
                  Velocidade (km/s)
                  </label>
                  <input
                  type="number"
                  min="1"
                  max="100"
                  step="0.1"
                  value={simulationForm.velocity_kms}
                  onChange={(e) => setSimulationForm(prev => ({
                    ...prev,
                    velocity_kms: parseFloat(e.target.value) || 0
                  }))}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                  placeholder="Ex: 35"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Velocidade de entrada na atmosfera
                </p>
                </div>

                <div>
                <label className="block text-sm font-medium mb-2">
                  Ângulo de Impacto (graus)
                  </label>
                  <input
                  type="number"
                  min="0"
                    max="90"
                  step="1"
                  value={simulationForm.impact_angle_deg}
                  onChange={(e) => setSimulationForm(prev => ({
                    ...prev,
                    impact_angle_deg: parseFloat(e.target.value) || 0
                  }))}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                  placeholder="Ex: 24"
                />
                <p className="text-xs text-gray-500 mt-1">
                  0° = perpendicular, 90° = rasante
                </p>
                </div>

                  <div>
                <label className="block text-sm font-medium mb-2">
                  Tipo de Terreno
                </label>
                  <select
                  value={simulationForm.target_type}
                  onChange={(e) => setSimulationForm(prev => ({
                    ...prev,
                    target_type: e.target.value
                  }))}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="solo">Solo</option>
                  <option value="rocha">Rocha</option>
                  <option value="oceano">Oceano</option>
                  </select>
                <p className="text-xs text-gray-500 mt-1">
                  Superfície de impacto
                </p>
                </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Latitude
                  </label>
                  <input
                    type="number"
                    min="-90"
                    max="90"
                    step="0.0001"
                    value={simulationForm.latitude}
                    onChange={(e) => setSimulationForm(prev => ({
                      ...prev,
                      latitude: parseFloat(e.target.value) || 0
                    }))}
                    className={`w-full p-2 rounded-lg border transition-colors text-sm ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                    placeholder="-3.7327"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Longitude
                  </label>
                  <input
                    type="number"
                    min="-180"
                    max="180"
                    step="0.0001"
                    value={simulationForm.longitude}
                    onChange={(e) => setSimulationForm(prev => ({
                      ...prev,
                      longitude: parseFloat(e.target.value) || 0
                    }))}
                    className={`w-full p-2 rounded-lg border transition-colors text-sm ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                    placeholder="-38.5270"
                  />
                </div>
              </div>
              <p className="text-xs text-gray-500">
                Coordenadas do ponto de impacto
              </p>
              
              {/* Instrução para clique no mapa */}
              <div className={`mt-2 p-3 rounded-lg border ${
                isMapLocked 
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className={isMapLocked ? 'text-red-600' : 'text-blue-600'}>
                    {isMapLocked ? '🔒' : '💡'}
                  </span>
                  <span className={`text-sm font-medium ${
                    isMapLocked ? 'text-red-800' : 'text-blue-800'
                  }`}>
                    {isMapLocked ? 'Mapa Travado:' : 'Dica:'}
                  </span>
                </div>
                <p className={`text-xs ${
                  isMapLocked ? 'text-red-700' : 'text-blue-700'
                }`}>
                  {isMapLocked 
                    ? 'Execute uma nova simulação para liberar o mapa e permitir mudanças de posição'
                    : 'Clique em qualquer lugar do mapa para atualizar automaticamente a posição de impacto'
                  }
                </p>
              </div>

              {/* Filtros */}
              <div className="space-y-4 mt-6">
                <h3 className="text-md font-semibold text-green-400">Filtros de Visualização</h3>
              
              <div>
                <label className="block text-sm font-medium mb-2">Severidade</label>
                <select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="all">Todas</option>
                  <option value="critical">Crítica</option>
                  <option value="high">Alta</option>
                  <option value="medium">Média</option>
                  <option value="low">Baixa</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Zona</label>
                <select
                  value={zoneFilter}
                  onChange={(e) => setZoneFilter(e.target.value)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="all">Todas</option>
                  <option value="safe">Zonas Seguras</option>
                  <option value="danger">Zonas de Perigo</option>
                  <option value="shelters">Abrigos</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Período</label>
                <select
                  value={timeFilter}
                  onChange={(e) => setTimeFilter(e.target.value)}
                  className={`w-full p-3 rounded-lg border transition-colors ${
                    darkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="1h">Última hora</option>
                  <option value="24h">Últimas 24h</option>
                  <option value="7d">Últimos 7 dias</option>
                </select>
              </div>
              
              {/* Checkbox para controlar visibilidade das zonas de impacto */}
              <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <input
                  type="checkbox"
                  id="showImpactZones"
                  checked={showImpactZones}
                  onChange={(e) => setShowImpactZones(e.target.checked)}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <label htmlFor="showImpactZones" className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                  Mostrar Zonas de Impacto
                </label>
              </div>
              <p className="text-xs text-gray-500">
                Controla a visibilidade dos círculos de impacto no mapa
              </p>
              </div>
            </div>
            )}

            {/* Busca de Asteroides Reais - Modo NEO */}
            {simulationMode === 'neo' && (
            <div className="space-y-4 flex-1">
              <NEOAsteroidSearch 
                onAsteroidSelected={handleAsteroidSelected}
                onSimulationData={handleAsteroidSimulationData}
              />
            </div>
            )}


            {/* Botão de Simulação - Modo Personalizado */}
            {simulationMode === 'custom' && (
            <div className="mt-6">
              <button
                onClick={runSimulation}
                disabled={loading}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ease-in-out simulation-button ${
                  loading 
                    ? 'bg-gray-500 cursor-not-allowed opacity-75' 
                    : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg transform hover:scale-105'
                } text-white flex items-center justify-center space-x-2`}
              >
                {loading ? (
                  <>
                    <div className="spinner h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Simulando...</span>
                  </>
                ) : (
                  <>
                    <span>🚀</span>
                    <span>Executar Simulação</span>
                  </>
                )}
              </button>
              
              {loading && (
                <div className="mt-2 text-center">
                  <p className="text-xs text-gray-500 animate-pulse">
                    Aguarde... Processando dados do impacto
                  </p>
                    </div>
              )}
            </div>
            )}

            {/* Status da Simulação */}
            {simulationData && (
              <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <h3 className="font-medium mb-2">Última Simulação</h3>
                <div className="text-sm space-y-1">
                  <div>Energia: {simulationData.impact_energy_mt.toFixed(2)} MT</div>
                  <div>Tipo: {simulationData.impact_type}</div>
                  <div>Raio: {simulationData.fireball_radius_km.toFixed(2)} km</div>
                </div>
              </div>
            )}

            {/* IA de Otimização de Rotas */}
            {simulationData && (
              <div className="mt-6">
                <AIRouteOptimizer 
                  simulationData={simulationData}
                  onRoutesUpdate={handleAIRoutesUpdate}
                />
              </div>
            )}

            {/* Botão para Relatório Científico */}
            {simulationData && (
              <div className="mt-6">
                <button
                  onClick={() => setShowScientificReport(true)}
                  className="w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ease-in-out bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 hover:shadow-lg transform hover:scale-105 text-white flex items-center justify-center space-x-2"
                >
                  <span>📊</span>
                  <span>Relatório Científico Detalhado</span>
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Análise científica completa com magnitudes do desastre e planos de contenção
                </p>
              </div>
            )}

            {/* Informações de Atualização */}
            <div className="mt-4 text-xs opacity-60">
              Última atualização: {lastUpdate.toLocaleTimeString()}
                  </div>
                </div>
        </aside>

        {/* Área Principal */}
        <main className="flex-1 flex flex-col lg:flex-row">
          {/* Mapa */}
          <div className={`flex-1 transition-all duration-300 ${
            isFullscreen ? 'fixed inset-0 z-40' : 'relative'
          }`}>
            <div className="h-full relative">
              {/* Controles do Mapa */}
              <div className={`absolute top-4 right-4 z-10 flex space-x-2 ${
                darkMode ? 'bg-gray-800' : 'bg-white'
              } rounded-lg shadow-lg p-2`}>
                <button
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  className={`p-2 rounded transition-colors duration-200 will-change-auto ${
                    darkMode 
                      ? 'hover:bg-gray-700' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {isFullscreen ? '🔽' : '🔼'}
                </button>
              </div>
              
              {/* Botão Flutuante de Nova Simulação */}
              {isMapLocked && (
                <div className="absolute top-4 left-4 z-10">
                  <button
                    onClick={handleNewSimulation}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-6 py-3 rounded-lg shadow-lg transition-all duration-200 transform hover:scale-105 flex items-center gap-2 font-semibold"
                  >
                    <span className="text-lg">🔄</span>
                    <span>Nova Simulação</span>
                  </button>
                </div>
              )}
              
              {/* Indicador de Mapa Travado */}
              {isMapLocked && (
                <div className="absolute bottom-4 left-4 z-10">
                  <div className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
                    <span className="text-lg">🔒</span>
                    <span className="text-sm font-medium">Mapa Travado</span>
                  </div>
                </div>
              )}
              
                  <MapContainer
                center={center}
                zoom={8}
                minZoom={3}
                maxZoom={18}
                zoomControl={true}
                scrollWheelZoom={true}
                doubleClickZoom={true}
                touchZoom={true}
                boxZoom={true}
                keyboard={true}
                dragging={true}
                style={{ 
                  height: '100%', 
                  width: '100%',
                  cursor: isFullscreen ? 'grab' : 'default'
                }}
                className={`transition-all duration-300 ${
                  isFullscreen ? 'cursor-grab' : ''
                }`}
              >
                <MapController isFullscreen={isFullscreen} simulationData={simulationData} />
                <MapClickHandler onMapClick={handleMapClick} />
                
                    <TileLayer
                  url={darkMode 
                    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  }
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    
                {/* Marcador Central */}
                <Marker position={center}>
                      <Popup>
                    <div className="text-center">
                      <h3 className="font-bold text-red-600">Ponto de Impacto</h3>
                      <p className="text-sm">Coordenadas: {center[0].toFixed(4)}, {center[1].toFixed(4)}</p>
                    </div>
                      </Popup>
                    </Marker>
                    
                {/* Zonas de Perigo */}
                {showImpactZones && dangerZones.map((zone, index) => (
                    <Circle
                    key={index}
                    center={center}
                    radius={zone.radius * 1000}
                    pathOptions={{ 
                      color: zone.color, 
                      fillColor: zone.color, 
                      fillOpacity: zone.opacity 
                    }}
                  />
                ))}
                
                {/* Zonas Seguras */}
                {safeZones.map(zone => (
                    <Circle
                    key={zone.id}
                    center={zone.position}
                    radius={5000}
                    pathOptions={{ 
                      color: 'green', 
                      fillColor: 'green', 
                      fillOpacity: 0.3 
                    }}
                  />
                ))}
                
                {/* Abrigos */}
                {shelters.map(shelter => (
                  <Marker key={shelter.id} position={shelter.position}>
                    <Popup>
                    <div className="text-center">
                        <h3 className="font-bold text-green-600">🏠 {shelter.name}</h3>
                        <p className="text-sm">Capacidade: {shelter.capacity.toLocaleString()} pessoas</p>
                        <p className="text-sm">Distância: {shelter.distance.toFixed(1)} km</p>
                </div>
                    </Popup>
                  </Marker>
                ))}
                
                {/* Rotas de Evacuação */}
                {evacuationRoutes.map(route => (
                  <Polyline
                    key={route.id}
                    positions={[route.from, route.to]}
                    pathOptions={{ color: 'blue', weight: 3, opacity: 0.7 }}
                  />
                ))}
                
                {/* Rotas Otimizadas por IA */}
                {aiOptimizedRoutes.filter(route => route.from && route.to && route.from[0] && route.from[1] && route.to[0] && route.to[1]).map(route => (
                  <Polyline
                    key={`ai_${route.id}`}
                    positions={[route.from, route.to]}
                    pathOptions={{ 
                      color: route.color || '#8B5CF6', 
                      weight: 4, 
                      opacity: 0.8,
                      dashArray: '10, 5'
                    }}
                  />
                ))}
                
                {/* Marcadores para rotas de IA */}
                {aiOptimizedRoutes.filter(route => route.to && route.to[0] && route.to[1]).map(route => (
                  <Marker key={`ai_marker_${route.id}`} position={route.to}>
                    <Popup>
                      <div className="text-center">
                        <h3 className="font-bold text-purple-600">🧠 {route.name}</h3>
                        <p className="text-sm">Distância: {route.distance?.toFixed(1)} km</p>
                        <p className="text-sm">Tempo: {route.estimatedTime} min</p>
                        <p className="text-sm">Capacidade: {route.capacity?.toLocaleString()} pessoas</p>
                        <p className="text-sm">Eficiência: {route.efficiency}%</p>
                        <div className="mt-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          Otimizado por IA
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {/* Safe Zones */}
                {safeZones.filter(zone => zone.latitude && zone.longitude).map((zone, index) => (
                  <Marker key={`safe_zone_${index}`} position={[zone.latitude, zone.longitude]}>
                    <Popup>
                      <div className="text-center">
                        <div className="flex items-center justify-center gap-2 mb-2">
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: zone.color || '#10B981' }}
                          ></div>
                          <h3 className="font-bold text-green-600">🛡️ {zone.name}</h3>
                        </div>
                        <p className="text-sm"><strong>Distância:</strong> {zone.distance_from_impact_km} km</p>
                        <p className="text-sm"><strong>Score de Segurança:</strong> {(zone.safety_score * 100).toFixed(0)}%</p>
                        <p className="text-sm"><strong>Capacidade:</strong> {zone.capacity?.toLocaleString()} pessoas</p>
                        <div className="mt-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Zona Segura Calculada
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {/* Rotas Otimizadas */}
                {optimalRoutes.filter(route => route.route_coordinates && route.route_coordinates.length > 0).map((route, index) => (
                  <Polyline
                    key={`optimal_route_${index}`}
                    positions={route.route_coordinates}
                    pathOptions={{ 
                      color: route.color || '#3B82F6', 
                      weight: 3, 
                      opacity: 0.9,
                      dashArray: '5, 10'
                    }}
                  />
                ))}
                
                {/* Marcadores para rotas otimizadas */}
                {optimalRoutes.filter(route => route.zone_coordinates && route.zone_coordinates[0] && route.zone_coordinates[1]).map((route, index) => (
                  <Marker key={`optimal_marker_${index}`} position={[route.zone_coordinates[1], route.zone_coordinates[0]]}>
                    <Popup>
                      <div className="text-center">
                        <div className="flex items-center justify-center gap-2 mb-2">
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: route.color || '#3B82F6' }}
                          ></div>
                          <h3 className="font-bold text-blue-600">🗺️ {route.zone_name}</h3>
                        </div>
                        <p className="text-sm"><strong>Distância:</strong> {route.total_distance_km} km</p>
                        <p className="text-sm"><strong>Tempo:</strong> {route.estimated_time_minutes} min</p>
                        <p className="text-sm"><strong>Score de Segurança:</strong> {(route.safety_score * 100).toFixed(0)}%</p>
                        <p className="text-sm"><strong>Waypoints:</strong> {route.waypoints_count}</p>
                        <p className="text-sm"><strong>Algoritmo:</strong> {route.algorithm_used}</p>
                        <div className="mt-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Rota Otimizada Calculada
                    </div>
                  </div>
                    </Popup>
                  </Marker>
                ))}

                {/* Feedback visual de clique no mapa */}
                {mapClickFeedback && (
                  <Marker position={mapClickFeedback.position}>
                    <Popup>
                      <div className="text-center">
                        <h3 className="font-bold text-green-600 mb-2">📍 Nova Posição Selecionada</h3>
                        <p className="text-sm">
                          <strong>Latitude:</strong> {mapClickFeedback.position[0].toFixed(6)}
                        </p>
                        <p className="text-sm">
                          <strong>Longitude:</strong> {mapClickFeedback.position[1].toFixed(6)}
                        </p>
                        <div className="mt-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Posição atualizada automaticamente
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                )}
              </MapContainer>
            </div>
            </div>

          {/* Painel de Alertas - Responsivo */}
          <aside className="w-full lg:w-80 border-l border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
            <div className="p-6 h-full flex flex-col">
              <h2 className="text-lg font-semibold mb-6 text-gray-800">Alertas Recentes</h2>
              
              <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200">
                <div className="space-y-4 pr-2">
                  {filteredAlerts.length === 0 ? (
                    <div className="text-center py-8 opacity-60">
                      <div className="text-4xl mb-2">🔔</div>
                      <p>Nenhum alerta encontrado</p>
                    </div>
                  ) : (
                    filteredAlerts.map(alert => (
                      <div
                        key={alert.id}
                        className={`p-4 rounded-lg border transition-colors hover:shadow-md ${
                          alert.severity === 'critical' 
                            ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800'
                            : alert.severity === 'high'
                            ? 'bg-orange-50 border-orange-200 dark:bg-orange-900/20 dark:border-orange-800'
                            : 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            alert.severity === 'critical' 
                              ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                              : alert.severity === 'high'
                              ? 'bg-orange-100 text-orange-800 dark:bg-orange-800 dark:text-orange-100'
                              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                          }`}>
                            {alert.severity.toUpperCase()}
                      </div>
                          <span className="text-xs opacity-60">
                            {alert.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm font-medium mb-1">{alert.message}</p>
                        <p className="text-xs opacity-60">{alert.location}</p>
                      </div>
                    ))
              )}
              </div>
              </div>
            </div>
          </aside>
        </main>
      </div>

      {/* Relatório Científico Modal */}
      {showScientificReport && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
          <div className="absolute inset-0 overflow-y-auto">
            <div className="relative min-h-full">
              <button
                onClick={() => setShowScientificReport(false)}
                className="fixed top-4 right-4 z-10 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <span className="text-white text-xl">✕</span>
              </button>
              <ScientificReport 
                simulationData={simulationData}
                asteroidData={selectedAsteroid}
                onClose={() => setShowScientificReport(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AsteroidDashboard;