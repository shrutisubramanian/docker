import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { getContainers, getIncidents } from '../api';

const SimulationContext = createContext();

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
};

export const SimulationProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [isSimulationMode, setIsSimulationMode] = useState(true);
  const [containers, setContainers] = useState([]);
  const [telemetryHistory, setTelemetryHistory] = useState({ cpu: [], memory: [] });
  const [activeHealingSession, setActiveHealingSession] = useState(null);
  const [isChaosActive, setIsChaosActive] = useState(false);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const lastIncidentCount = useRef(0);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const toggleSimulationMode = useCallback(() => {
    setIsSimulationMode(prev => !prev);
  }, []);

  const addLog = useCallback((text, type = 'info') => {
    setLogs((prev) => [
      { id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`, time: new Date().toLocaleTimeString(), text, type },
      ...prev.slice(0, 49)
    ]);
  }, []);

  // --- Real-time Telemetry Engine ---
  useEffect(() => {
    const pollContainers = async () => {
      try {
        const data = await getContainers();
        setContainers(data);

        // Calculate aggregate telemetry for charts
        if (data.length > 0) {
          const avgCpu = data.reduce((acc, c) => acc + parseFloat(c.cpu || 0), 0) / data.length;
          const avgMem = data.reduce((acc, c) => acc + parseFloat(c.memory.replace(/[A-Z]/g, '') || 0), 0) / data.length;
          
          setTelemetryHistory(prev => ({
            cpu: [...prev.cpu.slice(-19), avgCpu],
            memory: [...prev.memory.slice(-19), avgMem]
          }));
        }
      } catch (err) {
        console.error("Telemetry Sync Failed:", err);
      }
    };

    pollContainers();
    const interval = setInterval(pollContainers, 3000);
    return () => clearInterval(interval);
  }, []);

  // --- Incident Sync Engine ---
  useEffect(() => {
    const syncIncidents = async () => {
      try {
        const incidents = await getIncidents();
        if (incidents.length > lastIncidentCount.current) {
          // Process new incidents
          const newIncidents = incidents.slice(lastIncidentCount.current);
          newIncidents.forEach(inc => {
            addLog(`AI_ALERT // ${inc.container} // ${inc.error_type} // ${inc.resolution_status}`, 
              inc.resolution_status === 'Success' ? 'success' : 'error'
            );
          });
          lastIncidentCount.current = incidents.length;
        }
      } catch (err) {
        console.error("Incident Sync Failed:", err);
      }
    };

    syncIncidents();
    const interval = setInterval(syncIncidents, 5000);
    return () => clearInterval(interval);
  }, [addLog]);

  const triggerChaos = useCallback(() => {
    setIsChaosActive(true);
    addLog('CHAOS_INJECTION_DETECTED // SYSTEM_INTERFERENCE_MAX', 'error');
  }, [addLog]);

  const stopChaos = useCallback(() => {
    setIsChaosActive(false);
    addLog('SYSTEM_RECOVERY_COMPLETE // RETURNING_TO_NOMINAL_STANCE', 'success');
  }, [addLog]);

  const startHealing = useCallback((containerName, report = null) => {
    setActiveHealingSession({ 
      containerName, 
      report,
      status: report ? (report.resolution_status === 'Success' ? 'success' : 'failed') : 'pending' 
    });
    
    if (report) {
      addLog(`AI_REPORT_SYNCHRONIZED // TARGET: ${containerName} // STATUS: ${report.resolution_status}`, 
        report.resolution_status === 'Success' ? 'success' : 'error');
      
      // Inject raw logs to prove data-driven nature
      if (report.original_log) {
        addLog(`RAW_DIAGNOSTIC_TRACE_START // FROM: ${containerName}`, 'info');
        addLog(report.original_log, 'info');
        addLog(`RECOVERY_ACTION_IDENTIFIED // MATCH: ${report.suggested_fix}`, 'success');
      }
    } else {
      addLog(`INITIALIZING_HEALING_PIPELINE // TARGET: ${containerName}`, 'info');
    }
    setActiveTab('healing');
  }, [addLog]);

  return (
    <SimulationContext.Provider value={{
      containers,
      telemetryHistory,
      activeHealingSession,
      setActiveHealingSession,
      isChaosActive,
      triggerChaos,
      stopChaos,
      logs,
      setLogs,
      addLog,
      activeTab,
      setActiveTab,
      startHealing,
      theme,
      toggleTheme,
      isSimulationMode,
      toggleSimulationMode
    }}>
      {children}
    </SimulationContext.Provider>
  );
};
