import React from 'react';
import { Server, Cpu, MemoryStick, CheckCircle2, XCircle, HardDrive, Globe } from 'lucide-react';

const ContainerTable = ({ containers = [], loading = false, onSelect, selectedId }) => {
  return (
    <div className="bg-dark-panel rounded-xl border border-dark-border overflow-hidden p-6 shadow-lg mb-6">
      <div className="flex items-center space-x-2 mb-6">
        <Server className="w-5 h-5 text-blue-400" />
        <h2 className="text-xl font-semibold text-slate-100 tracking-wide">System Overview</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-dark-border text-slate-400 text-sm uppercase tracking-wider">
              <th className="py-3 px-4 font-medium">Container</th>
              <th className="py-3 px-4 font-medium">Status</th>
              <th className="py-3 px-4 font-medium">CPU</th>
              <th className="py-3 px-4 font-medium">Memory</th>
              <th className="py-3 px-4 font-medium">Disk Usage</th>
              <th className="py-3 px-4 font-medium">Net Latency</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="py-8 text-center text-slate-500">
                  <div className="flex justify-center items-center space-x-2">
                    <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                    <span>Loading container metrics...</span>
                  </div>
                </td>
              </tr>
            ) : containers.length === 0 ? (
              <tr>
                <td colSpan="6" className="py-8 text-center text-slate-500">No containers found</td>
              </tr>
            ) : (
              containers.map((c, i) => (
                <tr
                  key={i}
                  onClick={() => onSelect(c.name)}
                  className={`border-b border-dark-border/50 transition-colors cursor-pointer ${selectedId === c.name ? 'bg-indigo-500/10' : 'hover:bg-slate-800/30'
                    }`}
                >
                  <td className="py-4 px-4 font-medium text-slate-200">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-slate-800 rounded-lg">
                        <Server className={`w-4 h-4 ${selectedId === c.name ? 'text-indigo-400' : 'text-slate-400'}`} />
                      </div>
                      <span>{c.name}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${c.status.toLowerCase() === 'running'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                      {c.status.toLowerCase() === 'running'
                        ? <CheckCircle2 className="w-3 h-3 mr-1.5" />
                        : <XCircle className="w-3 h-3 mr-1.5" />
                      }
                      {c.status}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-slate-300">
                    <div className="flex items-center space-x-2">
                      <Cpu className="w-4 h-4 text-slate-500" />
                      <span>{c.cpu || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-slate-300">
                    <div className="flex items-center space-x-2">
                      <MemoryStick className="w-4 h-4 text-slate-500" />
                      <span>{c.memory || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-slate-300">
                    <div className="flex items-center space-x-2">
                      <HardDrive className="w-4 h-4 text-slate-500" />
                      <span>{c.disk || '0.1%'}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-slate-300">
                    <div className="flex items-center space-x-2">
                      <Globe className="w-4 h-4 text-slate-500" />
                      <span>{c.net || '0ms'}</span>
                    </div>
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

export default ContainerTable;