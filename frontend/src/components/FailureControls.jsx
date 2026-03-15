import React, { useState } from 'react';
import { AlertTriangle, Zap, Skull, RefreshCw, Layers, WifiOff, HardDrive } from 'lucide-react';

const FailureControls = ({ onSimulate, containers = [], selectedContainer, onSelectContainer }) => {
  const [loading, setLoading] = useState(null);

  const handleSimulate = async (type) => {
    setLoading(type);
    await onSimulate(type);
    setLoading(null);
  };

  const buttons = [
    { id: 'cpu_spike', label: 'CPU Spike', icon: <Zap className="w-4 h-4" />, color: 'border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10' },
    { id: 'memory_spike', label: 'Memory Spike', icon: <AlertTriangle className="w-4 h-4" />, color: 'border-orange-500/30 text-orange-400 hover:bg-orange-500/10' },
    { id: 'crash', label: 'Container Crash', icon: <Skull className="w-4 h-4" />, color: 'border-red-500/30 text-red-400 hover:bg-red-500/10' },
    { id: 'fork_bomb', label: 'Fork Bomb', icon: <Layers className="w-4 h-4" />, color: 'border-purple-500/30 text-purple-400 hover:bg-purple-500/10' },
    { id: 'network_delay', label: 'Network Latency', icon: <WifiOff className="w-4 h-4" />, color: 'border-blue-500/30 text-blue-400 hover:bg-blue-500/10' },
    { id: 'disk_exhaust', label: 'Disk Filling', icon: <HardDrive className="w-4 h-4" />, color: 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10' },
  ];

  return (
    <div className="bg-dark-panel rounded-xl border border-dark-border p-6 shadow-lg mb-6">
      <div className="flex items-center space-x-2 mb-6">
        <AlertTriangle className="w-5 h-5 text-rose-400" />
        <h2 className="text-xl font-semibold text-slate-100 tracking-wide">Failure Simulation</h2>
      </div>

      <p className="text-slate-400 text-sm mb-6">
        Trigger simulated anomalies to test the AI Self-Healing pipeline.
      </p>

      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-400 mb-2">Target Container</label>
        <select
          value={selectedContainer || ''}
          onChange={(e) => onSelectContainer(e.target.value)}
          className="w-full bg-dark-bg border border-dark-border text-slate-200 rounded-lg px-4 py-3 hover:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
        >
          {containers.length === 0 ? (
            <option value="">Loading containers...</option>
          ) : (
            containers.map(c => (
              <option key={c.name} value={c.name}>{c.name} ({c.status})</option>
            ))
          )}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {buttons.map((btn) => (
          <button
            key={btn.id}
            onClick={() => handleSimulate(btn.id)}
            disabled={loading !== null}
            className={`flex items-center justify-center space-x-2 py-3 px-4 rounded-lg border transition-all duration-200 ${btn.color} ${loading !== null ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading === btn.id ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              btn.icon
            )}
            <span className="font-medium text-xs md:text-sm">{btn.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default FailureControls;