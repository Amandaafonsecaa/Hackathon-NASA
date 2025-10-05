import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Shield, 
  Users, 
  Clock, 
  MapPin, 
  Activity,
  Phone,
  FileText,
  CheckCircle,
  AlertCircle,
  Truck,
  Home,
  Heart,
  Building,
  Car,
  Plane,
  Map,
  Navigation,
  Fuel,
  Wifi
} from 'lucide-react';

const GovernmentDashboard = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const alertLevel = 'VERMELHO';
  const evacuationProgress = 23;
  const timeToImpact = 168; // horas

  // Dados do relatório
  const impactData = {
    asteroid: {
      name: "2025 FX14",
      diameter: "180-210m",
      velocity: "19.4 km/s",
      angle: "43°",
      energy: "22.5 Megatons TNT",
      probability: "78% (±4%)",
      impactTime: "12/10/2025, 14:23 UTC",
      location: "Oceano Atlântico, 320 km a leste de Fortaleza/CE"
    },
    tsunami: {
      height: "12-18m",
      arrivalTime: "T+42min",
      affectedPopulation: 487320,
      criticalNeighborhoods: [
        { name: "Praia do Futuro", population: 45000, risk: "CRÍTICO", coordinates: [-3.7200, -38.4800], evacuationRoute: "BR-116" },
        { name: "Mucuripe", population: 38000, risk: "CRÍTICO", coordinates: [-3.7166, -38.4666], evacuationRoute: "BR-304" },
        { name: "Serviluz", population: 32000, risk: "CRÍTICO", coordinates: [-3.7100, -38.4600], evacuationRoute: "BR-116" },
        { name: "Meireles", population: 28000, risk: "ALTO", coordinates: [-3.7300, -38.5000], evacuationRoute: "CE-085" },
        { name: "Aldeota", population: 35000, risk: "ALTO", coordinates: [-3.7400, -38.5200], evacuationRoute: "CE-060" },
        { name: "Praia de Iracema", population: 25000, risk: "ALTO", coordinates: [-3.7200, -38.5000], evacuationRoute: "BR-304" },
        { name: "Varjota", population: 18000, risk: "MODERADO", coordinates: [-3.7500, -38.5300], evacuationRoute: "CE-090" },
        { name: "Dionísio Torres", population: 22000, risk: "MODERADO", coordinates: [-3.7600, -38.5400], evacuationRoute: "CE-090" }
      ]
    },
    infrastructure: {
      critical: [
        { name: "Porto de Mucuripe", status: "DESTRUIÇÃO TOTAL", action: "Evacuar equipamentos" },
        { name: "Aeroporto Pinto Martins", status: "DANOS SEVEROS", action: "Cancelar voos após 10:00" },
        { name: "Hospital Geral Fortaleza", status: "EVACUAÇÃO OBRIGATÓRIA", action: "Transferir 342 pacientes" },
        { name: "Usina Termelétrica Pecém", status: "SHUTDOWN NECESSÁRIO", action: "Desligar reatores até 06:00" }
      ]
    },
    resources: {
      shelters: { available: 287, capacity: 94300, needed: 1612000, deficit: 1517700 },
      water: { daily: 11300000, available: 68, status: "CRÍTICO" },
      food: { daily: 4800000, available: 92, status: "OK" },
      medical: { patients: 2847, beds: 2400, status: "INSUFICIENTE" }
    },
    timeline: [
      { time: "T-168h", action: "Relatório publicado", status: "completed" },
      { time: "T-144h", action: "Decreto de Estado de Emergência", status: "pending" },
      { time: "T-120h", action: "Evacuação obrigatória anunciada", status: "pending" },
      { time: "T-72h", action: "70% da população evacuada", status: "pending" },
      { time: "T-48h", action: "90% da população evacuada", status: "pending" },
      { time: "T-24h", action: "Evacuação concluída (95%)", status: "pending" },
      { time: "T-0", action: "IMPACTO", status: "critical" }
    ],
    roadRoutes: {
      primary: [
        { 
          name: "BR-116 (Fortaleza → Maracanaú)", 
          status: "OPERACIONAL", 
          capacity: 12000, 
          congestion: "BAIXO",
          distance: "25 km",
          time: "45 min",
          fuel: "SUFICIENTE",
          priority: "ALTA",
          color: "#3B82F6",
          coordinates: [[-3.7327, -38.5270], [-3.7500, -38.5500]]
        },
        { 
          name: "CE-040 (Fortaleza → Aquiraz)", 
          status: "BLOQUEADA", 
          capacity: 0, 
          congestion: "CRÍTICO",
          distance: "15 km",
          time: "N/A",
          fuel: "N/A",
          priority: "N/A",
          reason: "Direção ao mar - RISCO",
          color: "#EF4444",
          coordinates: [[-3.7327, -38.5270], [-3.7200, -38.4800]]
        },
        { 
          name: "BR-304 (Fortaleza → Eusébio)", 
          status: "OPERACIONAL", 
          capacity: 8000, 
          congestion: "MÉDIO",
          distance: "20 km",
          time: "35 min",
          fuel: "SUFICIENTE",
          priority: "ALTA",
          color: "#3B82F6",
          coordinates: [[-3.7327, -38.5270], [-3.7400, -38.5400]]
        },
        { 
          name: "CE-085 (Fortaleza → Caucaia)", 
          status: "OPERACIONAL", 
          capacity: 6000, 
          congestion: "BAIXO",
          distance: "18 km",
          time: "30 min",
          fuel: "SUFICIENTE",
          priority: "MÉDIA",
          color: "#3B82F6",
          coordinates: [[-3.7327, -38.5270], [-3.7300, -38.5100]]
        }
      ],
      secondary: [
        { 
          name: "CE-060 (Fortaleza → Pacatuba)", 
          status: "OPERACIONAL", 
          capacity: 4000, 
          congestion: "BAIXO",
          distance: "22 km",
          time: "40 min",
          fuel: "SUFICIENTE",
          priority: "MÉDIA"
        },
        { 
          name: "CE-090 (Fortaleza → Maranguape)", 
          status: "OPERACIONAL", 
          capacity: 3500, 
          congestion: "BAIXO",
          distance: "28 km",
          time: "50 min",
          fuel: "SUFICIENTE",
          priority: "BAIXA"
        }
      ],
      emergency: [
        { 
          name: "Rota de Emergência A1", 
          status: "ATIVA", 
          capacity: 2000, 
          congestion: "BAIXO",
          distance: "30 km",
          time: "60 min",
          fuel: "SUFICIENTE",
          priority: "CRÍTICA",
          description: "Via alternativa para hospitais"
        },
        { 
          name: "Rota de Emergência A2", 
          status: "ATIVA", 
          capacity: 1500, 
          congestion: "BAIXO",
          distance: "35 km",
          time: "70 min",
          fuel: "SUFICIENTE",
          priority: "CRÍTICA",
          description: "Via alternativa para aeroporto"
        }
      ]
    }
  };

  // Atualizar tempo em tempo real
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-900/30';
      case 'pending': return 'text-yellow-400 bg-yellow-900/30';
      case 'critical': return 'text-red-400 bg-red-900/30';
      case 'CRÍTICO': return 'text-red-400';
      case 'ALTO': return 'text-orange-400';
      case 'MODERADO': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-blue-900 text-white">
      {/* Header Governamental Moderno */}
      <header className="bg-blue-800/95 backdrop-blur-md border-b border-blue-500/30 sticky top-0 z-50 shadow-lg">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="relative">
                <Shield className="w-16 h-16 text-blue-400 drop-shadow-lg" />
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-white">!</span>
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  SISTEMA NACIONAL DE DEFESA CIVIL
                </h1>
                <p className="text-lg text-blue-300 font-medium">Relatório de Análise de Impacto Meteórico</p>
                <div className="flex items-center gap-4 mt-2">
                  <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-semibold border border-red-500/30">
                    URGENTE
                  </span>
                  <span className="px-3 py-1 bg-orange-500/20 text-orange-400 rounded-full text-sm font-semibold border border-orange-500/30">
                    CLASSIFICAÇÃO CONFIDENCIAL
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="bg-blue-800/50 rounded-lg p-4 border border-blue-500/30">
                <div className="text-lg font-mono text-blue-400 mb-2">
                  {currentTime.toLocaleString('pt-BR')}
                </div>
                <div className="text-2xl font-bold text-red-400 mb-1">
                  🔴 ALERTA: {alertLevel}
                </div>
                <div className="text-sm text-gray-300 mb-3">
                  T-{timeToImpact}h até impacto
                </div>
                <button
                  onClick={() => window.location.href = '?dashboard=simulation'}
                  className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-4 py-2 rounded-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
                >
                  🔬 Dashboard Simulação
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Sumário Executivo Moderno */}
        <div className="mb-12">
          <div className="bg-gradient-to-br from-blue-700/80 to-blue-800/80 backdrop-blur-lg rounded-2xl border-2 border-blue-400/50 p-8 shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <FileText className="w-8 h-8 text-blue-400" />
              </div>
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                SUMÁRIO EXECUTIVO
              </span>
            </h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="space-y-4">
                <div className="bg-blue-600/60 rounded-xl p-4 border-2 border-blue-400/40 hover:border-blue-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-blue-200 font-medium mb-1">Objeto Identificado</div>
                  <div className="text-xl font-bold text-white">{impactData.asteroid.name}</div>
                </div>
                <div className="bg-orange-600/60 rounded-xl p-4 border-2 border-orange-400/40 hover:border-orange-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-orange-200 font-medium mb-1">Probabilidade de Impacto</div>
                  <div className="text-xl font-bold text-white">{impactData.asteroid.probability}</div>
                </div>
                <div className="bg-yellow-600/60 rounded-xl p-4 border-2 border-yellow-400/40 hover:border-yellow-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-yellow-200 font-medium mb-1">Energia Liberada</div>
                  <div className="text-xl font-bold text-white">{impactData.asteroid.energy}</div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="bg-red-600/60 rounded-xl p-4 border-2 border-red-400/40 hover:border-red-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-red-200 font-medium mb-1">Data/Hora do Impacto</div>
                  <div className="text-lg font-bold text-white">{impactData.asteroid.impactTime}</div>
                </div>
                <div className="bg-blue-600/60 rounded-xl p-4 border-2 border-blue-400/40 hover:border-blue-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-blue-200 font-medium mb-1">Localização</div>
                  <div className="text-sm font-semibold text-white">{impactData.asteroid.location}</div>
                </div>
                <div className="bg-cyan-600/60 rounded-xl p-4 border-2 border-cyan-400/40 hover:border-cyan-300/60 transition-all duration-300 hover:scale-105 shadow-lg">
                  <div className="text-sm text-cyan-200 font-medium mb-1">Tsunami Esperado</div>
                  <div className="text-lg font-bold text-white">{impactData.tsunami.height} - {impactData.tsunami.arrivalTime}</div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-red-600/60 to-orange-600/60 rounded-xl p-6 border-2 border-red-400/50 hover:border-red-300/70 transition-all duration-300 hover:scale-105 shadow-xl">
                  <div className="text-lg font-bold text-red-200 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    DECISÃO RECOMENDADA
                  </div>
                  <div className="text-sm text-gray-100 leading-relaxed">
                    Evacuação total de áreas costeiras num raio de 50 km. 
                    Mobilização imediata de recursos nacionais e internacionais.
                    Ativação do protocolo de emergência nacional.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* KPIs Críticos Modernos */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Activity className="w-8 h-8 text-orange-400" />
            </div>
            <span className="bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
              INDICADORES CRÍTICOS
            </span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gradient-to-br from-red-600/70 to-pink-600/70 backdrop-blur-lg rounded-2xl border-2 border-red-400/50 p-6 shadow-2xl hover:shadow-red-500/25 transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-red-500/20 rounded-xl">
                  <Users className="w-8 h-8 text-red-400" />
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-red-300">{evacuationProgress}%</div>
                  <div className="text-sm text-red-200">EVACUADOS</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-300">Meta: 95%</div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-red-500 to-pink-500 transition-all duration-1000" style={{ width: `${evacuationProgress}%` }}></div>
                </div>
                <div className="text-xs text-gray-400">487.320 pessoas evacuadas</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-orange-600/70 to-yellow-600/70 backdrop-blur-lg rounded-2xl border-2 border-orange-400/50 p-6 shadow-2xl hover:shadow-orange-500/25 transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-500/20 rounded-xl">
                  <Home className="w-8 h-8 text-orange-400" />
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-orange-300">287</div>
                  <div className="text-sm text-orange-200">ABRIGOS</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-300">Meta: 685</div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-orange-500 to-yellow-500 transition-all duration-1000" style={{ width: '42%' }}></div>
                </div>
                <div className="text-xs text-gray-400">94.300 vagas disponíveis</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-600/70 to-cyan-600/70 backdrop-blur-lg rounded-2xl border-2 border-blue-400/50 p-6 shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-blue-500/20 rounded-xl">
                  <Heart className="w-8 h-8 text-blue-400" />
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-blue-300">41%</div>
                  <div className="text-sm text-blue-200">HOSPITAIS</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-300">Meta: 100%</div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-1000" style={{ width: '41%' }}></div>
                </div>
                <div className="text-xs text-gray-400">2.847 pacientes transferidos</div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-600/70 to-emerald-600/70 backdrop-blur-lg rounded-2xl border-2 border-green-400/50 p-6 shadow-2xl hover:shadow-green-500/25 transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-500/20 rounded-xl">
                  <Shield className="w-8 h-8 text-green-400" />
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-green-300">67%</div>
                  <div className="text-sm text-green-200">PROTEGIDO</div>
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-300">Meta: 100%</div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-1000" style={{ width: '67%' }}></div>
                </div>
                <div className="text-xs text-gray-400">Infraestrutura crítica</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Timeline de Ações Críticas Moderna */}
            <div className="bg-gradient-to-br from-blue-700/80 to-blue-800/80 backdrop-blur-lg rounded-2xl border-2 border-blue-400/50 p-8 shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Clock className="w-6 h-6 text-blue-400" />
              </div>
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                TIMELINE DE AÇÕES CRÍTICAS
              </span>
            </h3>
            <div className="space-y-4">
              {impactData.timeline.map((item, idx) => (
                <div key={idx} className={`flex items-center gap-4 p-4 rounded-xl border transition-all duration-300 hover:scale-105 ${
                  item.status === 'completed' ? 'bg-green-500/10 border-green-500/30' :
                  item.status === 'pending' ? 'bg-yellow-500/10 border-yellow-500/30' :
                  'bg-red-500/10 border-red-500/30'
                }`}>
                  <div className={`p-2 rounded-lg ${
                    item.status === 'completed' ? 'bg-green-500/20' :
                    item.status === 'pending' ? 'bg-yellow-500/20' :
                    'bg-red-500/20'
                  }`}>
                    {getStatusIcon(item.status)}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-lg">{item.time}</div>
                    <div className="text-sm text-gray-300">{item.action}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

            {/* Bairros Críticos Modernos */}
            <div className="bg-gradient-to-br from-red-700/80 to-red-800/80 backdrop-blur-lg rounded-2xl border-2 border-red-400/50 p-8 shadow-2xl hover:shadow-red-500/25 transition-all duration-300 hover:scale-105">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <MapPin className="w-6 h-6 text-red-400" />
              </div>
              <span className="bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                BAIRROS CRÍTICOS DE FORTALEZA
              </span>
            </h3>
            <div className="space-y-4">
              {impactData.tsunami.criticalNeighborhoods.map((neighborhood, idx) => (
                  <div key={idx} className={`bg-blue-600/60 rounded-xl p-4 border-2 transition-all duration-300 hover:scale-105 shadow-lg ${
                    neighborhood.risk === 'CRÍTICO' ? 'border-red-400/60 hover:border-red-300/80' :
                    neighborhood.risk === 'ALTO' ? 'border-orange-400/60 hover:border-orange-300/80' :
                    'border-yellow-400/60 hover:border-yellow-300/80'
                  }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-bold text-lg text-white">{neighborhood.name}</div>
                      <div className="text-sm text-gray-300">{(neighborhood.population / 1000).toFixed(0)}K pessoas</div>
                      <div className="text-xs text-gray-400">Rota: {neighborhood.evacuationRoute}</div>
                    </div>
                    <div className={`text-sm font-bold px-3 py-1 rounded-lg ${
                      neighborhood.risk === 'CRÍTICO' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                      neighborhood.risk === 'ALTO' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                      'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                    }`}>
                      {neighborhood.risk}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Infraestrutura Crítica Moderna */}
          <div className="bg-gradient-to-br from-slate-800/60 to-orange-900/40 backdrop-blur-lg rounded-2xl border border-orange-500/30 p-8 shadow-xl">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <Building className="w-6 h-6 text-orange-400" />
              </div>
              <span className="bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
                INFRAESTRUTURA CRÍTICA
              </span>
            </h3>
            <div className="space-y-4">
              {impactData.infrastructure.critical.map((infra, idx) => (
                <div key={idx} className="bg-slate-700/50 rounded-xl p-4 border border-orange-500/30 transition-all duration-300 hover:scale-105">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-bold text-lg text-orange-300">{infra.name}</div>
                      <div className="text-sm text-gray-300 mt-1">{infra.action}</div>
                    </div>
                    <div className="text-xs font-bold px-3 py-1 rounded-lg bg-red-500/20 text-red-400 border border-red-500/30">
                      {infra.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recursos Humanitários Modernos */}
          <div className="bg-gradient-to-br from-slate-800/60 to-green-900/40 backdrop-blur-lg rounded-2xl border border-green-500/30 p-8 shadow-xl">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Users className="w-6 h-6 text-green-400" />
              </div>
              <span className="bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                RECURSOS HUMANITÁRIOS
              </span>
            </h3>
            <div className="space-y-4">
              <div className="bg-slate-700/50 rounded-xl p-4 border border-green-500/30">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-green-300">Abrigos Disponíveis</span>
                  <span className="text-xl font-bold text-green-400">{impactData.resources.shelters.available}</span>
                </div>
                <div className="text-xs text-gray-300 mb-2">
                  Capacidade: {(impactData.resources.shelters.capacity / 1000).toFixed(0)}K vagas
                </div>
                <div className="text-xs text-red-400">
                  Déficit: {(impactData.resources.shelters.deficit / 1000).toFixed(0)}K vagas
                </div>
              </div>

              <div className="bg-slate-700/50 rounded-xl p-4 border border-blue-500/30">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-blue-300">Água Potável</span>
                  <span className="text-xl font-bold text-blue-400">{impactData.resources.water.available}%</span>
                </div>
                <div className="text-xs text-gray-300">
                  Necessário: {(impactData.resources.water.daily / 1000000).toFixed(1)}M L/dia
                </div>
              </div>

              <div className="bg-slate-700/50 rounded-xl p-4 border border-red-500/30">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-red-300">Pacientes Hospitalares</span>
                  <span className="text-xl font-bold text-red-400">{impactData.resources.medical.patients}</span>
                </div>
                <div className="text-xs text-gray-300">
                  Leitos disponíveis: {impactData.resources.medical.beds}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Rotas Rodoviárias Modernas */}
        <div className="mt-12">
          <div className="bg-gradient-to-br from-slate-800/60 to-blue-900/40 backdrop-blur-lg rounded-2xl border border-blue-500/30 p-8 shadow-xl">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Map className="w-8 h-8 text-blue-400" />
              </div>
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                ROTAS RODOVIÁRIAS DE EVACUAÇÃO
              </span>
            </h2>
            
            {/* Rotas Primárias */}
            <div className="mb-8">
              <h3 className="text-2xl font-bold mb-6 text-blue-300 flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Car className="w-6 h-6" />
                </div>
                ROTAS PRIMÁRIAS
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {impactData.roadRoutes.primary.map((route, idx) => (
                  <div key={idx} className={`bg-slate-700/50 rounded-xl p-6 border transition-all duration-300 hover:scale-105 ${
                    route.status === 'BLOQUEADA' ? 'border-red-500/50' : 'border-blue-500/50'
                  }`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="font-bold text-lg text-blue-300">{route.name}</div>
                        <div className="text-sm text-gray-300 mt-1">{route.distance} • {route.time}</div>
                        {route.reason && (
                          <div className="text-xs text-red-400 mt-2 bg-red-500/10 px-2 py-1 rounded">{route.reason}</div>
                        )}
                      </div>
                      <div className={`text-sm font-bold px-3 py-1 rounded-lg ${
                        route.status === 'BLOQUEADA' ? 'text-red-400 bg-red-500/20 border border-red-500/30' : 'text-green-400 bg-green-500/20 border border-green-500/30'
                      }`}>
                        {route.status}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-slate-600/50 rounded-lg p-2">
                        <span className="text-gray-400 text-xs">Capacidade:</span>
                        <div className="text-white font-semibold">{(route.capacity / 1000).toFixed(0)}K</div>
                      </div>
                      <div className="bg-slate-600/50 rounded-lg p-2">
                        <span className="text-gray-400 text-xs">Congestionamento:</span>
                        <div className={`font-semibold ${
                          route.congestion === 'BAIXO' ? 'text-green-400' :
                          route.congestion === 'MÉDIO' ? 'text-yellow-400' : 'text-red-400'
                        }`}>{route.congestion}</div>
                      </div>
                      <div className="bg-slate-600/50 rounded-lg p-2">
                        <span className="text-gray-400 text-xs">Combustível:</span>
                        <div className="text-green-400 font-semibold">{route.fuel}</div>
                      </div>
                      <div className="bg-slate-600/50 rounded-lg p-2">
                        <span className="text-gray-400 text-xs">Prioridade:</span>
                        <div className={`font-semibold ${
                          route.priority === 'ALTA' ? 'text-red-400' :
                          route.priority === 'MÉDIA' ? 'text-yellow-400' : 'text-gray-400'
                        }`}>{route.priority}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Ações Prioritárias */}
        <div className="mt-12">
          <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 backdrop-blur-lg rounded-2xl border border-red-500/30 p-8 shadow-xl">
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <span className="bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                TOP 5 AÇÕES CRÍTICAS (Próximas 72 horas)
              </span>
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-red-500/10 rounded-xl p-6 border border-red-500/30 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl font-bold text-red-400">1️⃣</span>
                  <span className="font-bold text-lg text-red-300">EVACUAÇÃO COSTEIRA</span>
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  Remover 1.612.000 pessoas da Zona 2-3
                </div>
                <div className="text-xs text-gray-400">
                  Prazo: até 10:00 de 12/10
                </div>
              </div>

              <div className="bg-orange-500/10 rounded-xl p-6 border border-orange-500/30 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl font-bold text-orange-400">2️⃣</span>
                  <span className="font-bold text-lg text-orange-300">ESTADO DE EMERGÊNCIA</span>
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  Decreto até 18:00 de hoje
                </div>
                <div className="text-xs text-gray-400">
                  6 estados do Nordeste
                </div>
              </div>

              <div className="bg-yellow-500/10 rounded-xl p-6 border border-yellow-500/30 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl font-bold text-yellow-400">3️⃣</span>
                  <span className="font-bold text-lg text-yellow-300">PROTEÇÃO INFRAESTRUTURA</span>
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  Shutdown até 06:00 de 12/10
                </div>
                <div className="text-xs text-gray-400">
                  Usinas, hospitais, portos
                </div>
              </div>

              <div className="bg-blue-500/10 rounded-xl p-6 border border-blue-500/30 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl font-bold text-blue-400">4️⃣</span>
                  <span className="font-bold text-lg text-blue-300">ABRIGOS EMERGENCIAIS</span>
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  +1.000.000 vagas até 10/10
                </div>
                <div className="text-xs text-gray-400">
                  398 novos abrigos
                </div>
              </div>

              <div className="bg-green-500/10 rounded-xl p-6 border border-green-500/30 hover:scale-105 transition-all duration-300">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl font-bold text-green-400">5️⃣</span>
                  <span className="font-bold text-lg text-green-300">COMUNICAÇÃO PÚBLICA</span>
                </div>
                <div className="text-sm text-gray-300 mb-2">
                  Campanha contínua
                </div>
                <div className="text-xs text-gray-400">
                  TV, rádio, redes sociais
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Contatos de Emergência */}
        <div className="mt-12">
          <div className="bg-gradient-to-br from-slate-800/60 to-blue-900/40 backdrop-blur-lg rounded-2xl border border-blue-500/30 p-8 shadow-xl">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Phone className="w-6 h-6 text-blue-400" />
              </div>
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                CONTATOS DE EMERGÊNCIA
              </span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">Defesa Civil Nacional</div>
                  <div className="text-lg font-bold text-white">0800-123-4567</div>
                </div>
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">Email</div>
                  <div className="text-sm text-white">defesacivil.emergencia@gov.br</div>
                </div>
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">App</div>
                  <div className="text-sm text-white">EVACUAÇÃO BR</div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">Sirenes Costeiras</div>
                  <div className="text-lg font-bold text-white">68 unidades ativas</div>
                </div>
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">SMS em Massa</div>
                  <div className="text-lg font-bold text-white">2.1M celulares</div>
                </div>
                <div className="bg-slate-700/50 rounded-xl p-4">
                  <div className="text-sm font-semibold text-blue-300 mb-1">Última Atualização</div>
                  <div className="text-sm text-white">{currentTime.toLocaleString('pt-BR')}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernmentDashboard;