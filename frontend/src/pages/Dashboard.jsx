import React, { useState, useEffect } from 'react';
import ContainerTable from '../components/ContainerTable';
import FailureControls from '../components/FailureControls';
import HealingTimeline from '../components/HealingTimeline';
import IncidentTable from '../components/IncidentTable';
import { getContainers, getIncidents, simulateFailure, triggerPipeline } from '../services/api';
import { Activity, Shield, RefreshCcw, AlertOctagon } from 'lucide-react';

const Dashboard = () => {
  const [containers, setContainers] = useState([]);
  const [selectedContainer, setSelectedContainer] = useState('');
  const [incidents, setIncidents] = useState([]);
  const [pipelineData, setPipelineData] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const [serverError, setServerError] = useState(null);

  const fetchData = async () => {
    try {
      const containersData = await getContainers();
      const incidentsData = await getIncidents();

      // Ensure we handle data structures correctly if they come back as objects
      setContainers(Array.isArray(containersData) ? containersData : containersData.containers || []);
      setIncidents(incidentsData);
      setServerError(null);
    } catch (error) {
      setServerError(error.message);
    } finally {
      setLoadingInitial(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Automatic selection of the first container if none is selected
  useEffect(() => {
    if (containers.length > 0 && !selectedContainer) {
      setSelectedContainer(containers[0].name);
    }
  }, [containers, selectedContainer]);

  const handleSimulateFailure = async (type) => {
    try {
      if (!selectedContainer) throw new Error("Please select a target container first.");
      setServerError(null);
      await simulateFailure(type, selectedContainer);
      await fetchData();
    } catch (error) {
      setServerError(error.message);
    }
  };

  const handleTriggerPipeline = async () => {
    setIsPipelineRunning(true);
    try {
      setServerError(null);
      if (!selectedContainer) throw new Error("Please select a target container first.");

      const result = await triggerPipeline(selectedContainer);
      setPipelineData(result);
    } catch (error) {
      setServerError(error.message);
    } finally {
      setIsPipelineRunning(false);
      await fetchData();
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg p-6 text-slate-200 font-sans selection:bg-indigo-500/30">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center justify-between mb-8 pb-4 border-b border-dark-border">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-500/30">
              <Shield className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-sm">Self-Healing Framework</h1>
              <p className="text-sm text-slate-400">AI-powered automated container recovery</p>
            </div>
          </div>

          <button
            onClick={fetchData}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-full transition-colors flex items-center justify-center space-x-2"
            title="Refresh Data"
          >
            <RefreshCcw className="w-5 h-5 flex-shrink-0" />
          </button>
        </header>

        {serverError && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-center space-x-3 text-rose-400">
            <AlertOctagon className="w-6 h-6 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-rose-300">Connection Error</h3>
              <p className="text-sm">{serverError}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="col-span-1 lg:col-span-2 flex flex-col gap-6">
            {/* Table now displays Disk and Network within its existing structure */}
            <ContainerTable
              containers={containers}
              loading={loadingInitial}
              onSelect={setSelectedContainer}
              selectedId={selectedContainer}
            />

            {/* Added 3 new attack types to FailureControls via handleSimulateFailure */}
            <FailureControls
              onSimulate={handleSimulateFailure}
              containers={containers}
              selectedContainer={selectedContainer}
              onSelectContainer={setSelectedContainer}
            />

            <IncidentTable incidents={incidents} loading={loadingInitial} />
          </div>

          <div className="col-span-1 flex flex-col gap-6">
            <div className="bg-dark-panel rounded-xl border border-dark-border p-6 shadow-lg relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              <h2 className="flex items-center space-x-2 text-xl font-semibold mb-4 text-slate-100 relative z-10">
                <Activity className="w-5 h-5 text-indigo-400" />
                <span>Healing Pipeline</span>
              </h2>
              <p className="text-slate-400 text-sm mb-6 relative z-10">
                Trigger the AI agent to analyze metrics, diagnose issues, and automatically restart unhealthy containers.
              </p>

              <button
                onClick={handleTriggerPipeline}
                disabled={isPipelineRunning || !!serverError}
                className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium tracking-wide shadow-lg shadow-indigo-500/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:active:scale-100 disabled:cursor-not-allowed flex justify-center items-center relative z-10"
              >
                {isPipelineRunning ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full mr-3"></div>
                    Running Pipeline...
                  </>
                ) : (
                  'Run Self-Healing Pipeline'
                )}
              </button>
            </div>

            <div className="flex-1">
              <HealingTimeline pipelineData={pipelineData} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;