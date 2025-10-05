import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import AsteroidDashboard from './components/AsteroidDashboard';
import GovernmentDashboard from './components/GovernmentDashboard';

// Função para determinar qual dashboard mostrar
const App = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const dashboardType = urlParams.get('dashboard') || 'simulation';
  
  if (dashboardType === 'government') {
    return <GovernmentDashboard />;
  }
  
  return <AsteroidDashboard />;
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
