import React from 'react';
import { 
  LayoutDashboard, 
  Skull, 
  Activity, 
  History as HistoryIcon, 
  Settings, 
  LifeBuoy,
  Zap,
  Cpu,
  Database,
  Bell,
  Sun,
  Moon,
  Power,
  RotateCcw,
  ShieldAlert,
  Search
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import GlitchOverlay from './GlitchOverlay';
import { useSimulation } from '../context/SimulationContext';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const Sidebar = ({ activeTab, setTab }) => {
  const { isChaosActive, isSimulationMode, toggleSimulationMode } = useSimulation();
  const items = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chaos', label: 'Chaos Suite', icon: Skull },
    { id: 'healing', label: 'Healing Pipeline', icon: Activity },
    { id: 'history', label: 'History', icon: HistoryIcon },
  ];

  return (
    <aside className="w-64 border-r border-border-subtle flex flex-col h-screen fixed left-0 top-0 z-20 bg-panel-bg transition-colors duration-300">
      <div className="p-6">
        <h1 className="text-neon font-bold text-xl tracking-tighter flex items-center gap-2">
          <Zap className={cn("fill-neon transition-all", isChaosActive && "text-red-500 fill-red-500 scale-125")} size={24} />
          {isChaosActive ? "SENTINEL_BREACHED" : "SYNTHETIC SENTINEL"}
        </h1>
        <p className="text-xs text-text-dim font-mono tracking-widest mt-1 uppercase opacity-80">
          {isChaosActive ? "PROTOCOL_FAILURE_INJECTED" : "AI COMMANDER V3.5.0"}
        </p>
      </div>

      <nav className="flex-1 mt-4">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => setTab(item.id)}
            className={cn(
              "w-full sidebar-item",
              activeTab === item.id && "active"
            )}
          >
            <item.icon size={20} />
            <span className="font-medium text-sm">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-border-subtle">
        <button 
          onClick={toggleSimulationMode}
          className={cn(
            "flex items-center gap-2 p-3 w-full border rounded-sm transition-all font-bold text-xs uppercase tracking-[0.2em]",
            isChaosActive ? "bg-red-500/10 text-red-500 border-red-500/30" : 
            isSimulationMode ? "bg-neon/10 text-neon border-neon/30 hover:bg-neon/20" :
            "bg-blue-500/10 text-blue-400 border-blue-500/30 hover:bg-blue-500/20"
          )}
        >
          {isChaosActive ? <ShieldAlert size={16} /> : <Activity size={16} />}
          {isChaosActive ? "CHAOS_INJECTED" : isSimulationMode ? "SIMULATION MODE: ON" : "REAL-TIME MODE: ACTIVE"}
        </button>
      </div>
    </aside>
  );
};

const Topbar = () => {
  const { isChaosActive, theme, toggleTheme } = useSimulation();
  return (
    <header className="h-16 border-b border-border-subtle bg-bg-primary/80 backdrop-blur-md sticky top-0 z-10 ml-64 flex items-center justify-between px-8 transition-colors duration-300">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-6">
          <div className="flex flex-col">
            <span className="text-xs text-text-dim font-mono font-bold tracking-widest">SYSTEM STATUS</span>
            <span className={cn("text-sm font-bold font-mono transition-colors tracking-tighter", isChaosActive ? "text-red-500" : "text-neon")}>
              {isChaosActive ? "CRITICAL_DRIFT" : "OPTIMAL_ACTIVE"}
            </span>
          </div>
          <div className="h-10 w-[1px] bg-border-subtle"></div>
          <div className="flex flex-col">
            <span className="text-xs text-text-dim font-mono font-bold tracking-widest">STABILITY</span>
            <span className={cn("text-sm font-bold font-mono transition-colors tracking-tighter", isChaosActive ? "text-red-500" : "text-text-main")}>
              {isChaosActive ? "41.2%" : "99.8%"}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" size={14} />
          <input 
            type="text" 
            placeholder="Search telemetry..."
            className="bg-panel-bg border border-border-subtle rounded-md pl-9 pr-4 py-1.5 text-xs text-text-main w-64 focus:outline-none focus:border-neon/50 transition-all"
          />
        </div>
        <button 
          onClick={toggleTheme}
          className="p-2 text-text-dim hover:text-neon transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        <div className="h-8 w-[1px] bg-border-subtle"></div>
      </div>
    </header>
  );
};

export const Layout = ({ children, activeTab, setTab }) => {
  return (
    <div className="min-h-screen bg-bg-primary flex transition-colors duration-300">
      <GlitchOverlay />
      <Sidebar activeTab={activeTab} setTab={setTab} />
      <div className="flex-1 flex flex-col">
        <Topbar />
        <main className="ml-64 p-8 flex-1">
          {children}
        </main>
      </div>
    </div>
  );
};
