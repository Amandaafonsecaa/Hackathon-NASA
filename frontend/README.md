# 🚀 IMPACTOR-2025 - NASA Space Apps Challenge

Um dashboard interativo para simulação de impacto de asteroides desenvolvido para o NASA Space Apps Challenge.

## 🌟 Características

- **Simulação Realística**: Cálculos baseados em física de impacto real
- **Mapas Interativos**: Visualização global e local com Leaflet
- **Métricas Avançadas**: 
  - Energia do impacto (Megatons TNT)
  - Magnitude sísmica
  - Tamanho da cratera
  - Bola de fogo e zona de destruição
  - Ondas de choque e ventos de pico
  - Tempo de evacuação necessário
  - Área afetada e vítimas estimadas

- **Estratégias de Mitigação**:
  - Impactador Cinético
  - Dispositivo Nuclear
  - Trator Gravitacional

- **Sistema de Evacuação**: 
  - Pontos de encontro regionais
  - Rotas de evacuação
  - Hospitais prioritários
  - Porto do Mucuripe para evacuação marítima

## 🛠️ Tecnologias Utilizadas

- **React 18** - Framework principal
- **Tailwind CSS** - Estilização
- **Leaflet** - Mapas interativos
- **Lucide React** - Ícones
- **Framer Motion** - Animações

## 🚀 Como Executar

1. **Instalar dependências**:
```bash
npm install
```

2. **Executar o projeto**:
```bash
npm start
```

3. **Acessar no navegador**:
```
http://localhost:3000
```

## 📊 Funcionalidades

### Painel de Controle
- Ajuste do diâmetro do asteroide (10m - 500m)
- Velocidade de impacto (10 - 50 km/s)
- Ângulo de impacto (15° - 90°)
- Coordenadas de impacto (lat/lng)
- Tempo até impacto (1h - 7 dias)
- População em risco (100K - 10M)

### Simulação de Impacto
- Cálculos baseados em física real
- Fórmulas de energia cinética
- Efeitos do ângulo de impacto
- Estimativas de destruição

### Mapas Interativos
- **Mapa Global**: Zona de impacto mundial
- **Mapa Local**: Sistema de evacuação de Fortaleza
- Marcadores animados
- Zonas de destruição e tsunami
- Rotas de evacuação

### Métricas em Tempo Real
- Energia do impacto
- Magnitude sísmica
- Tamanho da cratera
- Status de deflexão
- Bola de fogo
- Ondas de choque
- Ventos de pico
- Tempo de evacuação
- Área afetada
- Vítimas estimadas

## 🎯 Objetivo

Este projeto foi desenvolvido para o NASA Space Apps Challenge com o objetivo de criar uma ferramenta educativa e informativa sobre os riscos de impacto de asteroides e estratégias de mitigação.

## 📱 Responsivo

O dashboard é totalmente responsivo e funciona em:
- Desktop
- Tablet
- Mobile

## 🔧 Estrutura do Projeto

```
src/
├── components/
│   └── AsteroidDashboard.js    # Componente principal
├── index.js                     # Ponto de entrada
└── index.css                    # Estilos globais
```

## 🌍 Localização

O projeto está configurado para simular impactos na região de Fortaleza, Ceará, Brasil, incluindo:
- Coordenadas específicas da cidade
- Sistema de evacuação regional
- Porto do Mucuripe para evacuação marítima
- Hospitais e pontos de encontro

## 📈 Próximas Melhorias

- [ ] Integração com APIs da NASA
- [ ] Dados de asteroides reais
- [ ] Simulação 3D
- [ ] Alertas em tempo real
- [ ] Histórico de simulações
- [ ] Exportação de relatórios

## 🤝 Contribuição

Este projeto foi desenvolvido para o NASA Space Apps Challenge. Contribuições são bem-vindas!

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

**Desenvolvido com ❤️ para o NASA Space Apps Challenge 2025**
