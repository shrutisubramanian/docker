import React, { useState, useEffect, useMemo } from 'react';
import { 
  Skull, 
  Zap, 
  Target, 
  Terminal as TerminalIcon, 
  ShieldAlert, 
  Activity, 
  Cpu, 
  MemoryStick as Memory, 
  WifiOff, 
  FileWarning, 
  Bomb,
  Trash2,
  Lock,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { 
  getContainers, 
  simulateFailure,
  triggerPipeline 
} from '../api';
import { useSimulation } from '../context/SimulationContext';
import Terminal from '../components/Terminal';
import { Line } from 'react-chartjs-2';

const cn = (...inputs) => inputs.filter(Boolean).join(' ');

const ChaosPopup = ({ isOpen, onClose, container, type, onHeal }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="cyber-panel max-w-md w-full relative overflow-hidden bg-bg-primary border-chaos/50 p-8 shadow-[0_0_50px_rgba(255,51,102,0.3)]">
        <div className="scanline-fast opacity-30"></div>
        <div className="flex flex-col items-center text-center gap-6">
          <div className="w-20 h-20 rounded-full bg-chaos/10 flex items-center justify-center text-chaos animate-pulse border border-chaos/30">
            <ShieldAlert size={40} />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-chaos tracking-tighter uppercase mb-2">System Anomaly Detected</h3>
            <p className="text-sm text-text-dim font-mono leading-relaxed italic">
              Sector: <span className="text-text-main font-bold">{container}</span><br />
              Vector: <span className="text-chaos font-bold uppercase">{type.replace('_', ' ')}</span>
            </p>
          </div>
          <div className="w-full h-[1px] bg-border-subtle"></div>
          <p className="text-xs text-text-main/80 font-mono italic">
            "Synthetic Sentinel has detected a critical drift from baseline parameters. 
            Automated healing systems are standing by for authorization."
          </p>
          <div className="flex gap-4 w-full">
            <button 
              onClick={onClose}
              className="flex-1 py-3 border border-border-subtle text-text-dim hover:text-text-main text-xs font-bold uppercase transition-all"
            >
              DISMISS
            </button>
            <button 
              onClick={onHeal}
              className="flex-2 py-3 bg-chaos text-white text-xs font-bold uppercase shadow-neon-red hover:bg-chaos/80 transition-all active:scale-95"
            >
              INITIALIZE_HEAL
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const AttackCard = ({ icon: Icon, title, description, type, isActive, onSelect }) => (
  <button 
    onClick={() => onSelect(type)}
    className={cn(
      "cyber-panel flex flex-col items-start p-6 text-left group gap-4 h-full",
      isActive && "border-[#ff3366] bg-[#ff3366]/5 shadow-[0_0_15px_rgba(255,51,102,0.1)]",
      !isActive && "hover:border-[#ff3366]/40"
    )}
  >
    <div className={cn(
      "w-12 h-12 rounded-lg flex items-center justify-center transition-all",
      isActive ? "bg-chaos text-white" : "bg-bg-primary text-text-dim group-hover:text-chaos"
    )}>
      <Icon size={24} />
    </div>
    <div>
      <h4 className="font-bold text-sm tracking-tight mb-1 group-hover:text-chaos transition-colors uppercase text-text-main">{title}</h4>
      <p className="text-xs text-text-dim font-mono leading-relaxed">{description}</p>
    </div>
    {isActive ? (
      <div className="mt-auto flex gap-2">
         <span className="text-[10px] font-bold text-chaos px-2.5 py-1 border border-chaos/30 rounded-sm bg-chaos/5">ARMED</span>
         <span className="text-[10px] font-bold text-text-dim px-2.5 py-1 border border-border-subtle rounded-sm bg-bg-primary">TARGET_LOCKED</span>
      </div>
    ) : (
      <div className="mt-auto">
        <span className="text-[10px] font-bold text-text-dim bg-bg-primary px-2.5 py-1 rounded-sm border border-border-subtle">UNARMED</span>
      </div>
    )}
  </button>
);

const ChaosSuite = () => {
  const { containers, triggerChaos, addLog, isChaosActive, logs: globalLogs, startHealing } = useSimulation();
  const [selectedContainer, setSelectedContainer] = useState(null);
  const [selectedAttack, setSelectedAttack] = useState(null);
  const [isInjecting, setIsInjecting] = useState(false);
  const [showPopup, setShowPopup] = useState(false);

  const handleHeal = async () => {
    if (!selectedContainer) return;
    try {
      setShowPopup(false);
      // Step 1: Immediate Redirect
      startHealing(selectedContainer); 
      
      // Step 2: Async Backend Load
      const response = await triggerPipeline(selectedContainer);
      
      // Step 3: Update with Real Data
      startHealing(selectedContainer, response.incidents?.[0]);
    } catch (error) {
      console.error('Heal trigger failed:', error);
      addLog(`RECOVERY_INIT_FAILED // ${error.message}`, 'error');
    }
  };

  const handleInject = async () => {
    if (!selectedContainer || !selectedAttack) return;
    setIsInjecting(true);
    addLog(`INITIALIZING_CHAOS_VECTOR // TARGET: ${selectedContainer} // TYPE: ${selectedAttack}`, 'info');
    
    try {
      await simulateFailure(selectedAttack, selectedContainer);
      triggerChaos();
      setShowPopup(true);
    } catch (error) {
      console.error('Injection failed:', error);
      addLog(`INJECTION_FAILED // ${error.message}`, 'error');
    } finally {
      setIsInjecting(false);
    }
  };

  const attacks = [
    { id: 'cpu_spike', title: 'Resource Drifts', description: 'Induce hardware-level saturation to test horizontal scaling and pod eviction thresholds.', icon: Cpu },
    { id: 'dependency', title: 'Connectivity Issues', description: 'Simulate distributed network instability to validate circuit breaker patterns.', icon: WifiOff },
    { id: 'crash', title: 'Integrity Failures', description: 'Hard-kills and process corruption to verify state recovery and replica consistency.', icon: Skull },
    { id: 'latency', title: 'Network Latency', description: 'Introduce packet jitter and artificial delay to test timeout resilience.', icon: Clock },
    { id: 'leak', title: 'Memory Exhaustion', description: 'Simulate heap saturation and GC pressure to test automated restarts.', icon: Memory },
    { id: 'permissions', title: 'Security Breach', description: 'Inject RBAC permission drift to verify automated access management.', icon: Lock },
    { id: 'build', title: 'Pipeline Errors', description: 'Inject corrupt artifacts to test CI/CD rollback mechanisms.', icon: FileWarning },
    { id: 'disk_full', title: 'Storage Failure', description: 'Simulate storage volume saturation to test log rotation logic.', icon: Bomb },
  ];

  // Derived metrics for the drift chart
  const driftData = useMemo(() => {
    const base = [10, 12, 15, 14, 18, 16, 20, 22, 18, 15, 12, 14];
    if (isChaosActive) {
      return base.map(v => v + Math.random() * 80);
    }
    return base;
  }, [isChaosActive]);

  const chartData = {
    labels: Array(driftData.length).fill(''),
    datasets: [{
      data: driftData,
      borderColor: isChaosActive ? '#ff3366' : '#00ff66',
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 0,
      fill: true,
      backgroundColor: isChaosActive ? 'rgba(255, 51, 102, 0.1)' : 'rgba(0, 255, 102, 0.05)',
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: isChaosActive ? 200 : 1000 },
    scales: { x: { display: false }, y: { display: false, min: 0, max: 100 } },
    plugins: { legend: { display: false } }
  };

  return (
    <div className="flex flex-col gap-8 h-full">
      <div className={cn(
        "flex justify-between items-start border-l-4 pl-6 py-2 transition-colors",
        isChaosActive ? "border-chaos" : "border-neon"
      )}>
        <div>
          <span className={cn("text-xs font-mono flex items-center gap-1.5", isChaosActive ? "text-chaos" : "text-neon")}>
             <ShieldAlert size={14} className={cn(isChaosActive && "animate-pulse")} />
             {isChaosActive ? "EMERGENCY_STATE: CLUSTER_INSTABILITY_INJECTED" : "SYSTEM_READY: CHAOS_ORCHESTRATOR_IDLE"}
          </span>
          <h2 className="text-3xl font-bold tracking-tighter mt-1 uppercase text-text-main">Chaos Engineering Suite</h2>
          <p className="text-gray-500 font-mono text-xs mt-1 max-w-2xl opacity-80 italic">
            {isChaosActive ? 
              "Protocol Sentinel is currently simulating high-frequency jitter across all ingress nodes. Auto-healing suppressed." :
              "Select a target container and failure vector to begin infrastructure resilience testing."
            }
          </p>
        </div>
        <div className="flex gap-4">
           <div className="cyber-panel p-3 w-56 h-24">
              <span className="text-[11px] text-text-dim font-bold uppercase block mb-2 tracking-widest">Metrics_Drift_Impact</span>
              <div className="h-10">
                <Line data={chartData} options={chartOptions} />
              </div>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8 flex-1">
        {/* Left: Selection */}
        <div className="col-span-4 flex flex-col gap-8">
           <div className="cyber-panel">
               <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xs font-bold font-mono tracking-widest text-text-dim uppercase">Target Selection</h3>
                  <span className="text-[11px] bg-bg-primary px-3 py-1 rounded text-text-dim uppercase border border-border-subtle font-bold">{selectedContainer ? "1 SELECTED" : "0 SELECTED"}</span>
               </div>
              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
                 {containers.map(c => (
                     <button 
                       key={c.name}
                       onClick={() => setSelectedContainer(c.name)}
                       className={cn(
                         "w-full flex items-center justify-between p-3 rounded bg-bg-primary/50 border border-transparent transition-all",
                         selectedContainer === c.name ? "border-chaos/40 bg-chaos/5" : "hover:bg-bg-primary"
                       )}
                     >
                        <div className="flex items-center gap-3">
                           <div className={cn(
                             "w-1.5 h-1.5 rounded-full transition-all",
                             selectedContainer === c.name ? "bg-chaos shadow-[0_0_8px_#ff3366]" : "bg-text-dim/30"
                           )}></div>
                            <div className="text-left">
                               <div className={cn("text-xs font-bold font-mono transition-colors", selectedContainer === c.name ? "text-text-main" : "text-text-dim")}>{c.name}</div>
                               <div className="text-[10px] text-text-dim/60 font-mono uppercase font-bold">NODE_0x{80 + Math.floor(Math.random()*19)} // PROD_MAIN</div>
                            </div>
                        </div>
                        <Target size={12} className={selectedContainer === c.name ? "text-chaos" : "text-text-dim/20"} />
                     </button>
                 ))}
              </div>
           </div>

            <div className="cyber-panel flex-1 flex flex-col gap-6">
               <div className="flex items-center gap-2">
                  <TerminalIcon size={18} className="text-chaos" />
                  <h3 className="text-xs font-bold font-mono tracking-widest text-text-dim uppercase">Shared Telemetry</h3>
               </div>
               <Terminal limit={10} className="flex-1 text-xs" title="CHAOS_STREAM_MONITOR" />
            </div>
        </div>

        {/* Right: Vectors */}
        <div className="col-span-8 flex flex-col gap-6">
           <div className="grid grid-cols-2 gap-6">
              {attacks.map(attack => (
                <AttackCard 
                  key={attack.id}
                  {...attack} 
                  isActive={selectedAttack === attack.id}
                  type={attack.id}
                  onSelect={setSelectedAttack}
                />
              ))}
           </div>

           <div className="cyber-panel flex-1 flex flex-col relative overflow-hidden group">
              <div className="scanline"></div>
               <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-2">
                     <Activity size={16} className="text-chaos" />
                     <h3 className="text-xs font-bold font-mono tracking-widest text-text-dim uppercase">Chaos Vector Log</h3>
                  </div>
                 <div className="flex items-center gap-6">
                    <button 
                      onClick={handleInject}
                      disabled={!selectedContainer || !selectedAttack || isInjecting}
                       className={cn(
                         "flex items-center gap-2 px-8 py-3 font-bold text-xs rounded transition-all active:scale-95 uppercase tracking-widest",
                         isInjecting ? "bg-bg-primary text-text-dim cursor-not-allowed" : 
                         (!selectedContainer || !selectedAttack) ? "bg-bg-primary text-text-dim/40 cursor-not-allowed border border-border-subtle" : 
                         "bg-chaos text-white shadow-neon-red border border-chaos/50"
                       )}
                     >
                        <Zap size={14} fill="currentColor" />
                        {isInjecting ? "INITIALIZING..." : "EXECUTE INJECTION"}
                     </button>
                 </div>
              </div>

               <div className="flex-1 overflow-y-auto">
                  <table className="w-full text-xs font-mono">
                     <thead>
                        <tr className="text-text-dim uppercase border-b border-border-subtle bg-bg-primary">
                           <th className="px-5 py-4 text-left font-bold">Timestamp</th>
                           <th className="px-5 py-4 text-left font-bold">Target_Hash</th>
                           <th className="px-5 py-4 text-left font-bold">Chaos Vector</th>
                           <th className="px-5 py-4 text-center font-bold">Severity</th>
                           <th className="px-5 py-4 text-right font-bold">Outcome</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-border-subtle">
                       {globalLogs.slice(0, 10).map((log, i) => (
                           <tr key={i} className="group hover:bg-bg-primary/50 transition-colors">
                              <td className="px-5 py-5 text-chaos font-bold">{log.time}</td>
                              <td className="px-5 py-5 text-text-main font-bold uppercase tracking-tighter">
                                 {log.text.split(' // ')[1] || "SYSTEM"}
                              </td>
                              <td className="px-5 py-5 text-text-dim italic text-xs">
                                 {log.text.split(' // ')[2] || log.text}
                              </td>
                              <td className="px-5 py-5 text-center">
                                 <div className="h-1.5 w-24 bg-border-subtle rounded-full overflow-hidden mx-auto">
                                    <div 
                                      className={cn(
                                        "h-full transition-all duration-1000", 
                                        log.type === 'error' ? "bg-chaos w-full" : 
                                        log.type === 'success' ? "bg-neon w-full" : "bg-yellow-500 w-3/4"
                                      )}
                                    ></div>
                                 </div>
                              </td>
                              <td className="px-5 py-5 text-right text-xs">
                                 <span className={cn(
                                    "px-2.5 py-1 rounded font-bold uppercase tracking-tighter",
                                    log.type === 'success' ? 'bg-neon/10 text-neon' : 
                                    log.type === 'error' ? 'bg-chaos/10 text-chaos' :
                                    'bg-yellow-500/10 text-yellow-500'
                                 )}>
                                    {log.type === 'success' ? 'STABLE' : log.type === 'error' ? 'INJECTED' : 'PROCESS'}
                                 </span>
                              </td>
                           </tr>
                       ))}
                    </tbody>
                  </table>
               </div>
           </div>
        </div>
      </div>

      <ChaosPopup 
        isOpen={showPopup}
        onClose={() => setShowPopup(false)}
        container={selectedContainer}
        type={selectedAttack}
        onHeal={handleHeal}
      />
    </div>
  );
};

export default ChaosSuite;
