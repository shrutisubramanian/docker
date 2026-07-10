import React from 'react';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import ChaosSuite from './pages/ChaosSuite';
import HealingPipeline from './pages/HealingPipeline';
import History from './pages/History';
import { SimulationProvider, useSimulation } from './context/SimulationContext';

function AppContent() {
  const { activeTab, setActiveTab } = useSimulation();

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'chaos':
        return <ChaosSuite />;
      case 'healing':
        return <HealingPipeline />;
      case 'history':
        return <History />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} setTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}

function App() {
  return (
    <SimulationProvider>
      <AppContent />
    </SimulationProvider>
  );
}

export default App;
