import React from 'react';
import { Car, Plane, Ship, MapPin, Clock, Users, Route, AlertTriangle } from 'lucide-react';

const EvacuationRoutesVisualization = ({ evacuationData }) => {
  if (!evacuationData) return null;

  const { routes, points, metrics } = evacuationData;

  return (
    <div className="space-y-6">
      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-white" />
            <div>
              <div className="text-xl font-bold">{metrics.population_at_risk.toLocaleString()}</div>
              <div className="text-xs text-red-200">Pessoas em Risco</div>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-orange-600 to-orange-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-white" />
            <div>
              <div className="text-xl font-bold">{metrics.evacuation_time_hours}h</div>
              <div className="text-xs text-orange-200">Tempo Total</div>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-white" />
            <div>
              <div className="text-xl font-bold">{metrics.total_capacity.toLocaleString()}</div>
              <div className="text-xs text-green-200">Capacidade Total</div>
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <Route className="w-6 h-6 text-white" />
            <div>
              <div className="text-xl font-bold">{metrics.evacuation_efficiency.toFixed(1)}%</div>
              <div className="text-xs text-blue-200">Eficiência</div>
            </div>
          </div>
        </div>
      </div>

      {/* Rotas por Modalidade */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Rotas Terrestres */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-blue-400">
            <Car className="w-5 h-5" />
            Rotas Terrestres
          </h3>
          
          {routes?.terrestrial_routes?.map((route, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4 mb-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{route.name}</h4>
                <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                  {route.status || 'ATIVA'}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.capacity?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.estimated_time}h</span>
                </div>
              </div>
              
              {route.description && (
                <p className="text-xs text-gray-400 mt-2">{route.description}</p>
              )}
            </div>
          ))}
        </div>

        {/* Rotas Aéreas */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-green-400">
            <Plane className="w-5 h-5" />
            Evacuação Aérea
          </h3>
          
          {routes?.air_routes?.map((route, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4 mb-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{route.name}</h4>
                <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                  {route.status || 'DISPONÍVEL'}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.capacity?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.estimated_time}h</span>
                </div>
              </div>
              
              {route.description && (
                <p className="text-xs text-gray-400 mt-2">{route.description}</p>
              )}
            </div>
          ))}
        </div>

        {/* Rotas Marítimas */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-purple-400">
            <Ship className="w-5 h-5" />
            Evacuação Marítima
          </h3>
          
          {routes?.maritime_routes?.map((route, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4 mb-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{route.name}</h4>
                <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded">
                  {route.status || 'OPERACIONAL'}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.capacity?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">{route.estimated_time}h</span>
                </div>
              </div>
              
              {route.description && (
                <p className="text-xs text-gray-400 mt-2">{route.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Pontos de Encontro */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-yellow-400">
          <MapPin className="w-5 h-5" />
          Pontos de Encontro e Abrigos
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {points?.meeting_points?.map((point, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{point.name}</h4>
                <span className={`text-xs px-2 py-1 rounded ${
                  point.status === 'OPERACIONAL' ? 'bg-green-600 text-white' :
                  point.status === 'LIMITADO' ? 'bg-yellow-600 text-white' :
                  'bg-red-600 text-white'
                }`}>
                  {point.status || 'OPERACIONAL'}
                </span>
              </div>
              
              <div className="space-y-1 text-sm">
                <div className="flex items-center gap-1">
                  <Users className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">Capacidade: {point.capacity?.toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-gray-400" />
                  <span className="text-gray-300">Distância: {point.distance_km}km</span>
                </div>
                {point.facilities && (
                  <div className="text-xs text-gray-400 mt-2">
                    <strong>Facilidades:</strong> {point.facilities.join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alertas e Recomendações */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-red-400">
          <AlertTriangle className="w-5 h-5" />
          Alertas e Recomendações
        </h3>
        
        <div className="space-y-3">
          {metrics.evacuation_efficiency < 60 && (
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-3">
              <div className="font-semibold text-red-300">⚠️ Capacidade Limitada</div>
              <p className="text-sm text-red-200 mt-1">
                A capacidade de evacuação é limitada. Considere ativar rotas alternativas ou 
                aumentar o tempo de evacuação.
              </p>
            </div>
          )}
          
          {metrics.evacuation_time_hours > 12 && (
            <div className="bg-yellow-900/50 border border-yellow-500 rounded-lg p-3">
              <div className="font-semibold text-yellow-300">⏰ Tempo Crítico</div>
              <p className="text-sm text-yellow-200 mt-1">
                O tempo de evacuação é superior a 12 horas. Priorize evacuação por via aérea 
                para áreas mais distantes.
              </p>
            </div>
          )}
          
          {metrics.evacuation_efficiency > 80 && (
            <div className="bg-green-900/50 border border-green-500 rounded-lg p-3">
              <div className="font-semibold text-green-300">✅ Plano Eficiente</div>
              <p className="text-sm text-green-200 mt-1">
                O plano de evacuação tem excelente capacidade. Mantenha as rotas operacionais 
                e monitore o fluxo de pessoas.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EvacuationRoutesVisualization;
