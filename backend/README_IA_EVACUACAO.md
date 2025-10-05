# 🧭 IA para Evacuação Sem Congestionamento

Sistema integrado de Inteligência Artificial para evacuação inteligente que evita congestionamentos e otimiza rotas em tempo real.

## 🎯 Visão Geral

O sistema implementa três componentes principais de IA:

- **🧭 Routing AI**: Calcula rotas de evacuação seguras usando dados geográficos e simulações
- **🌍 Predictive AI**: Estima risco populacional combinando dados da NASA, USGS e WorldPop  
- **🚦 Decision AI**: Sugere melhor estratégia de mitigação baseada em energia, tempo e localização

## 🏗️ Arquitetura

### Componentes Principais

1. **Traffic AI Service** (`services/traffic_ai_service.py`)
   - Grafo viário com capacidade dinâmica usando OSMnx
   - Função BPR (Bureau of Public Roads) para modelagem de congestionamento
   - Assignment iterativo Frank-Wolfe para distribuição de tráfego
   - Modelo ML para previsão de tempo de viagem

2. **Traffic Assignment** (`services/traffic_assignment.py`)
   - Controlador RL (Deep Q-Network) para semáforos
   - Sistema de coordenação multi-intersecção
   - Otimização de offset entre semáforos

3. **Realtime WebSocket** (`services/realtime_websocket.py`)
   - Atualizações em tempo real via WebSocket
   - Sistema de inscrições por tipo de mensagem
   - Telemetria e alertas críticos

4. **Serviço Integrado** (`services/integrated_evacuation_service.py`)
   - Orquestra todos os componentes
   - Pipeline completo de análise de evacuação
   - Gerenciamento de cenários em tempo real

## 🚀 APIs Principais

### Análise Integrada de Evacuação

```http
POST /api/v1/evacuation-ai/analyze
```

**Endpoint principal** que combina todos os componentes de IA para gerar um plano de evacuação completo.

**Request:**
```json
{
  "impact_latitude": -23.5505,
  "impact_longitude": -46.6333,
  "asteroid_diameter_m": 500,
  "asteroid_velocity_kms": 20,
  "impact_angle_deg": 45,
  "terrain_type": "rock",
  "wind_speed_ms": 10,
  "wind_direction_deg": 0,
  "evacuation_radius_km": 25,
  "population_areas": [
    {
      "id": "area_001",
      "name": "Centro",
      "population": 50000,
      "latitude": -23.5505,
      "longitude": -46.6333,
      "priority": 1
    }
  ],
  "evacuation_points": [
    {
      "id": "shelter_001",
      "name": "Abrigo Central",
      "type": "shelter",
      "capacity": 5000,
      "latitude": -23.6005,
      "longitude": -46.6833
    }
  ],
  "enable_ml_predictions": true,
  "enable_rl_control": true,
  "enable_realtime_updates": true
}
```

**Response:**
```json
{
  "success": true,
  "scenario_id": "evac_1703123456",
  "execution_time_seconds": 45.2,
  "impact_simulation": {
    "energy_megatons": 125.5,
    "crater_diameter_km": 8.2,
    "is_airburst": false,
    "tsunami_generated": true
  },
  "traffic_analysis": {
    "network_stats": {
      "nodes": 1247,
      "edges": 2891
    },
    "demand_stats": {
      "total_demand": 45000
    },
    "assignment_results": {
      "iterations": 23,
      "converged": true,
      "bottlenecks": 3
    }
  },
  "evacuation_routes": {
    "total_od_pairs": 16,
    "routes_per_pair": 3
  },
  "recommendations": {
    "evacuation_strategy": "Rotas distribuídas para evitar congestionamento",
    "staggering_recommended": true,
    "estimated_evacuation_time": "2.5 horas"
  }
}
```

### APIs de Componentes Individuais

#### IA de Tráfego
```http
# Carregar rede viária
GET /api/v1/traffic-ai/network/load?center_latitude=-23.5505&center_longitude=-46.6333&radius_km=15

# Definir matriz de demanda
POST /api/v1/traffic-ai/demand

# Executar assignment
POST /api/v1/traffic-ai/assign

# Predição ML
POST /api/v1/traffic-ai/ml/predict

# Status do sistema
GET /api/v1/traffic-ai/status
```

#### WebSocket em Tempo Real
```http
# Conectar ao WebSocket
ws://localhost:8000/api/v1/ws/traffic?client_id=my_client

# Tipos de mensagem:
# - traffic_updates: Dados gerais de tráfego
# - evacuation_status: Status da evacuação  
# - route_updates: Atualizações de rotas
# - incidents: Alertas de incidentes
# - bottlenecks: Avisos de gargalos
```

## 🧠 Algoritmos de IA

### 1. Routing AI - Otimização de Rotas

**Função BPR (Bureau of Public Roads):**
```
t = t0 * (1 + α(v/c)^β)
```
- `t`: Tempo de viagem
- `t0`: Tempo livre de fluxo
- `v`: Fluxo atual (veículos/hora)
- `c`: Capacidade da via
- `α = 0.15, β = 4`: Parâmetros padrão

**Assignment Frank-Wolfe:**
1. Calcular menor caminho com custos livres
2. Acumular fluxo nas arestas
3. Atualizar custos com BPR
4. Recalcular caminhos
5. Line search para step size ótimo
6. Repetir até convergência

