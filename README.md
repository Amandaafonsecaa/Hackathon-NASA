# ☄️ Meteor Madness — NASA Space Apps Challenge 2025

> 🌍 **IA que analisa, prevê e guia pessoas para zonas seguras em caso de impacto meteórico.**  
> Dados reais da NASA transformados em ação e sobrevivência.

---

## 🛰️ Sobre o Projeto

**Meteor Madness** é uma plataforma interativa e educativa que **simula impactos de meteoros** e usa **Inteligência Artificial** para **traçar rotas seguras de evacuação**,  
emitir **alertas em tempo real** com base em **dados oficiais da NASA**, e **educar o público** sobre defesa planetária e desastres naturais.

> Quando o céu ameaça, nossa IA mostra o caminho para a segurança.

---

## 🎯 Objetivo

Transformar dados astronômicos e ambientais complexos em **decisões acessíveis e acionáveis**.  
O sistema ajuda:
- 👨‍👩‍👧 cidadãos a saberem **como agir em caso de emergência**;  
- 🧭 gestores públicos a **planejar evacuação** e **mitigação de riscos**;  
- 🧠 escolas e museus a **ensinar ciência de forma interativa**.

---

## 💡 Funcionalidades Principais

| Módulo | Descrição |
|--------|------------|
| 🪐 **Simulação Física de Impacto** | Cálculo de energia, cratera, calor, vento, choque e terremoto com base em dados físicos reais. |
| 🧠 **Decision AI** | IA que analisa energia, velocidade e tempo até o impacto e escolhe **a melhor estratégia de mitigação** (kinetic, nuclear ou gravity tractor). |
| 🗺️ **Routing AI** | IA que **analisa zonas de impacto e traça automaticamente as rotas de fuga mais seguras** até pontos de encontro fora da área de risco. |
| 🔔 **NASA Alert System** | Sistema de **notificações automáticas** que usa a **NASA NEO API** e outras fontes (USGS, WorldPop) para alertar regiões afetadas. |
| 📊 **Predictive AI** | Estima o **risco populacional, danos estruturais e custo ambiental** combinando dados da NASA, USGS e modelos físicos. |
| 🧭 **Mapa Interativo** | Mostra **zonas de impacto, zonas seguras e rotas de evacuação** em tempo real com visualização em 2D/3D. |

---

## 🧠 Tecnologias Utilizadas

### 🖥️ Backend
- 🧩 **Python + FastAPI**  
- 🧮 **NumPy / SciPy** – cálculos físicos de impacto  
- 🤖 **Scikit-learn** – módulo de *Decision AI*  
- 🗺️ **OSMnx + NetworkX** – módulo de *Routing AI* (rotas de evacuação)  
- 🔔 **NASA NEO API** – detecção de asteroides e alertas oficiais  

### 💻 Frontend
- ⚛️ **React + TypeScript**  
- 🌈 **TailwindCSS / D3.js / Mapbox GL** – interface e visualização de dados espaciais  
- 🧭 **Visualização interativa 2D/3D** das zonas de impacto e rotas seguras  

### 🌐 Dados e Fontes
- 🌍 **NASA NEO API** – dados de asteroides próximos à Terra  
- 🏔️ **USGS Geological & Seismic Data** – relevo, falhas e vulnerabilidade do solo  
- 👥 **WorldPop Population Density** – densidade populacional global para estimar riscos  

--- 

## 🧮 Base Científica

Os cálculos físicos seguem modelos **validados por estudos da NASA, ESA e USGS**.

| Fenômeno | Fórmula / Modelo | Fonte |
|-----------|------------------|--------|
| Cratera | Holsapple & Housen (2007), Melosh (1989) | NASA PDC |
| Fireball | \( F = \frac{E}{4πr^2} \) | Impact Effects Program |
| Shockwave | Kingery & Bulmash (1984) | US DoD TNT Scaling |
| Wind Blast | \( v = √(2ΔP/ρ) \) | Fluid Dynamics |
| Earthquake | \( M = \frac{2}{3} \log_{10}(E) - 3.2 \) | Gutenberg-Richter (1956) |

---

## 🔔 Sistema de Alertas

> “A IA monitora o céu — se um objeto perigoso for detectado, as regiões sob risco recebem aviso instantâneo.”

O módulo **NASA Alert System** atua como um radar inteligente de defesa planetária:

- 🔭 Conecta-se à **[NASA NEO API](https://api.nasa.gov/)** *(Near-Earth Objects Feed)*.  
- 📡 Verifica **probabilidade de impacto** e **proximidade com a Terra** em tempo real.  
- 🚨 Se o risco for **≥ 1%**, o sistema dispara automaticamente:
  - 📱 **Notificação de alerta** simulada (push ou e-mail);  
  - 🗺️ **Atualização dinâmica do mapa** com novas zonas de impacto e segurança;  
  - 🧭 **Geração imediata de rotas seguras** através da *Routing AI*.  

> Assim, o Meteor Madness transforma dados astronômicos em **resposta rápida e coordenada**.

## ⚙️ Arquitetura do Sistema

```plaintext
+--------------------------------------------------------------+
|                      METEOR MADNESS SYSTEM                   |
+--------------------------------------------------------------+
| 1. NASA NEO API + USGS Data (real-time inputs)               |
| 2. Simulação Física: energia, cratera, fogo, choque, etc.    |
| 3. IA Modules:                                               |
|      • Decision AI – seleciona estratégia de mitigação       |
|      • Routing AI – calcula rotas de fuga seguras            |
|      • Predictive AI – estima população afetada              |
| 4. Alert System – envia notificações automáticas             |
| 5. Frontend – mapa interativo com zonas de impacto e segurança|
+--------------------------------------------------------------+
```
