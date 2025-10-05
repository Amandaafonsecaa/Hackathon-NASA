import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  AlertTriangle, 
  Users, 
  MapPin, 
  Clock, 
  TrendingUp,
  Shield,
  Zap,
  Globe,
  BarChart3,
  Download,
  Eye,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const ScientificReport = ({ simulationData, asteroidData, onClose }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    executive: true,
    threat: true,
    zones: true,
    infrastructure: true,
    humanitarian: true,
    costs: true,
    timeline: true
  });

  // Gerar dados do relatório baseado na simulação
  useEffect(() => {
    if (simulationData) {
      generateReportData();
    }
  }, [simulationData, asteroidData]);

  const generateReportData = () => {
    setIsGenerating(true);
    
    // Simular processamento
    setTimeout(() => {
      // Obter dados da simulação atual
      const diameter = simulationData?.diameter_m || 200;
      const velocity = simulationData?.velocity_kms || 17;
      const angle = simulationData?.impact_angle_deg || 30;
      const targetType = simulationData?.target_type || 'solo';
      
      // Calcular energia cinética baseada nas características reais
      const mass = Math.PI * Math.pow(diameter / 2, 3) * 3000; // Densidade média de 3000 kg/m³
      const energyJoules = 0.5 * mass * Math.pow(velocity * 1000, 2);
      const energyMegatons = energyJoules / (4.184e15); // Conversão para megatons TNT
      
      // Calcular magnitude sísmica baseada na energia
      const seismicMagnitude = Math.log10(energyMegatons) + 4.0;
      
      // Calcular diâmetro da cratera baseado na energia e ângulo
      const craterDiameter = Math.pow(energyMegatons, 0.294) * (Math.sin(angle * Math.PI / 180) ** 0.5);
      
      // Calcular raio da fireball baseado na energia
      const fireballRadius = Math.pow(energyMegatons, 0.4) * 0.5;
      
      // Calcular intensidade da onda de choque baseada na energia e distância
      const shockwaveIntensity = 120 + Math.log10(energyMegatons) * 10;
      
      // Calcular ventos máximos baseados na energia
      const peakWinds = Math.pow(energyMegatons, 0.3) * 50;
      
      // Determinar tipo de impacto baseado no tamanho e velocidade
      const isAirburst = diameter < 150 || velocity > 50;
      const impactType = isAirburst ? 'AIRBURST ATMOSFÉRICO' : 'IMPACTO DIRETO';
      
      // Calcular população afetada baseada no raio da fireball
      const populationDensity = 200; // pessoas por km² (média urbana)
      const affectedPopulation = Math.PI * Math.pow(fireballRadius * 2, 2) * populationDensity;
      
      // Calcular custos baseados na energia e população
      const evacuationCost = affectedPopulation * 500; // R$ 500 por pessoa evacuada
      const infrastructureCost = energyMegatons * 1000000000; // R$ 1B por megaton
      
      const data = {
        // Dados do asteroide baseados na simulação
        asteroid: {
          name: asteroidData?.name || `Asteroide ${diameter}m`,
          id: asteroidData?.id || `SIM-${diameter}-${velocity}`,
          diameter: diameter,
          velocity: velocity,
          angle: angle,
          classification: diameter > 140 ? "Potentially Hazardous Asteroid (PHA)" : "Near-Earth Object (NEO)",
          probability: Math.min(95, 60 + (diameter / 10)), // Probabilidade baseada no tamanho
          confidence: "±3%",
          impactDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString('pt-BR'),
          localTime: new Date().toLocaleTimeString('pt-BR'),
          location: `Lat: ${simulationData?.latitude?.toFixed(4) || -3.7327}, Lon: ${simulationData?.longitude?.toFixed(4) || -38.5270}`
        },
        
        // Análise de impacto baseada em cálculos reais
        impact: {
          energy: energyMegatons,
          seismic: seismicMagnitude,
          crater: craterDiameter,
          fireball: fireballRadius,
          shockwave: shockwaveIntensity,
          winds: peakWinds,
          type: impactType,
          targetType: targetType
        },
        
        // Zonas de impacto calculadas dinamicamente
        zones: {
          direct: {
            radius: craterDiameter / 2,
            population: 0,
            vessels: Math.floor(affectedPopulation / 10000),
            description: isAirburst ? "Explosão atmosférica" : "Cratera de impacto"
          },
          tsunami: targetType === 'oceano' ? {
            radius: fireballRadius * 0.8,
            population: Math.floor(affectedPopulation * 0.3),
            height: `${Math.floor(fireballRadius * 2)}-${Math.floor(fireballRadius * 3)} metros`,
            municipalities: [
              { name: "Zona Costeira", population: Math.floor(affectedPopulation * 0.2), neighborhoods: ["Praia", "Porto"] }
            ]
          } : {
            radius: fireballRadius * 0.5,
            population: Math.floor(affectedPopulation * 0.1),
            height: "N/A (Impacto terrestre)",
            municipalities: []
          },
          moderate: {
            radius: fireballRadius * 1.5,
            population: Math.floor(affectedPopulation * 0.6),
            height: `${Math.floor(fireballRadius)}-${Math.floor(fireballRadius * 1.5)} metros`,
            description: "Danos estruturais significativos"
          },
          shockwave: {
            radius: fireballRadius * 5,
            population: Math.floor(affectedPopulation * 3),
            intensity: `>${Math.floor(shockwaveIntensity)} dB`,
            description: "Estrondo sônico, quebra de vidros"
          },
          seismic: {
            radius: fireballRadius * 10,
            population: Math.floor(affectedPopulation * 8),
            magnitude: `M ${(seismicMagnitude - 1).toFixed(1)} - ${seismicMagnitude.toFixed(1)}`,
            description: "Tremores detectáveis"
          }
        },
        
        // Infraestrutura crítica baseada na localização
        infrastructure: {
          critical: [
            { name: "Zona de Impacto Direto", location: "Centro do impacto", zone: "Crítica", status: "🔴 Destruição Total", action: "Evacuação imediata" },
            { name: "Infraestrutura Local", location: "Raio de 5km", zone: "Alta", status: "🟡 Danos Severos", action: "Reinforço estrutural" }
          ],
          high: [
            { name: "Sistemas de Transporte", location: "Raio de 15km", zone: "Média", action: "Desvio de rotas" },
            { name: "Comunicações", location: "Raio de 25km", zone: "Baixa", action: "Backup de sistemas" }
          ]
        },
        
        // Recursos humanitários calculados dinamicamente
        humanitarian: {
          totalAffected: Math.floor(affectedPopulation * 4),
          mandatoryEvacuation: Math.floor(affectedPopulation * 0.8),
          recommendedEvacuation: Math.floor(affectedPopulation * 1.5),
          monitoring: Math.floor(affectedPopulation * 1.7),
          shelters: {
            current: { units: Math.floor(affectedPopulation / 1000), capacity: Math.floor(affectedPopulation * 0.3) },
            deficit: Math.floor(affectedPopulation * 0.5),
            solution: {
              schools: { units: Math.floor(affectedPopulation / 2000), capacity: Math.floor(affectedPopulation * 0.2) },
              camps: { units: Math.floor(affectedPopulation / 5000), capacity: Math.floor(affectedPopulation * 0.15) },
              interior: { capacity: Math.floor(affectedPopulation * 0.1) },
              solidarity: { capacity: Math.floor(affectedPopulation * 0.05) }
            }
          },
          logistics: {
            water: { daily: Math.floor(affectedPopulation * 3), status: "70% disponível" },
            food: { daily: Math.floor(affectedPopulation * 1.5), status: "85% disponível" },
            hygiene: { kits: Math.floor(affectedPopulation * 0.8), status: "60% disponível" },
            blankets: { units: Math.floor(affectedPopulation * 1.2), status: "80% disponível" },
            medicine: { tons: Math.floor(affectedPopulation / 1000000), status: "90% disponível" }
          }
        },
        
        // Custos estimados baseados na energia e população
        costs: {
          operational: {
            evacuation: evacuationCost,
            shelters: evacuationCost * 0.8,
            hospitals: evacuationCost * 0.3,
            military: evacuationCost * 0.4,
            total: evacuationCost * 2.5
          },
          damagesAvoided: {
            lives: { saved: Math.floor(affectedPopulation * 0.1), range: `${Math.floor(affectedPopulation * 0.05)}-${Math.floor(affectedPopulation * 0.15)}` },
            infrastructure: infrastructureCost,
            economy: infrastructureCost * 0.6
          },
          roi: 4.2
        },
        
        // Timeline baseada na proximidade do impacto
        timeline: [
          { time: "T-168h", action: "Relatório científico publicado", status: "✅" },
          { time: "T-144h", action: "Ativação de protocolos emergenciais", status: "🎯" },
          { time: "T-120h", action: "Início da evacuação voluntária", status: "🎯" },
          { time: "T-72h", action: "Evacuação obrigatória anunciada", status: "🎯" },
          { time: "T-48h", action: "70% da população evacuada", status: "🎯" },
          { time: "T-24h", action: "Evacuação concluída (95%)", status: "🎯" },
          { time: "T-0", action: "IMPACTO", status: "🔴" },
          { time: "T+1h", action: "Avaliação inicial de danos", status: "🟡" },
          { time: "T+24h", action: "Início das operações de resgate", status: "🟡" }
        ]
      };
      
      setReportData(data);
      setIsGenerating(false);
    }, 2000);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const downloadReport = () => {
    // Implementar download do relatório em PDF
    console.log('Downloading scientific report...');
  };

  if (!simulationData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
        <div className="container mx-auto px-6 py-12">
          <div className="text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-blue-400" />
            <h1 className="text-3xl font-bold mb-4">Relatório Científico</h1>
            <p className="text-gray-300 mb-8">
              Execute uma simulação primeiro para gerar o relatório científico detalhado
            </p>
            <div className="bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
              <p className="text-sm text-gray-300">
                Este relatório contém análises científicas detalhadas sobre magnitudes do desastre 
                e planos de contenção baseados em dados de simulação.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isGenerating) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold mb-2">Gerando Relatório Científico</h2>
          <p className="text-gray-300">Processando dados de impacto e planos de contenção...</p>
        </div>
      </div>
    );
  }

  if (!reportData) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
      {/* Header */}
      <div className="bg-black/50 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">RELATÓRIO DE ANÁLISE DE IMPACTO METEÓRICO</h1>
                <p className="text-sm text-gray-300">Sistema Nacional de Defesa Civil - Classificação: URGENTE</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2"
              >
                <span>←</span>
                Voltar
              </button>
              <button
                onClick={downloadReport}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
              <div className="px-3 py-2 bg-red-600 rounded-lg text-sm font-medium">
                🔴 URGENTE
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Sumário Executivo */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-red-900/50 to-orange-900/50 rounded-lg p-6 border border-red-500/50 cursor-pointer"
            onClick={() => toggleSection('executive')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-red-400" />
                📋 SUMÁRIO EXECUTIVO
              </h2>
              {expandedSections.executive ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.executive && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Objeto:</span>
                      <span className="font-semibold">{reportData.asteroid.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Classificação:</span>
                      <span className="font-semibold">{reportData.asteroid.classification}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Probabilidade:</span>
                      <span className="font-semibold text-red-400">{reportData.asteroid.probability}% ({reportData.asteroid.confidence})</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Data/Hora:</span>
                      <span className="font-semibold">{reportData.asteroid.impactDate}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Localização:</span>
                      <span className="font-semibold">{reportData.asteroid.location}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Nível de Alerta:</span>
                      <span className="font-semibold text-red-400">🔴 VERMELHO - EVACUAÇÃO IMEDIATA</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 mt-4">
                  <h3 className="font-semibold text-red-300 mb-2">Decisão Recomendada:</h3>
                  <p className="text-sm">
                    Evacuação total de áreas costeiras num raio de 50 km. Mobilização de recursos nacionais e internacionais. 
                    Declaração de Estado de Emergência em 6 estados do Nordeste.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Análise de Ameaça */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-orange-900/50 to-yellow-900/50 rounded-lg p-6 border border-orange-500/50 cursor-pointer"
            onClick={() => toggleSection('threat')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <Zap className="w-6 h-6 text-orange-400" />
                1️⃣ ANÁLISE DE AMEAÇA E CENÁRIOS DE IMPACTO
              </h2>
              {expandedSections.threat ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.threat && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-orange-300">Características do Objeto</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Diâmetro Estimado:</span>
                        <span className="font-semibold">{reportData.asteroid.diameter} metros</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Velocidade de Entrada:</span>
                        <span className="font-semibold">{reportData.asteroid.velocity} km/s</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Ângulo de Impacto:</span>
                        <span className="font-semibold">{reportData.asteroid.angle}°</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tipo de Terreno:</span>
                        <span className="font-semibold">{reportData.impact.targetType}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Energia Cinética:</span>
                        <span className="font-semibold">{reportData.impact.energy.toFixed(2)} Megatons TNT</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Massa Estimada:</span>
                        <span className="font-semibold">{((Math.PI * Math.pow(reportData.asteroid.diameter / 2, 3) * 3000) / 1000).toFixed(0)} toneladas</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-orange-300">Tipo de Impacto</h3>
                    <div className="bg-orange-900/30 border border-orange-500/50 rounded-lg p-4">
                      <h4 className="font-semibold text-orange-300 mb-2">{reportData.impact.type}</h4>
                      <div className="space-y-2 text-sm">
                        {reportData.impact.type === 'AIRBURST ATMOSFÉRICO' ? (
                          <>
                            <div className="flex justify-between">
                              <span>T+00:00</span>
                              <span>Explosão atmosférica a {Math.floor(reportData.impact.fireball * 0.8)} km de altitude</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+00:05</span>
                              <span>Onda de choque atinge o solo ({Math.floor(reportData.impact.shockwave)} dB)</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+00:30</span>
                              <span>Ventos de {Math.floor(reportData.impact.winds)} km/h</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+02:00</span>
                              <span>Efeitos secundários cessam</span>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="flex justify-between">
                              <span>T+00:00</span>
                              <span>Impacto direto - cratera de {reportData.impact.crater.toFixed(1)} km</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+00:03</span>
                              <span>Ejeção de material a {Math.floor(reportData.impact.fireball * 2)} km</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+00:15</span>
                              <span>Onda de choque ({Math.floor(reportData.impact.shockwave)} dB)</span>
                            </div>
                            <div className="flex justify-between">
                              <span>T+01:00</span>
                              <span>Terremoto M {reportData.impact.seismic.toFixed(1)}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400">{reportData.impact.seismic.toFixed(1)}</div>
                    <div className="text-sm text-gray-300">Magnitude Sísmica</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-400">{reportData.impact.crater.toFixed(1)} km</div>
                    <div className="text-sm text-gray-300">Diâmetro da Cratera</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-red-400">{reportData.impact.fireball.toFixed(1)} km</div>
                    <div className="text-sm text-gray-300">Raio da Fireball</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-orange-400">{Math.floor(reportData.impact.shockwave)} dB</div>
                    <div className="text-sm text-gray-300">Intensidade da Onda</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-400">{Math.floor(reportData.impact.winds)} km/h</div>
                    <div className="text-sm text-gray-300">Ventos Máximos</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-400">{reportData.impact.energy.toFixed(2)} MT</div>
                    <div className="text-sm text-gray-300">Energia Total</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Zonas de Impacto */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-red-900/50 to-pink-900/50 rounded-lg p-6 border border-red-500/50 cursor-pointer"
            onClick={() => toggleSection('zones')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <MapPin className="w-6 h-6 text-red-400" />
                2️⃣ ZONAS DE IMPACTO E POPULAÇÃO AFETADA
              </h2>
              {expandedSections.zones ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.zones && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4">
                    <h3 className="font-semibold text-red-300 mb-2">Zona 1: Impacto Direto</h3>
                    <div className="space-y-1 text-sm">
                      <div>Raio: {reportData.zones.direct.radius} km</div>
                      <div>População: {reportData.zones.direct.population.toLocaleString()}</div>
                      <div>Embarcações: {reportData.zones.direct.vessels}</div>
                    </div>
                  </div>
                  
                  <div className="bg-orange-900/30 border border-orange-500/50 rounded-lg p-4">
                    <h3 className="font-semibold text-orange-300 mb-2">Zona 2: Tsunami Crítico</h3>
                    <div className="space-y-1 text-sm">
                      <div>População: {reportData.zones.tsunami.population.toLocaleString()}</div>
                      <div>Altura: {reportData.zones.tsunami.height}</div>
                      <div>Municípios: {reportData.zones.tsunami.municipalities.length}</div>
                    </div>
                  </div>
                  
                  <div className="bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-4">
                    <h3 className="font-semibold text-yellow-300 mb-2">Zona 3: Inundação Moderada</h3>
                    <div className="space-y-1 text-sm">
                      <div>População: {reportData.zones.moderate.population.toLocaleString()}</div>
                      <div>Raio: {reportData.zones.moderate.radius} km</div>
                      <div>Altura: {reportData.zones.moderate.height}</div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="font-semibold text-white mb-3">Municípios Críticos - Zona Tsunami</h3>
                  <div className="space-y-2">
                    {reportData.zones.tsunami.municipalities.map((city, index) => (
                      <div key={index} className="flex justify-between items-center bg-gray-700 rounded p-2">
                        <div>
                          <span className="font-semibold">{city.name}</span>
                          <span className="text-sm text-gray-300 ml-2">({city.population.toLocaleString()} pessoas)</span>
                        </div>
                        <div className="text-sm text-gray-400">
                          {city.neighborhoods.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Infraestrutura Crítica */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-purple-900/50 to-indigo-900/50 rounded-lg p-6 border border-purple-500/50 cursor-pointer"
            onClick={() => toggleSection('infrastructure')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <Shield className="w-6 h-6 text-purple-400" />
                3️⃣ INFRAESTRUTURA CRÍTICA EM RISCO
              </h2>
              {expandedSections.infrastructure ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.infrastructure && (
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-red-300">🔴 CRÍTICO - Evacuação/Reforço Imediato</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {reportData.infrastructure.critical.map((item, index) => (
                      <div key={index} className="bg-red-900/30 border border-red-500/50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-white">{item.name}</h4>
                          <span className="text-sm font-semibold text-red-300">{item.status}</span>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>Localização: {item.location}</div>
                          <div>Zona: {item.zone}</div>
                          <div className="text-red-300 font-medium">Ação: {item.action}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-orange-300">🟡 ALTA PRIORIDADE - Preparação</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {reportData.infrastructure.high.map((item, index) => (
                      <div key={index} className="bg-orange-900/30 border border-orange-500/50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-white">{item.name}</h4>
                        </div>
                        <div className="text-sm text-gray-300 space-y-1">
                          <div>Localização: {item.location}</div>
                          <div>Zona: {item.zone}</div>
                          <div className="text-orange-300 font-medium">Ação: {item.action}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recursos Humanitários */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-green-900/50 to-teal-900/50 rounded-lg p-6 border border-green-500/50 cursor-pointer"
            onClick={() => toggleSection('humanitarian')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <Users className="w-6 h-6 text-green-400" />
                4️⃣ RELATÓRIO DE RECURSOS HUMANITÁRIOS
              </h2>
              {expandedSections.humanitarian ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.humanitarian && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-400">{reportData.humanitarian.totalAffected.toLocaleString()}</div>
                    <div className="text-sm text-gray-300">População Total Afetada</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-red-400">{reportData.humanitarian.mandatoryEvacuation.toLocaleString()}</div>
                    <div className="text-sm text-gray-300">Evacuação Obrigatória</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-orange-400">{reportData.humanitarian.recommendedEvacuation.toLocaleString()}</div>
                    <div className="text-sm text-gray-300">Evacuação Recomendada</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-400">{reportData.humanitarian.monitoring.toLocaleString()}</div>
                    <div className="text-sm text-gray-300">Monitoramento</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="font-semibold text-green-300 mb-3">Capacidade de Abrigos</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Abrigos Atuais:</span>
                        <span>{reportData.humanitarian.shelters.current.units} unidades ({reportData.humanitarian.shelters.current.capacity.toLocaleString()} vagas)</span>
                      </div>
                      <div className="flex justify-between text-red-300">
                        <span>Déficit:</span>
                        <span>{reportData.humanitarian.shelters.deficit.toLocaleString()} vagas</span>
                      </div>
                      <div className="mt-3 space-y-1">
                        <div className="text-sm">Solução Proposta:</div>
                        <div className="text-sm text-gray-300">• Escolas/Ginásios: +{reportData.humanitarian.shelters.solution.schools.capacity.toLocaleString()} vagas</div>
                        <div className="text-sm text-gray-300">• Acampamentos: +{reportData.humanitarian.shelters.solution.camps.capacity.toLocaleString()} vagas</div>
                        <div className="text-sm text-gray-300">• Interior: +{reportData.humanitarian.shelters.solution.interior.capacity.toLocaleString()} vagas</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="font-semibold text-green-300 mb-3">Necessidades Logísticas (7 dias)</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Água Potável:</span>
                        <span>{reportData.humanitarian.logistics.water.daily.toLocaleString()} L/dia</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Alimentos:</span>
                        <span>{reportData.humanitarian.logistics.food.daily.toLocaleString()}/dia</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Kits Higiene:</span>
                        <span>{reportData.humanitarian.logistics.hygiene.kits.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Cobertores:</span>
                        <span>{reportData.humanitarian.logistics.blankets.units.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Custos */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-yellow-900/50 to-amber-900/50 rounded-lg p-6 border border-yellow-500/50 cursor-pointer"
            onClick={() => toggleSection('costs')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <TrendingUp className="w-6 h-6 text-yellow-400" />
                5️⃣ ESTIMATIVA DE CUSTOS
              </h2>
              {expandedSections.costs ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.costs && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="font-semibold text-yellow-300 mb-3">Custos Operacionais</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Evacuação e Transporte:</span>
                        <span>R$ {(reportData.costs.operational.evacuation / 1000000).toFixed(0)}M</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Abrigos e Suprimentos:</span>
                        <span>R$ {(reportData.costs.operational.shelters / 1000000).toFixed(0)}M</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Hospitais de Campanha:</span>
                        <span>R$ {(reportData.costs.operational.hospitals / 1000000).toFixed(0)}M</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Forças Armadas:</span>
                        <span>R$ {(reportData.costs.operational.military / 1000000).toFixed(0)}M</span>
                      </div>
                      <div className="flex justify-between font-semibold text-yellow-300 border-t pt-2">
                        <span>SUBTOTAL:</span>
                        <span>R$ {(reportData.costs.operational.total / 1000000).toFixed(0)}M</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-800 rounded-lg p-4">
                    <h3 className="font-semibold text-green-300 mb-3">Danos Evitados</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Vidas Salvas:</span>
                        <span>{reportData.costs.damagesAvoided.lives.range} pessoas</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Infraestrutura:</span>
                        <span>R$ {(reportData.costs.damagesAvoided.infrastructure / 1000000000).toFixed(0)}B</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Economia Regional:</span>
                        <span>R$ {(reportData.costs.damagesAvoided.economy / 1000000000).toFixed(0)}B/ano</span>
                      </div>
                      <div className="flex justify-between font-semibold text-green-300 border-t pt-2">
                        <span>ROI da Evacuação:</span>
                        <span>R$ {reportData.costs.roi} por R$ 1 investido</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Timeline */}
        <div className="mb-8">
          <div 
            className="bg-gradient-to-r from-blue-900/50 to-cyan-900/50 rounded-lg p-6 border border-blue-500/50 cursor-pointer"
            onClick={() => toggleSection('timeline')}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold flex items-center gap-3">
                <Clock className="w-6 h-6 text-blue-400" />
                6️⃣ TIMELINE CONSOLIDADA
              </h2>
              {expandedSections.timeline ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
            
            {expandedSections.timeline && (
              <div className="space-y-4">
                {reportData.timeline.map((event, index) => (
                  <div key={index} className="flex items-center space-x-4 bg-gray-800 rounded-lg p-4">
                    <div className="text-sm font-mono text-blue-300 min-w-[120px]">{event.time}</div>
                    <div className="text-lg">{event.status}</div>
                    <div className="flex-1 text-white">{event.action}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Metadados */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
          <h3 className="text-lg font-semibold mb-4 text-gray-300">🔬 METADADOS DO RELATÓRIO</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Gerado por:</span>
                <span>Sistema Nacional de Análise de Ameaças Espaciais (SNAAE-IA)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Modelo de IA:</span>
                <span>Claude Sonnet 4.5 + Módulos Especializados</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Confiança Geral:</span>
                <span className="text-green-400">91%</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Última Atualização:</span>
                <span>{new Date().toLocaleString('pt-BR')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Próxima Atualização:</span>
                <span>Em 6 horas (ou sob demanda)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Contato Emergencial:</span>
                <span className="text-blue-400">defesacivil.emergencia@gov.br</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScientificReport;