### 2. Predictive AI - Machine Learning

**Modelo Gradient Boosting:**
- **Features**: hora, chuva, visibilidade, vento, inclinação, superfície, faixas
- **Target**: Tempo de viagem em segundos
- **Performance**: < 100ms por predição

**Dataset Sintético:**
- 10.000 amostras geradas
- Variações meteorológicas e de tráfego
- Validação cruzada 80/20

### 3. Decision AI - Reinforcement Learning

**Deep Q-Network (DQN):**
- **Estado**: Filas, fluxos, tempos de espera, hora, clima
- **Ação**: Fase do semáforo (0-3)
- **Recompensa**: -(atraso + overflow)
- **Rede**: 3 camadas ocultas (128 neurônios)

**Coordenção Multi-Interseção:**
- Sistema de offset sincronizado
- Minimização de tempo médio e pico
- Adaptação a condições em tempo real

## 📊 Métricas de Performance

| Componente | Métrica | Valor |
|------------|---------|-------|
| Rede Viária | Carregamento | < 30s (área 20km) |
| Assignment | Convergência | < 50 iterações |
| ML | Predição | < 100ms |
| RL | Decisão | < 50ms |
| WebSocket | Latência | < 50ms |
| Tempo Real | Intervalo | 5s |

## 🔧 Instalação e Configuração

### Dependências
```bash
pip install -r requirements.txt
```

### Dependências Principais
- `osmnx`: Rede viária OpenStreetMap
- `networkx`: Algoritmos de grafos
- `torch`: Deep Learning (RL)
- `scikit-learn`: Machine Learning
- `websockets`: Comunicação tempo real

### Executar Servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testar Sistema
```bash
python examples/evacuation_ai_example.py
```

## 🌐 WebSocket - Tempo Real

### Conectar
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/traffic?client_id=my_client');

ws.onopen = function() {
    // Inscrever em atualizações
    ws.send(JSON.stringify({
        type: 'subscribe',
        data: { subscription_type: 'traffic_updates' }
    }));
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Mensagem:', message.message_type, message.data);
};
```

### Tipos de Mensagem

1. **traffic_updates**: Dados gerais de tráfego
2. **evacuation_status**: Progresso da evacuação
3. **route_updates**: Mudanças de rotas
4. **incident_alert**: Alertas de incidentes
5. **bottleneck_warning**: Avisos de gargalos
6. **system_status**: Status do sistema

## 📈 Exemplo de Uso Completo

```python
import requests

# 1. Executar análise completa
response = requests.post('http://localhost:8000/api/v1/evacuation-ai/analyze', json={
    "impact_latitude": -23.5505,
    "impact_longitude": -46.6333,
    "asteroid_diameter_m": 500,
    "asteroid_velocity_kms": 20,
    "evacuation_radius_km": 25,
    "population_areas": [...],
    "evacuation_points": [...]
})

scenario_id = response.json()['scenario_id']

# 2. Verificar status
status = requests.get(f'http://localhost:8000/api/v1/evacuation-ai/scenario/{scenario_id}/status')

# 3. Atualizar cenário em tempo real
requests.post('http://localhost:8000/api/v1/evacuation-ai/update-scenario', json={
    "scenario_id": scenario_id,
    "weather_update": {"hour": 18, "rainfall": 5, "visibility": 4},
    "traffic_incidents": [{"type": "accident", "severity": "medium"}]
})
```

## 🎯 Diferenciais Técnicos

1. **Grafo Viário Real**: Usa OSMnx para carregar rede viária real
2. **BPR Dinâmico**: Modela congestionamento com função BPR
3. **Assignment Iterativo**: Frank-Wolfe para distribuição ótima
4. **ML Meteorológico**: Predição baseada em condições reais
5. **RL Multi-Agente**: Coordenação inteligente de semáforos
6. **Tempo Real**: WebSocket para atualizações instantâneas
7. **Evitação de Risco**: Penaliza arestas em zonas de risco
8. **K-Rotas**: Múltiplas alternativas por par OD

## 🔮 Roadmap

### Fase 1 ✅ (Implementado)
- [x] Grafo viário com OSMnx
- [x] Função BPR para congestionamento
- [x] Assignment Frank-Wolfe
- [x] Modelo ML para predição
- [x] Controlador RL básico
- [x] WebSocket em tempo real

### Fase 2 🚧 (Planejado)
- [ ] Microsimulação de tráfego
- [ ] RL multi-agente avançado
- [ ] Integração com dados históricos
- [ ] Otimização de abrigos
- [ ] Análise de vulnerabilidade

### Fase 3 🔮 (Futuro)
- [ ] IA generativa para cenários
- [ ] Simulação de multidões
- [ ] Integração com IoT
- [ ] Blockchain para coordenação
- [ ] Realidade aumentada

## 📞 Suporte

Para dúvidas técnicas ou sugestões, consulte:
- Documentação da API: `http://localhost:8000/docs`
- Exemplos: `examples/evacuation_ai_example.py`
- Logs: Verifique console do servidor

---

**🧭 Cosmos Sentinel - IA para Evacuação Inteligente**  
*Evitando congestionamentos, salvando vidas.*
