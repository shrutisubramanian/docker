import React from 'react';
import { ShieldAlert, RefreshCw, CheckCircle } from 'lucide-react';

const IncidentTable = ({ incidents = [], loading = false }) => {
  return (
    <div className="bg-dark-panel rounded-xl border border-dark-border overflow-hidden p-6 shadow-lg mb-6 flex-1 flex flex-col">
      <div className="flex items-center space-x-2 mb-6">
        <ShieldAlert className="w-5 h-5 text-indigo-400" />
        <h2 className="text-xl font-semibold text-slate-100 tracking-wide">Incident History</h2>
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse min-w-[500px]">
          <thead>
            <tr className="border-b border-dark-border text-slate-400 text-sm uppercase tracking-wider">
              <th className="py-3 px-4 font-medium">Time</th>
              <th className="py-3 px-4 font-medium">Container</th>
              <th className="py-3 px-4 font-medium">Issue</th>
              <th className="py-3 px-4 font-medium">Action</th>
              <th className="py-3 px-4 font-medium text-right">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" className="py-8 text-center text-slate-500">
                  <div className="flex justify-center items-center space-x-2">
                    <div className="animate-spin h-5 w-5 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
                    <span>Loading incidents...</span>
                  </div>
                </td>
              </tr>
            ) : incidents.length === 0 ? (
              <tr>
                <td colSpan="5" className="py-8 text-center text-slate-500">No recent incidents found</td>
              </tr>
            ) : (
              incidents.map((inc, i) => (
                <tr key={i} className="border-b border-dark-border/50 hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-4 text-slate-400 font-mono text-xs">{inc.time}</td>
                  <td className="py-4 px-4 font-medium text-slate-200">{inc.container}</td>
                  <td className="py-4 px-4 text-rose-400 text-sm">{inc.issue}</td>
                  <td className="py-4 px-4 text-slate-300 text-sm">{inc.action}</td>
                  <td className="py-4 px-4 text-right">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      {inc.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IncidentTable;
