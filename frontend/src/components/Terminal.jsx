import React, { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, ChevronRight } from 'lucide-react';
import { useSimulation } from '../context/SimulationContext';
import { twMerge } from 'tailwind-merge';
import { clsx } from 'clsx';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const Terminal = ({ className, title = "LIVE_LOG_STREAM", limit = 10 }) => {
  const { logs } = useSimulation();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [logs]);

  return (
    <div className={cn("bg-panel-bg border border-border-subtle rounded p-3 font-mono text-[10px] h-48 flex flex-col transition-colors duration-300", className)}>
      <div className="text-text-dim mb-2 flex items-center gap-2 border-b border-border-subtle pb-1 uppercase tracking-widest text-[9px] font-bold">
        <TerminalIcon size={12} />
        {title}
        <div className="ml-auto flex gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-red-500/50"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/50"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-green-500/50"></div>
        </div>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-1 pr-2">
        {logs.slice(0, limit).map((log) => (
          <div key={log.id} className="flex gap-2 group animate-in fade-in slide-in-from-left-1 duration-300">
            <span className="text-text-dim shrink-0">[{log.time}]</span>
            <span className={cn(
              "font-bold shrink-0 uppercase",
              log.type === 'error' ? 'text-chaos' : 
              log.type === 'success' ? 'text-neon' : 
              'text-cyan-500'
            )}>
              {log.type === 'error' ? 'ERR' : log.type === 'success' ? 'OK' : 'SYS'}
            </span>
            <span className="text-text-main/80 group-hover:text-text-main transition-colors break-all">
              <ChevronRight size={10} className="inline mr-1 text-text-dim/50" />
              {log.text}
            </span>
          </div>
        ))}
        <div className="flex gap-2">
          <span className="text-neon animate-pulse">_</span>
        </div>
      </div>
    </div>
  );
};

export default Terminal;
