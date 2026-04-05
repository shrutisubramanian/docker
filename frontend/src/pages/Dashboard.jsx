import React, { useEffect, useState } from 'react';
import { 
  getContainers, 
  triggerPipeline 
} from '../api';
import { 
  Zap, 
  Cpu, 
  MemoryStick as Memory, 
  HardDrive, 
  Activity,
  ArrowUpRight,
  TrendingUp,
  Search,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Terminal as TerminalIcon,
  Database
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { useSimulation } from '../context/SimulationContext';
import Terminal from '../components/Terminal';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ChartCard = ({ title, data, color }) => {
  const { theme } = useSimulation();
  const isDark = theme === 'dark';

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: isDark ? '#121214' : '#ffffff',
        titleColor: color,
        bodyColor: isDark ? '#fff' : '#0f172a',
        borderColor: isDark ? '#1f1f22' : '#e2e8f0',
        borderWidth: 1,
      }
    },
    scales: {
      x: { display: false },
      y: { 
        display: false,
        beginAtZero: true,
      }
    }
  };

  const chartData = {
    labels: Array(data.length).fill(''),
    datasets: [
      {
        data: data,
        borderColor: color,
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 100);
          gradient.addColorStop(0, `${color}33`);
          gradient.addColorStop(1, `${color}00`);
          return gradient;
        },
      },
    ],
  };

  return (
    <div className="cyber-panel h-48 relative overflow-hidden group">
      <div className="scanline"></div>
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className="text-[11px] text-text-dim font-mono flex items-center gap-1 uppercase tracking-wider">
            <Activity size={12} className="text-neon" />
            {title}
          </span>
          <h3 className="text-xl font-bold font-mono text-text-main mt-1 italic tracking-tighter">TELEMETRY_STREAM</h3>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-neon text-xs font-bold flex items-center gap-1 bg-neon/10 px-2 py-0.5 rounded-sm">
            <TrendingUp size={12} />
            +4.2%
          </span>
          <span className="text-[11px] text-text-dim font-mono mt-1">REAL-TIME</span>
        </div>
      </div>
      <div className="h-24">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { 
    containers, 
    telemetryHistory, 
    startHealing, 
    setActiveTab, 
    addLog,
    logs
  } = useSimulation();

  const handleExportLogs = () => {
    const logText = logs.map(l => `[${l.time}] [${l.type.toUpperCase()}] ${l.text}`).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `synthetic_sentinel_logs_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    addLog('SYSTEM_LOGS_EXPORTED // ARCHIVE_GENERATED', 'success');
  };

  const handleFix = async (name) => {
    try {
      // Step 1: Immediate Redirect
      startHealing(name);
      
      // Step 2: Async Backend Load
      const response = await triggerPipeline(name);
      
      // Step 3: Update with Real Data
      startHealing(name, response.incidents?.[0]);
    } catch (error) {
      console.error('Error triggering fix:', error);
      addLog(`HEAL_FAILED // ${error.message}`, 'error');
    }
  };

  const cn = (...inputs) => inputs.filter(Boolean).join(' ');

  return (
    <div className="flex flex-col gap-8 transition-colors duration-300">
      <div className="flex justify-between items-center px-2">
        <div>
          <h2 className="text-3xl font-bold tracking-tighter text-text-main uppercase">Dashboard_Cmd_Root</h2>
          <p className="text-text-dim font-mono text-xs mt-1 uppercase tracking-wider italic opacity-70">
            Real-time heuristics engine active // T-minus 00:0{Math.floor(Math.random()*5)} to next sync
          </p>
        </div>
        <div className="flex gap-4">
           <button 
             onClick={handleExportLogs}
             className="px-5 py-2.5 bg-panel-bg border border-border-subtle text-text-main text-xs font-bold flex items-center gap-2 hover:border-neon/50 transition-colors uppercase tracking-widest"
           >
            EXPORT LOGS
           </button>
           <button 
             onClick={() => setActiveTab('chaos')}
             className="px-5 py-2.5 bg-neon text-black text-xs font-bold flex items-center gap-2 hover:bg-neon/80 transition-all uppercase tracking-widest shadow-neon active:scale-95"
           >
            INJECT CHAOS
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ChartCard 
          title="CPU_LOAD_TELEMETRY" 
          data={telemetryHistory.cpu.length > 0 ? telemetryHistory.cpu : [0]} 
          color="#00ff66" 
        />
        <ChartCard 
          title="RAM_MEMORY_HEAP" 
          data={telemetryHistory.memory.length > 0 ? telemetryHistory.memory : [0]} 
          color="#00e5ff" 
        />
      </div>

      <div className="cyber-panel">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
             <h3 className="font-bold uppercase tracking-widest text-sm text-text-dim">Active Container Inventory</h3>
             <div className="flex gap-2">
                <span className="flex items-center gap-1 text-[11px] text-neon bg-neon/5 px-2.5 py-0.5 rounded-full border border-neon/20 font-bold">
                   <div className="w-1.5 h-1.5 rounded-full bg-neon animate-pulse"></div>
                   HEALTHY
                </span>
                <span className="flex items-center gap-1 text-[11px] text-yellow-500 bg-yellow-500/5 px-2.5 py-0.5 rounded-full border border-yellow-500/20 font-bold">
                   <div className="w-1.5 h-1.5 rounded-full bg-yellow-500"></div>
                   SCALING
                </span>
                <span className="flex items-center gap-1 text-[11px] text-chaos bg-chaos/5 px-2.5 py-0.5 rounded-full border border-chaos/20 font-bold">
                   <div className="w-1.5 h-1.5 rounded-full bg-chaos animate-pulse"></div>
                   FAILING
                </span>
             </div>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" size={16} />
            <input 
              type="text" 
              placeholder="Filter assets..."
              className="pl-10 pr-4 py-2 bg-bg-primary border border-border-subtle rounded text-xs text-text-main focus:outline-none focus:border-neon/30 w-64 transition-all"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="text-text-dim uppercase border-b border-border-subtle bg-bg-primary/30">
                <th className="py-4 px-4 font-bold">Container_ID</th>
                <th className="py-4 px-4 font-bold">Image_Hash</th>
                <th className="py-4 px-4 font-bold">Status</th>
                <th className="py-4 px-4 font-bold">Health</th>
                <th className="py-4 px-4 font-bold">Resource_Footprint</th>
                <th className="py-4 px-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {containers.length === 0 ? (
                <tr>
                   <td colSpan="6" className="py-8 text-center text-text-dim italic uppercase">System_Scanning...</td>
                </tr>
              ) : containers.map((c) => (
                <tr key={c.name} className="group hover:bg-neon/5 transition-colors">
                  <td className="py-4 px-4">
                    <span className="text-neon font-bold">{c.name}</span>
                  </td>
                  <td className="py-4 px-4 text-text-dim opacity-60 uppercase">sha256:{c.name.split('').reverse().join('').substring(0, 8)}...</td>
                  <td className="py-4 px-4">
                    <span className="text-text-main font-bold bg-panel-bg border border-border-subtle px-2 py-0.5 rounded shadow-sm uppercase tracking-tighter">Running</span>
                  </td>
                  <td className="py-4 px-4">
                    {parseFloat(c.cpu) > 80 ? (
                      <span className="flex items-center gap-1.5 text-chaos font-bold uppercase tracking-tighter">
                        <AlertCircle size={14} /> Critical
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-neon font-bold uppercase tracking-tighter">
                        <CheckCircle2 size={14} /> Healthy
                      </span>
                    )}
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-3 w-48">
                      <div className="flex-1 h-1 bg-border-subtle rounded-full overflow-hidden">
                        <div 
                          className={cn(
                            "h-full rounded-full transition-all duration-1000",
                            parseFloat(c.cpu) > 80 ? "bg-chaos" : "bg-neon"
                          )}
                          style={{ width: c.cpu }}
                        ></div>
                      </div>
                      <span className="text-text-main font-bold min-w-[40px] text-right">{c.memory}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={() => handleFix(c.name)}
                        className="px-4 py-1.5 bg-neon/10 border border-neon/30 text-neon hover:bg-neon hover:text-black transition-all rounded-sm text-[10px] font-bold uppercase tracking-widest"
                      >
                        HEAL
                      </button>
                      <button className="p-1 text-text-dim hover:text-text-main transition-colors">
                        <ExternalLink size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 pt-4 border-t border-border-subtle flex justify-center">
            <span className="text-[11px] text-text-dim font-bold animate-pulse-slow uppercase tracking-[0.3em] font-mono">
              End Of Stream — View Extended Logs (14,204 More Entries)
            </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 pb-8">
        <div className="cyber-panel flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TerminalIcon size={18} className="text-neon" />
              <h3 className="font-bold tracking-widest text-sm uppercase text-text-dim">Live Sentry Logs</h3>
            </div>
            <div className="flex gap-1">
               <div className="w-2.5 h-2.5 rounded-full bg-chaos/40"></div>
               <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/40"></div>
               <div className="w-2.5 h-2.5 rounded-full bg-neon/40"></div>
            </div>
          </div>
          <Terminal limit={10} className="h-80 text-xs" />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
