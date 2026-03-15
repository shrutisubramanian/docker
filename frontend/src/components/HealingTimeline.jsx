import React from 'react';
import { Activity, ShieldCheck, ActivitySquare } from 'lucide-react';

const HealingTimeline = ({ pipelineData }) => {
  if (!pipelineData) {
    return (
      <div className="bg-dark-panel rounded-xl border border-dark-border p-6 shadow-lg h-full flex flex-col items-center justify-center text-slate-500 min-h-[300px]">
        <ActivitySquare className="w-12 h-12 mb-4 opacity-50 text-slate-600" />
        <p>Run the healing pipeline to see diagnosis here.</p>
      </div>
    );
  }

  const { diagnosis, timeline } = pipelineData;

  return (
    <div className="bg-dark-panel rounded-xl border border-dark-border p-6 shadow-lg h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-semibold text-slate-100 tracking-wide">AI Diagnosis</h2>
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700/50 mb-6">
        <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-sm">
          <div>
            <p className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Container</p>
            <p className="text-slate-100 font-medium">{diagnosis?.container || 'Unknown'}</p>
          </div>
          <div>
            <p className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Detected Issue</p>
            <p className="text-rose-400 font-medium">{diagnosis?.issue || 'None'}</p>
          </div>
          <div className="col-span-2 pt-2 border-t border-slate-700/50">
            <p className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Root Cause</p>
            <p className="text-slate-200">{diagnosis?.root_cause || '-'}</p>
          </div>
          <div className="col-span-2 pt-2 border-t border-slate-700/50">
            <p className="text-slate-400 mb-1 text-xs uppercase tracking-wider font-semibold">Recommended Action</p>
            <p className="text-emerald-400 pb-1 font-medium">{diagnosis?.action || '-'}</p>
          </div>
        </div>
      </div>

      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Recovery Execution Log</h3>
      
      <div className="flex-1 overflow-y-auto relative pl-4 border-l border-slate-700 space-y-6 max-h-[250px] pr-2">
        {timeline && timeline.map((step, idx) => (
          <div key={idx} className="relative">
            <div className="absolute -left-[21px] mt-1.5 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-dark-panel"></div>
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 font-mono mb-1">{step.time}</span>
              <span className="text-sm text-slate-200">{step.message}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HealingTimeline;
