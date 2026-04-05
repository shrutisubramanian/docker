import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Brain, 
  CheckCircle2, 
  Search, 
  ShieldAlert, 
  TrendingDown,
  Wrench,
  RotateCcw
} from 'lucide-react';
import { useSimulation } from '../context/SimulationContext';
import Terminal from '../components/Terminal';

const cn = (...inputs) => inputs.filter(Boolean).join(' ');

const PipelineStep = ({ icon: Icon, title, time, children, status, isActive }) => (
  <div className={cn(
    "relative pl-12 pb-12 transition-all duration-500",
    isActive ? "opacity-100" : "opacity-30 blur-[1px]"
  )}>
    {/* Line */}
    <div className="absolute left-5 top-10 bottom-0 w-[2px] bg-border-subtle">
       {status === 'active' && <div className="h-full w-full bg-gradient-to-b from-neon to-transparent animate-pulse"></div>}
       {status === 'complete' && <div className="h-full w-full bg-neon shadow-[0_0_8px_#00ff66]"></div>}
    </div>
    
    {/* Icon Wrapper */}
    <div className={cn(
      "absolute left-0 top-0 w-10 h-10 rounded-lg flex items-center justify-center z-10 border transition-all duration-500",
      status === 'complete' ? "bg-neon/10 border-neon/50 text-neon" :
      status === 'active' ? "bg-neon border-neon text-black shadow-neon animate-pulse" :
      "bg-panel-bg border-border-subtle text-text-dim"
    )}>
      <Icon size={20} />
    </div>

    <div className="flex justify-between items-start mb-2">
      <h3 className={cn(
        "text-xl font-bold tracking-tight transition-colors",
        status === 'active' || status === 'complete' ? "text-text-main" : "text-text-dim"
      )}>{title}</h3>
      <span className="text-xs text-text-dim font-mono bg-bg-primary px-3 py-1 rounded border border-border-subtle uppercase font-bold tracking-widest">T + {time}S</span>
    </div>
    
    <div className="text-sm text-text-dim/80 font-mono leading-relaxed max-w-xl">
      {children}
    </div>

    {status === 'active' && (
      <div className="mt-4 h-1 w-64 bg-border-subtle rounded-full overflow-hidden">
        <div className="h-full bg-neon w-full origin-left animate-progress-fast"></div>
      </div>
    )}
  </div>
);

