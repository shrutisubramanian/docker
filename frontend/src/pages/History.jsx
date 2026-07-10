import React, { useState, useEffect } from 'react';
import { 
  getIncidents 
} from '../api';
import { 
  History as HistoryIcon, 
  Search, 
  Download, 
  ExternalLink, 
  CheckCircle2, 
  ShieldAlert, 
  Activity, 
  ChevronLeft, 
  ChevronRight,
  RotateCcw
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const History = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    getIncidents().then(data => {
      setIncidents(data);
      setLoading(false);
    });
  }, []);

  const filteredIncidents = incidents.filter(inc => {
    if (filter === 'ALL') return true;
    if (filter === 'CRITICAL') return inc.severity === 'CRITICAL';
    if (filter === 'RESOLVED') return true;
    return true;
  });

  const totalPages = Math.ceil(filteredIncidents.length / itemsPerPage);
  const paginatedIncidents = filteredIncidents.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Reset to page 1 when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [filter]);

  const handleGeneratePDF = () => {
    const doc = new jsPDF();
    
    // Add Report Header
    doc.setFontSize(22);
    doc.setTextColor(0, 255, 102); // Neon Green
    doc.text('SYNTHETIC SENTINEL: AUDIT REPORT', 14, 22);
    
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);
    doc.text(`Sector: PROD_CLUSTER_MAIN`, 14, 35);
    
    // Add Table
    const tableColumn = ["Timestamp", "Container", "Anomaly", "AI Diagnosis", "Status"];
    const tableRows = incidents.map(inc => [
      new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString(),
      inc.container,
      inc.error_type,
      inc.root_cause || "Autonomous resolution applied.",
      "RESOLVED"
    ]);

    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 45,
      theme: 'grid',
      headStyles: { fillColor: [0, 255, 102], textColor: [0, 0, 0] },
      styles: { fontSize: 8, font: 'courier' }
    });

    doc.save(`synthetic_sentinel_audit_${new Date().getTime()}.pdf`);
  };

  const latestIncidents = incidents.slice(0, 3);

  return (
    <div className="flex flex-col gap-8 h-full">
      <div className="flex justify-between items-center border-b border-border-subtle pb-6">
        <div className="flex items-center gap-4">
           <div className="w-12 h-12 bg-neon/10 border border-neon/20 rounded-lg flex items-center justify-center text-neon">
              <HistoryIcon size={24} />
           </div>
           <div>
              <h2 className="text-3xl font-bold tracking-tighter uppercase font-mono text-text-main">Incident Lifecycle History</h2>
              <p className="text-text-dim font-mono text-[11px] mt-0.5 italic">Persistent archive of AI-managed infrastructure transformations.</p>
           </div>
        </div>
        <div className="flex items-center gap-3">
           <div className="flex rounded-md overflow-hidden border border-border-subtle p-1 bg-bg-primary">
              {['ALL', 'CRITICAL', 'RESOLVED'].map(f => (
                 <button 
                   key={f}
                   onClick={() => setFilter(f)}
                   className={cn(
                     "px-4 py-1.5 text-[10px] font-bold tracking-widest rounded transition-all",
                     filter === f ? "bg-neon text-black" : "text-text-dim hover:text-text-main"
                   )}
                 >
                   {f}
                 </button>
              ))}
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-2">
          {latestIncidents.length > 0 ? latestIncidents.map((inc, idx) => (
            <div key={idx} className={cn(
              "cyber-panel p-4 flex items-center gap-4 border-l-4",
              inc.severity === 'CRITICAL' ? "border-chaos" : "border-neon"
            )}>
               <div className={cn(
                 "w-12 h-12 rounded-lg flex items-center justify-center",
                 inc.severity === 'CRITICAL' ? "bg-chaos/10 text-chaos" : "bg-neon/10 text-neon"
               )}>
                  {inc.severity === 'CRITICAL' ? <ShieldAlert size={24} /> : <CheckCircle2 size={24} />}
               </div>
               <div>
                  <span className="text-[9px] text-text-dim font-bold uppercase tracking-widest">{inc.error_type}</span>
                  <h4 className="text-sm font-bold text-text-main tracking-widest uppercase">{inc.container}</h4>
               </div>
            </div>
          )) : [1,2,3].map(i => (
            <div key={i} className="cyber-panel p-4 flex items-center gap-4 border-l-4 border-border-subtle opacity-50">
               <div className="w-12 h-12 rounded-lg bg-bg-primary flex items-center justify-center text-text-dim">
                  <Activity size={24} />
               </div>
               <div>
                  <span className="text-[9px] text-text-dim font-bold uppercase tracking-widest">Awaiting Data</span>
                  <h4 className="text-sm font-bold text-text-main tracking-widest uppercase">System Scanning...</h4>
               </div>
            </div>
          ))}
      </div>

      <div className="cyber-panel flex-1 flex flex-col relative overflow-hidden group min-h-[400px]">
         <div className="scanline"></div>
          <div className="p-6 border-b border-border-subtle flex justify-between items-center">
             <div className="flex items-center gap-3">
                <div className="text-[10px] text-text-dim font-bold uppercase tracking-[0.3em]">Infrastructure Health Alerts</div>
                <span className="px-2 py-0.5 bg-chaos/10 text-chaos text-[9px] font-bold border border-chaos/20 uppercase rounded-sm">3 Critical Events Detected</span>
             </div>
             <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" size={12} />
                <input 
                  type="text" 
                  placeholder="QUERY LOGS..." 
                  className="bg-bg-primary border border-border-subtle pl-10 pr-4 py-2 rounded text-xs font-mono text-text-main focus:outline-none focus:border-neon/30"
                />
             </div>
          </div>

         <div className="flex-1 overflow-y-auto">
             <table className="w-full text-[11px] font-mono">
                <thead>
                   <tr className="text-text-dim font-bold uppercase border-b border-border-subtle bg-bg-primary">
                      <th className="px-6 py-4 text-left">Timestamp</th>
                      <th className="px-6 py-4 text-left">Affected Container</th>
                      <th className="px-6 py-4 text-center">Detected Anomaly</th>
                      <th className="px-6 py-4 text-left">AI Diagnosis</th>
                      <th className="px-6 py-4 text-center">Outcome</th>
                      <th className="px-6 py-4 text-right">Action</th>
                   </tr>
                </thead>
                 <tbody className="divide-y divide-border-subtle">
                  {loading ? (
                    <tr><td colSpan="6" className="p-20 text-center text-neon animate-pulse uppercase tracking-[0.5em] font-bold">Retrieving Archival Data...</td></tr>
                  ) : paginatedIncidents.length === 0 ? (
                    <tr><td colSpan="6" className="p-20 text-center text-text-dim italic uppercase tracking-widest">No matching logs found in sector archive.</td></tr>
                  ) : paginatedIncidents.map((inc, i) => (
                    <tr key={`${inc.container}-${inc.timestamp}-${i}`} className="group hover:bg-bg-primary transition-colors">
                       <td className="px-6 py-4">
                          <div className="text-text-main font-bold">{new Date().toLocaleTimeString()}</div>
                          <div className="text-text-dim text-[10px]">OCT 24, 2026</div>
                       </td>
                       <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                             <div className="w-8 h-8 rounded border border-border-subtle flex items-center justify-center text-text-dim">
                                <RotateCcw size={14} />
                             </div>
                             <div className="text-text-main font-bold">{inc.container}</div>
                          </div>
                       </td>
                        <td className="px-6 py-4 text-center">
                           <span className={cn(
                             "px-2 py-0.5 rounded text-[9px] font-bold border",
                             inc.severity === 'CRITICAL' ? "bg-chaos/10 text-chaos border-chaos/20" : "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
                           )}>
                             {inc.error_type}
                           </span>
                        </td>
                       <td className="px-6 py-4 text-text-dim max-w-xs truncate italic font-mono">
                          "{inc.root_cause || "Recursive retry stack detected leading to ingress layer failure."}"
                       </td>
                       <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                             <div className="w-1.5 h-1.5 rounded-full bg-neon"></div>
                             <span className="text-neon font-bold uppercase text-[10px]">Resolved</span>
                          </div>
                       </td>
                       <td className="px-6 py-4 text-right">
                          <button className="p-2 text-text-dim hover:text-text-main transition-all border border-transparent hover:border-border-subtle rounded">
                             <ExternalLink size={14} />
                          </button>
                       </td>
                    </tr>
                  ))}
               </tbody>
            </table>
         </div>

          <div className="p-4 border-t border-border-subtle flex justify-between items-center bg-bg-primary">
             <span className="text-xs text-text-dim font-bold uppercase tracking-widest italic">
                Showing {Math.min((currentPage - 1) * itemsPerPage + 1, filteredIncidents.length)} - {Math.min(currentPage * itemsPerPage, filteredIncidents.length)} of {filteredIncidents.length} Records
             </span>
             <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                   <button 
                     onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                     disabled={currentPage === 1}
                     className="p-1.5 text-text-dim hover:text-neon transition-all disabled:opacity-20 disabled:cursor-not-allowed"
                   >
                     <ChevronLeft size={18} />
                   </button>
                   
                   {[...Array(totalPages)].map((_, i) => {
                     const page = i + 1;
                     // Show limited pages if many
                     if (totalPages > 5 && (page > 3 && page < totalPages)) {
                        if (page === 4) return <span key="dots" className="text-text-dim mx-1">...</span>;
                        return null;
                     }
                     return (
                       <button 
                         key={page}
                         onClick={() => setCurrentPage(page)}
                         className={cn(
                           "w-8 h-8 flex items-center justify-center text-[11px] font-bold rounded transition-all",
                           currentPage === page ? "bg-neon text-black shadow-neon" : "text-text-dim hover:bg-bg-primary hover:text-text-main"
                         )}
                       >
                         {page}
                       </button>
                     );
                   })}

                   <button 
                     onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                     disabled={currentPage === totalPages || totalPages === 0}
                     className="p-1.5 text-text-dim hover:text-neon transition-all disabled:opacity-20 disabled:cursor-not-allowed"
                   >
                     <ChevronRight size={18} />
                   </button>
                </div>
                 <button 
                   onClick={handleGeneratePDF}
                   className="flex items-center gap-2 px-4 py-2 bg-neon text-black text-xs font-bold rounded hover:bg-neon/80 transition-all shadow-neon active:scale-95"
                 >
                    <Download size={16} />
                    GENERATE AUDIT PDF
                 </button>
              </div>
           </div>
       </div>
    </div>
  );
};

export default History;
