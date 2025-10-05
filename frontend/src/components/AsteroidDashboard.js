import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { cosmosAPI } from '../services/apiService';

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

  useEffect(() => {
    if (simulationData?.fireball_radius_km > 0) {
      const radius = simulationData.fireball_radius_km * 1000;
      const zoomLevel = Math.max(6, Math.min(12, Math.floor(15 - Math.log10(radius / 1000))));
      map.setZoom(zoomLevel);
    }
  }, [simulationData, map]);

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
  const [darkMode, setDarkMode] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [apiStatus, setApiStatus] = useState('connecting');
  const [lastUpdate, setLastUpdate] = useState(new Date());
  
  // Estados de simulação
  const [simulationData, setSimulationData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Estados de filtros
  const [severityFilter, setSeverityFilter] = useState('all');
  const [zoneFilter, setZoneFilter] = useState('all');
  const [timeFilter, setTimeFilter] = useState('24h');
  
  // Estados de alertas
  const [alerts, setAlerts] = useState([]);
  
  // Estados de evacuação
  const [safeZones, setSafeZones] = useState([]);
  const [dangerZones, setDangerZones] = useState([]);
  const [evacuationRoutes, setEvacuationRoutes] = useState([]);
  const [shelters, setShelters] = useState([]);

  // Coordenadas padrão
  const [center] = useState([-3.7327, -38.5270]);

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
        capacity: 8000,
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
    const newAlerts = [
      {
        id: Date.now(),
        type: 'impact',
        severity: 'critical',
        message: `Impacto detectado: ${data.impact_energy_mt} MT`,
        timestamp: new Date(),
        location: 'Centro da cidade'
      },
      {
        id: Date.now() + 1,
        type: 'evacuation',
        severity: 'high',
        message: `Evacuação iniciada para zona de ${data.fireball_radius_km} km`,
        timestamp: new Date(),
        location: 'Todas as zonas afetadas'
      },
      {
        id: Date.now() + 2,
        type: 'seismic',
        severity: 'medium',
        message: `Terremoto magnitude ${data.seismic_magnitude} detectado`,
        timestamp: new Date(),
        location: 'Região metropolitana'
      }
    ];

    setAlerts(prev => [...newAlerts, ...prev].slice(0, 10));
  }, []);

  // Executar simulação
  const runSimulation = useCallback(async () => {
    setLoading(true);
    try {
      const result = await cosmosAPI.simulateImpact({
        diameter_m: 100,
        velocity_kms: 35,
        impact_angle_deg: 24,
        target_type: 'rocha',
        latitude: center[0],
        longitude: center[1]
      });

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

        setSimulationData(mappedData);
        generateZonesAndRoutes(mappedData);
        generateAlerts(mappedData);
      }
    } catch (error) {
      console.error('Erro na simulação:', error);
    } finally {
      setLoading(false);
    }
  }, [center, generateZonesAndRoutes, generateAlerts]);

  // Atualização automática
  useEffect(() => {
    const interval = setInterval(() => {
      checkApiStatus();
      setLastUpdate(new Date());
      if (simulationData) {
        runSimulation();
      }
    }, 15000);

    return () => clearInterval(interval);
  }, [checkApiStatus, runSimulation, simulationData]);

  // Inicialização
  useEffect(() => {
    checkApiStatus();
    runSimulation();
  }, [checkApiStatus, runSimulation]);

  // Filtrar alertas
  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter !== 'all' && alert.severity !== severityFilter) return false;
    if (timeFilter === '1h' && Date.now() - alert.timestamp.getTime() > 3600000) return false;
    if (timeFilter === '24h' && Date.now() - alert.timestamp.getTime() > 86400000) return false;
    return true;
  });

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode 
        ? 'bg-gray-900 text-white' 
        : 'bg-gray-50 text-gray-900'
    }`}>
      {/* Header Fixo */}
      <header className={`fixed top-0 left-0 right-0 z-50 border-b transition-colors duration-300 ${
        darkMode 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  darkMode ? 'bg-blue-600' : 'bg-blue-500'
                }`}>
                  <span className="text-xl">🌌</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold">COSMOS SENTINEL</h1>
                  <p className="text-sm opacity-70">Sistema de Monitoramento</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-4">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  apiStatus === 'online' 
                    ? 'bg-green-100 text-green-800' 
                    : apiStatus === 'connecting'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {apiStatus === 'online' ? '🟢 Online' : 
                   apiStatus === 'connecting' ? '🟡 Conectando' : '🔴 Offline'}
                </div>
                <Clock />
              </div>
              
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg transition-colors ${
                  darkMode 
                    ? 'hover:bg-gray-700' 
                    : 'hover:bg-gray-100'
                }`}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Layout Principal */}
      <div className="pt-20 flex h-screen">
        {/* Painel Lateral */}
        <aside className={`w-80 border-r transition-colors duration-300 ${
          darkMode 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-white border-gray-200'
        }`}>
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-6">Filtros e Controles</h2>
            
            {/* Filtros */}
            <div className="space-y-6">
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
            </div>

            {/* Botão de Simulação */}
            <div className="mt-8">
              <button
                onClick={runSimulation}
                disabled={loading}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  loading 
                    ? 'bg-gray-500 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white`}
              >
                {loading ? '🔄 Simulando...' : '🚀 Executar Simulação'}
              </button>
            </div>

            {/* Status da Simulação */}
            {simulationData && (
              <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <h3 className="font-medium mb-2">Última Simulação</h3>
                <div className="text-sm space-y-1">
                  <div>Energia: {simulationData.impact_energy_mt} MT</div>
                  <div>Tipo: {simulationData.impact_type}</div>
                  <div>Raio: {simulationData.fireball_radius_km} km</div>
                </div>
              </div>
            )}

            {/* Informações de Atualização */}
            <div className="mt-4 text-xs opacity-60">
              Última atualização: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </aside>

        {/* Área Principal */}
        <main className="flex-1 flex">
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
                  className={`p-2 rounded transition-colors ${
                    darkMode 
                      ? 'hover:bg-gray-700' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  {isFullscreen ? '🔽' : '🔼'}
                </button>
              </div>

              <MapContainer
                center={center}
                zoom={8}
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
                {dangerZones.map((zone, index) => (
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
              </MapContainer>
            </div>
          </div>

          {/* Painel de Alertas */}
          <aside className={`w-80 border-l transition-colors duration-300 ${
            darkMode 
              ? 'bg-gray-800 border-gray-700' 
              : 'bg-white border-gray-200'
          }`}>
            <div className="p-6">
              <h2 className="text-lg font-semibold mb-6">Alertas Recentes</h2>
              
              <div className="space-y-4">
                {filteredAlerts.length === 0 ? (
                  <div className="text-center py-8 opacity-60">
                    <div className="text-4xl mb-2">🔔</div>
                    <p>Nenhum alerta encontrado</p>
                  </div>
                ) : (
                  filteredAlerts.map(alert => (
                    <div
                      key={alert.id}
                      className={`p-4 rounded-lg border transition-colors ${
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
          </aside>
        </main>
      </div>
    </div>
  );
}

export default AsteroidDashboard;