const HealingPipeline = () => {
  const { activeHealingSession, setActiveHealingSession, stopChaos, addLog } = useSimulation();
  const [currentStep, setCurrentStep] = useState(0);

  const report = activeHealingSession?.report;
  const targetName = activeHealingSession?.containerName;

  useEffect(() => {
    if (activeHealingSession) {
      setCurrentStep(0);
      const timers = [
        setTimeout(() => setCurrentStep(1), 600),
        setTimeout(() => setCurrentStep(2), 1800),
        setTimeout(() => setCurrentStep(3), 3500),
        setTimeout(() => setCurrentStep(4), 5000),
      ];
      return () => timers.forEach(clearTimeout);
    }
  }, [activeHealingSession]);

  const handleReset = () => {
    setActiveHealingSession(null);
    stopChaos();
    setCurrentStep(0);
    addLog('HEALING_PIPELINE_RESOLVED // RETURNING_TO_NOMINAL_STANCE', 'success');
  };

  return (
    <div className="flex flex-col gap-8 h-full">
      <div className="flex justify-between items-center border-b border-border-subtle pb-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tighter uppercase font-mono text-text-main text-neon drop-shadow-neon">Healing Pipeline</h2>
          <p className="text-text-dim font-mono text-xs mt-1 uppercase italic opacity-80 font-bold tracking-wider">
            {activeHealingSession ? 
              `AI-DRIVEN ANOMALY MITIGATION // TARGET_INSTANCE: [${targetName || "RECOVERING"}]` : 
              "IDLE_STANDBY // MONITORING_CLUSTER_HEALTH..."
            }
          </p>
        </div>
        <div className="flex gap-8">
           <div className="text-right">
              <span className="text-xs text-text-dim font-bold uppercase block mb-1 tracking-widest opacity-60">Engine_Precision</span>
              <span className="text-2xl font-bold font-mono text-neon">0.992</span>
           </div>
           <div className="text-right">
              <span className="text-xs text-text-dim font-bold uppercase block mb-1 tracking-widest opacity-60">Mitigation_Time</span>
              <span className="text-2xl font-bold font-mono text-text-main">1.2<span className="text-xs text-text-dim">s</span></span>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8 flex-1 overflow-hidden">
        {/* Left: Progression */}
        <div className="col-span-8 overflow-y-auto pr-4 custom-scrollbar">
           {!activeHealingSession ? (
             <div className="cyber-panel p-20 flex flex-col items-center justify-center text-center opacity-50 grayscale hover:grayscale-0 transition-all cursor-default group overflow-hidden">
                <div className="scanline opacity-10"></div>
                <div className="w-20 h-20 rounded-full border border-dashed border-border-subtle flex items-center justify-center mb-6 group-hover:border-neon/50 group-hover:animate-spin-slow transition-colors">
                   <Activity size={40} className="text-text-dim/60 group-hover:text-neon" />
                </div>
                <h3 className="text-xl font-bold font-mono text-text-dim/80 mb-2 uppercase tracking-widest">No Active Healing Session</h3>
                <p className="text-sm text-text-dim/60 font-mono max-w-xs leading-relaxed uppercase">
                  All system parameters are within nominal ranges. Sentinel is currently in passive surveillance mode.
                </p>
             </div>
           ) : (
             <div className="cyber-panel p-10 relative overflow-hidden">
                <div className="scanline"></div>
                
                <div className="mb-10 flex items-center justify-between border-b border-border-subtle/30 pb-4">
                   <div className="flex items-center gap-2">
                      <TrendingDown size={18} className="text-neon" />
                      <h3 className="font-bold tracking-widest text-xs uppercase font-mono text-text-main">Real-time Recovery Flow</h3>
                   </div>
                   <div className="px-4 py-1.5 bg-neon/10 text-neon text-[10px] font-bold rounded-sm border border-neon/20 uppercase tracking-[0.2em] font-mono shadow-[0_0_10px_rgba(0,255,102,0.1)]">
                      SESSION_ID: {activeHealingSession.report?.id || "UNREGISTERED"}
                   </div>
                </div>

                <div className="max-w-2xl mx-auto space-y-2">
                   <PipelineStep 
                     icon={Search} 
                     title="Structural Deviation Detected" 
                     time="0.005" 
                     status={currentStep >= 1 ? "complete" : "active"}
                     isActive={currentStep >= 0}
                   >
                     AI-Sentry identified a critical anomaly on container <span className="text-chaos font-bold uppercase">{targetName}</span>. 
                     Telemetry layer reporting initial vector: <span className="underline italic text-neon uppercase font-bold tracking-tighter">[{typeof report?.error_type === 'string' ? report.error_type : "DOCKER_FAULT"}]</span>.
                     <div className="mt-2 text-[10px] text-text-dim border-t border-border-subtle/30 pt-2 flex justify-between uppercase font-mono">
                        <span>Model_Identifier: Structural-SVM_v3.5</span>
                        <span>Trace_ID: {activeHealingSession.report?.id?.substring(0, 8) || "PENDING"}</span>
                      </div>
                   </PipelineStep>

                   <PipelineStep 
                     icon={Brain} 
                     title="Automated Neural Diagnosis" 
                     time="0.122" 
                     status={currentStep >= 2 ? "complete" : currentStep === 1 ? "active" : "pending"}
                     isActive={currentStep >= 1}
                   >
                      <div className="flex gap-2 mb-3 mt-1">
                         <span className="bg-chaos/10 text-chaos text-[10px] px-3 py-1 rounded border border-chaos/20 uppercase font-bold tracking-wider font-mono">
                           {report?.error_type || "UNKNOWN_VECTOR"}
                         </span>
                         <span className="bg-neon/10 text-neon text-[10px] px-3 py-1 rounded border border-neon/20 uppercase font-bold tracking-wider font-mono">
                           Confidence: {report?.confidence || "98"}%
                         </span>
                      </div>
                      Neural Engine Analysis: <span className="text-text-main font-mono text-[13px] opacity-90 leading-relaxed block border-l-2 border-neon pl-4 mt-2 bg-bg-primary/40 py-2">
                         "{report?.root_cause || "Infrastructure discrepancy identified. Root cause traced to process lifecycle failure."}"
                      </span>
                   </PipelineStep>

                   <PipelineStep 
                     icon={Wrench} 
                     title="Targeted Recovery Execution" 
                     time="0.450" 
                     status={currentStep >= 3 ? "complete" : currentStep === 2 ? "active" : "pending"}
                     isActive={currentStep >= 2}
                   >
                      AI Intervention Recommended: <span className="text-neon font-bold uppercase tracking-tighter">[{report?.suggested_fix || "RESTART"}]</span>.
                      <div className="mt-4 bg-black/40 p-5 rounded font-mono text-xs border border-border-subtle text-text-dim/90 leading-relaxed shadow-inner">
                         <div className="flex items-center gap-2 mb-2 text-neon/60 border-b border-border-subtle/30 pb-1">
                            <RotateCcw size={10} />
                            <span>EXECUTION_CMD</span>
                         </div>
                         <span className="text-neon/80 mr-2">$</span> {report?.detailed_fix || "docker restart " + targetName}
                      </div>
                   </PipelineStep>

                   <PipelineStep 
                     icon={CheckCircle2} 
                     title="Operational Equilibrium Restored" 
                     time="1.120" 
                     status={currentStep >= 4 ? "complete" : currentStep === 3 ? "active" : "pending"}
                     isActive={currentStep >= 3}
                   >
                     Final Outcome: <span className="text-neon font-bold uppercase">[{report?.resolution_status || "SUCCESS"}]</span>. 
                     System stabilizes. All metrics have returned within nominal parameters. 
                     The incident has been logged for persistent training.
                   </PipelineStep>
                </div>

                {currentStep === 4 && (
                  <div className="mt-12 flex justify-center animate-in zoom-in slide-in-from-bottom-6 duration-1000">
                    <button 
                      onClick={handleReset}
                      className="px-12 py-4 bg-neon text-black text-[11px] font-bold font-mono tracking-[0.2em] hover:bg-neon/80 transition-all rounded shadow-[0_0_20px_rgba(0,255,102,0.3)] uppercase active:scale-95"
                    >
                      Acknowledge & Confirm Stability
                    </button>
                  </div>
                )}
             </div>
           )}
        </div>

        {/* Right: Reasoning Terminal */}
        <div className="col-span-4 flex flex-col gap-6 h-full overflow-hidden">
           <div className="cyber-panel flex-1 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between mb-4 border-b border-border-subtle pb-3">
                 <div className="flex items-center gap-2">
                    <Brain size={16} className="text-neon" />
                    <h3 className="text-[11px] font-bold font-mono tracking-widest text-text-dim uppercase">Reasoning Trace</h3>
                 </div>
                 <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-neon animate-pulse"></div>
                    <div className="w-2 h-2 rounded-full bg-border-subtle"></div>
                 </div>
              </div>
              
              <div className="space-y-4 flex-1 flex flex-col overflow-hidden">
                  <div className="p-4 bg-bg-primary/50 border-l-2 border-neon/40 shadow-inner">
                     <span className="text-[10px] text-neon/70 font-bold block mb-1 uppercase tracking-widest font-mono">Classification Strategy</span>
                     <p className="text-xs text-text-main font-mono italic opacity-90 leading-relaxed">
                        Utilizing <span className="text-neon font-bold">Structural-SVM + TF-IDF Bundle</span>. 
                        Targeting 128-dimensional signal space for <span className="text-chaos font-bold uppercase">{report?.error_type || "NONE"}</span> failure mode.
                     </p>
                  </div>

                 <div className="flex-1 overflow-hidden relative border border-border-subtle/50 rounded p-1 bg-black/40">
                    <div className="absolute top-0 right-0 p-2 z-10">
                       <span className="text-[9px] font-bold text-text-dim/30 font-mono tracking-tighter">RAW_LOG_ANALYSIS</span>
                    </div>
                    <Terminal 
                       title="ANALYZER_STDOUT" 
                       limit={50} 
                       className="h-full text-[10px] font-mono" 
                    />
                 </div>

                 <div className="pt-4 border-t border-border-subtle shrink-0">
                     <div className="flex justify-between items-center mb-2">
                        <span className="text-[10px] text-text-dim font-bold uppercase tracking-[0.2em] font-mono opacity-60">Confidence Probability</span>
                        <span className="text-sm font-bold font-mono text-neon">{(report?.confidence / 100) || "0.98"}</span>
                     </div>
                    <div className="h-1 bg-border-subtle/50 rounded-full overflow-hidden">
                       <div 
                         className="h-full bg-gradient-to-r from-chaos onto-yellow-500 to-neon transition-all duration-2000"
                         style={{ width: currentStep >= 2 ? `${report?.confidence || 98}%` : '0%' }}
                       ></div>
                    </div>
                 </div>
              </div>
           </div>

           <div className="cyber-panel shrink-0 bg-transparent border-border-subtle/50">
              <h3 className="text-[10px] font-bold font-mono tracking-[0.2em] text-text-dim uppercase mb-4 opacity-70 italic">Final System Resolution</h3>
              <div className={cn(
                "p-5 rounded border text-center transition-all duration-1000 shadow-inner",
                currentStep >= 4 ? "bg-neon/10 border-neon/40 shadow-[0_0_15px_rgba(0,255,102,0.05)]" : 
                activeHealingSession ? "bg-yellow-500/10 border-yellow-500/40 animate-pulse" :
                "bg-bg-primary border-border-subtle"
              )}>
                 <span className={cn(
                   "text-sm font-bold font-mono uppercase tracking-[0.3em]",
                   currentStep >= 4 ? "text-neon" : 
                   activeHealingSession ? "text-yellow-500" : "text-text-dim/30"
                 )}>
                   {currentStep >= 4 ? "CLUSTER_SAFE" : activeHealingSession ? "DISSIPATING_THREAT" : "NO_ANOMALIES"}
                 </span>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default HealingPipeline;
