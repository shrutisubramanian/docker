import React from 'react';
import { useSimulation } from '../context/SimulationContext';
import { ShieldAlert } from 'lucide-react';

const GlitchOverlay = () => {
  const { isChaosActive, activeHealingSession } = useSimulation();

  // Reappear only if the healing process fails, otherwise hide during active sessions
  const shouldShow = isChaosActive && (!activeHealingSession || activeHealingSession.status === 'failed');

  if (!shouldShow) return null;

  return (
    <div className="fixed inset-0 z-[100] pointer-events-none overflow-hidden bg-red-500/5 mix-blend-overlay">
      {/* Glitch Slices */}
      <div className="absolute inset-0 bg-[rgba(255,0,0,0.1)] animate-glitch-1"></div>
      <div className="absolute inset-0 bg-[rgba(0,255,255,0.1)] animate-glitch-2"></div>
      
      {/* Static Noise */}
      <div className="absolute inset-0 opacity-20 bg-[url('https://media.giphy.com/media/oEI9uWUicKgS2Uz43a/giphy.gif')] bg-repeat"></div>
      
      {/* Alert Icon */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-4 animate-pulse">
        <ShieldAlert size={120} className="text-red-500 drop-shadow-[0_0_20px_rgba(255,0,0,1)]" />
        <h2 className="text-4xl font-black text-white font-mono tracking-[0.5em] bg-red-600 px-8 py-2 skew-x-[-20deg] border-4 border-white shadow-[10px_10px_0_black]">
          CHAOS_INJECTED
        </h2>
        <div className="text-xs font-mono text-red-500 font-bold bg-black px-4 py-1 animate-bounce">
          SYSTEM_STABILITY: CRITICAL_FAILURE_SIMULATED
        </div>
      </div>
      
      {/* Scanning lines */}
      <div className="absolute inset-0 scanline-fast"></div>
    </div>
  );
};

export default GlitchOverlay;
