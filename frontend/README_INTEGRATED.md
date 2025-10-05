# 🚀 COSMOS SENTINEL - Frontend Integrado

Dashboard interativo para simulação de impacto de asteroides com integração completa ao backend Cosmos Sentinel.

## 🌟 Novas Funcionalidades Integradas

### ✅ **Integração Completa com Backend**
- **API Service Centralizado**: Serviço unificado para todas as chamadas ao backend
- **Cálculos Avançados**: Física de impacto precisa do backend vs. cálculos locais
- **Dados Reais da NASA**: Integração com APIs de asteroides reais
- **Zonas de Risco Dinâmicas**: GeoJSON gerado pelo backend
- **Rotas de Evacuação**: Cálculos otimizados de evacuação
- **Dados Ambientais**: Análise atmosférica e topográfica em tempo real
- **Imagens de Satélite**: Dados visuais atualizados
- **Relatórios Executivos**: Geração automática de relatórios

### 🔧 **APIs Integradas**

1. **`/api/v1/simular`** - Simulação física completa
2. **`/api/v1/neo`** - Dados reais de asteroides da NASA
3. **`/api/v1/geojson`** - Zonas de risco e evacuação
4. **`/api/v1/evacuacao`** - Rotas e pontos de evacuação
5. **`/api/v1/ambiental`** - Dados ambientais e atmosféricos
6. **`/api/v1/satelite`** - Imagens de satélite
7. **`/api/v1/relatorios`** - Relatórios executivos
8. **`/api/v1/earthdata`** - Acesso unificado NASA
9. **`/api/v1/defesa-civil`** - Coordenação de emergência
10. **`/api/v1/saude`** - Monitoramento de saúde

## 🚀 Como Executar

### 1. **Backend (Obrigatório)**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
O backend deve estar rodando em `http://localhost:8001`

### 2. **Frontend**
```bash
cd frontend
npm install
npm start
```

### 3. **Acessar**
```
http://localhost:3000
```

## 🎯 **Funcionalidades Principais**

### **Busca de Asteroides Reais**
- Digite o ID de um asteroide real (ex: 2000433, 99942)
- Dados carregados automaticamente da NASA
- Parâmetros de simulação atualizados com dados reais

### **Simulação Avançada**
- **Modo Backend**: Cálculos precisos com física avançada
- **Modo Local**: Fallback para cálculos JavaScript
- **Toggle**: Alternar entre modos em tempo real

### **Indicadores de Status**
- **Conexão Backend**: Status em tempo real
- **Carregamento**: Indicadores visuais durante processamento
- **Erros**: Mensagens claras de erro
- **Sucesso**: Confirmação de dados carregados

### **Dados Integrados**
- **Simulação**: Energia, cratera, terremoto, tsunami
- **Zonas de Risco**: Polígonos GeoJSON dinâmicos
- **Evacuação**: Rotas otimizadas e pontos de encontro
- **Ambiental**: Elevação, temperatura, qualidade do ar
- **Satélite**: Imagens em tempo real da região
- **Relatórios**: Documentos executivos automáticos

## 🔧 **Estrutura do Projeto**

```
frontend/
├── src/
│   ├── services/
│   │   └── apiService.js          # Serviço centralizado da API
│   ├── components/
│   │   ├── AsteroidDashboard.js  # Dashboard principal integrado
│   │   └── GovernmentDashboard.js # Dashboard governamental
│   ├── index.js                   # Ponto de entrada
│   └── index.css                  # Estilos globais
├── public/                         # Arquivos estáticos
├── build/                         # Build de produção
└── package.json                    # Dependências
```

## 🌐 **Configuração da API**

### **URL Base**
```javascript
const baseURL = 'http://localhost:8001/api/v1';
```

### **Timeout**
```javascript
const timeout = 30000; // 30 segundos
```

### **Headers Padrão**
```javascript
{
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}
```

## 📊 **Exemplo de Uso**

### **Buscar Asteroide Real**
```javascript
const result = await cosmosAPI.getEnhancedAsteroidData('2000433');
if (result.success) {
  console.log('Asteroide carregado:', result.data);
}
```

### **Executar Simulação**
```javascript
const simulationData = {
  diameter_m: 100,
  velocity_kms: 17,
  impact_angle_deg: 45,
  target_type: 'rocha'
};

const result = await cosmosAPI.simulateImpact(simulationData);
```

### **Gerar Zonas de Risco**
```javascript
const riskZones = await cosmosAPI.generateRiskZones(simulationData);
```

## 🎨 **Interface do Usuário**

### **Painel de Controle**
- Busca de asteroides reais da NASA
- Parâmetros de simulação ajustáveis
- Toggle entre modo backend/local
- Status de conexão em tempo real

### **Indicadores Visuais**
- 🟢 **Verde**: Conectado ao backend
- 🟡 **Amarelo**: Verificando conexão
- 🔴 **Vermelho**: Desconectado
- ⚪ **Cinza**: Processando

### **Feedback do Usuário**
- Mensagens de erro claras
- Indicadores de carregamento
- Confirmações de sucesso
- Status de dados carregados

## 🔄 **Fluxo de Integração**

1. **Inicialização**: Teste de conexão com backend
2. **Busca**: Dados de asteroides reais (opcional)
3. **Simulação**: Cálculos avançados do backend
4. **Zonas**: Geração de GeoJSON dinâmico
5. **Evacuação**: Rotas e pontos otimizados
6. **Ambiental**: Dados atmosféricos e topográficos
7. **Satélite**: Imagens em tempo real
8. **Relatórios**: Documentos executivos

## 🚨 **Tratamento de Erros**

- **Conexão**: Fallback para modo local
- **API**: Mensagens de erro específicas
- **Timeout**: Retry automático
- **Dados**: Validação de resposta

## 📈 **Próximas Melhorias**

- [ ] Cache de dados para performance
- [ ] Histórico de simulações
- [ ] Exportação de relatórios PDF
- [ ] Notificações em tempo real
- [ ] Modo offline com dados cached
- [ ] Integração com mais APIs da NASA

## 🤝 **Contribuição**

Este projeto integra frontend React com backend FastAPI para criar uma ferramenta completa de simulação de impacto de asteroides.

## 📄 **Licença**

Este projeto é open source e está disponível sob a licença MIT.

---

**Desenvolvido com ❤️ para o NASA Space Apps Challenge 2025**

**Integração Frontend-Backend Completa ✅**
