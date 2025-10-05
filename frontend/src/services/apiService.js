// API Service para integração com o backend Cosmos Sentinel
class CosmosSentinelAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/v1';
    this.timeout = 30000; // 30 segundos
  }

  // Método genérico para fazer requisições
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: this.timeout,
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      return { 
        success: false, 
        error: error.message,
        data: null 
      };
    }
  }

  // ===== SIMULAÇÃO DE IMPACTO =====
  async simulateImpact(simulationData) {
    return this.request('/simular', {
      method: 'POST',
      body: JSON.stringify(simulationData),
    });
  }

  // ===== DADOS DE ASTEROIDES (NASA NEO) =====
  async getAsteroidData(asteroidId) {
    return this.request(`/neo/${asteroidId}`);
  }

  async getEnhancedAsteroidData(asteroidId) {
    return this.request(`/neo/${asteroidId}/enhanced`);
  }

  async getAsteroidImpactAnalysis(asteroidId, impactLat, impactLon, impactAngle = 45, targetType = 'rocha') {
    const params = new URLSearchParams({
      impact_latitude: impactLat,
      impact_longitude: impactLon,
      impact_angle_deg: impactAngle,
      target_type: targetType,
    });
    return this.request(`/neo/${asteroidId}/impact-analysis?${params}`);
  }

  // ===== ZONAS DE RISCO GEOJSON =====
  async generateRiskZones(simulationData) {
    return this.request('/geojson/risk-zones', {
      method: 'POST',
      body: JSON.stringify(simulationData),
    });
  }

  async generateEvacuationZones(evacuationData) {
    return this.request('/geojson/evacuation-zones', {
      method: 'POST',
      body: JSON.stringify(evacuationData),
    });
  }

  // ===== ROTAS DE EVACUAÇÃO =====
  async calculateEvacuationRoutes(evacuationRequest) {
    return this.request('/evacuacao', {
      method: 'POST',
      body: JSON.stringify(evacuationRequest),
    });
  }

  async getEvacuationPoints(lat, lon, radiusKm = 50) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      radius_km: radiusKm,
    });
    return this.request(`/evacuacao/pontos?${params}`);
  }

  // ===== DADOS AMBIENTAIS =====
  async getEnvironmentalAnalysis(analysisRequest) {
    return this.request('/ambiental/comprehensive-analysis', {
      method: 'POST',
      body: JSON.stringify(analysisRequest),
    });
  }

  async getElevationData(lat, lon, bufferKm = 5) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      buffer_km: bufferKm,
    });
    return this.request(`/ambiental/elevation?${params}`);
  }

  async getTemperatureData(lat, lon, date = null) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
    });
    if (date) params.append('date', date);
    return this.request(`/ambiental/temperature?${params}`);
  }

  // ===== IMAGENS DE SATÉLITE =====
  async getSatelliteImagery(imageryRequest) {
    return this.request('/satelite/imagery', {
      method: 'POST',
      body: JSON.stringify(imageryRequest),
    });
  }

  async getMultiLayerAnalysis(analysisRequest) {
    return this.request('/satelite/multi-layer-analysis', {
      method: 'POST',
      body: JSON.stringify(analysisRequest),
    });
  }

  // ===== RELATÓRIOS =====
  async generateExecutiveReport(reportRequest) {
    return this.request('/relatorios/executivo', {
      method: 'POST',
      body: JSON.stringify(reportRequest),
    });
  }

  async generateSimulationReport(reportRequest) {
    return this.request('/relatorios/simulacao', {
      method: 'POST',
      body: JSON.stringify(reportRequest),
    });
  }

  // ===== DADOS DA NASA EARTHDATA =====
  async getUnifiedDataAccess(dataRequest) {
    return this.request('/earthdata/unified-access', {
      method: 'POST',
      body: JSON.stringify(dataRequest),
    });
  }

  async getMerra2Data(minLon, minLat, maxLon, maxLat, startDate, endDate) {
    const params = new URLSearchParams({
      min_lon: minLon,
      min_lat: minLat,
      max_lon: maxLon,
      max_lat: maxLat,
      start_date: startDate,
      end_date: endDate,
    });
    return this.request(`/earthdata/merra2?${params}`);
  }

  async getNasaDataSources() {
    return this.request('/earthdata/data-sources');
  }

  // ===== DEFESA CIVIL =====
  async getEmergencyCoordination(lat, lon, emergencyType = 'asteroid_impact') {
    const params = new URLSearchParams({
      lat: lat,
      lon: lon,
      emergency_type: emergencyType,
    });
    return this.request(`/defesa-civil/coordenacao?${params}`);
  }

  async getAvailableResources(lat, lon, alertLevel = 'orange') {
    const params = new URLSearchParams({
      lat: lat,
      lon: lon,
      alert_level: alertLevel,
    });
    return this.request(`/defesa-civil/recursos?${params}`);
  }

  // ===== MONITORAMENTO DE SAÚDE =====
  async getHealthInfrastructure(lat, lon, radiusKm = 25) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      radius_km: radiusKm,
    });
    return this.request(`/saude/infraestrutura?${params}`);
  }

  async getHealthMonitoring(lat, lon, date = null) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
    });
    if (date) params.append('date', date);
    return this.request(`/saude/monitoramento?${params}`);
  }

  // ===== DADOS GEOGRÁFICOS =====
  async getGeographicData(lat, lon) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
    });
    return this.request(`/dados-geograficos?${params}`);
  }

  // ===== RISCO LOCAL =====
  async checkLocalRisk(lat, lon, craterKm = 1.0) {
    const params = new URLSearchParams({
      lat: lat,
      lon: lon,
      crater_km: craterKm,
    });
    return this.request(`/risco-local?${params}`);
  }

  // ===== POPULAÇÃO =====
  async getPopulationData(lat, lon, radiusKm = 10) {
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lon,
      radius_km: radiusKm,
    });
    return this.request(`/populacao?${params}`);
  }

  // ===== UTILITÁRIOS =====
  async checkBackendHealth() {
    // Health check não precisa do prefixo /api/v1
    const url = 'http://localhost:8000/health';
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: this.timeout,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API Error [${url}]:`, error);
      throw error;
    }
  }

  // Método para testar conectividade
  async testConnection() {
    try {
      const result = await this.checkBackendHealth();
      return result.success;
    } catch (error) {
      return false;
    }
  }
}

// Instância global da API
const cosmosAPI = new CosmosSentinelAPI();

// Exportar para React
export { cosmosAPI };
export default cosmosAPI;
