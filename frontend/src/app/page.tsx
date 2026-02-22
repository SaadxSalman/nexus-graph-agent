"use client";
import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";
import { LayoutGrid, MessageSquare, Activity, User } from "lucide-react";

export default function NexusDashboard() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [typing, setTyping] = useState("");

  useEffect(() => {
    const s = io(process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:3001", {
      auth: { workspaceId: "enterprise-main-01" }
    });

    s.on("activity_log", (log) => setLogs(prev => [log, ...prev].slice(0, 5)));
    s.on("user_typing", (user) => {
      setTyping(`${user} is moving a task...`);
      setTimeout(() => setTyping(""), 2000);
    });

    setSocket(s);
    return () => { s.disconnect(); };
  }, []);

  const triggerUpdate = (status: string) => {
    socket?.emit("task_update", { title: "API Integration", status, user: "Saad" });
    socket?.emit("typing", "Saad");
  };

  return (
    <main className="max-w-7xl mx-auto p-8">
      <header className="mb-12">
        <h2 className="text-3xl font-bold mb-2">Workspace Overview</h2>
        <p className="text-zinc-500 italic">{typing || "All systems operational"}</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Kanban Board Mockup */}
        <section className="lg:col-span-2 grid grid-cols-2 gap-4">
          <div className="kanban-column">
            <h3 className="flex items-center gap-2 mb-4 font-semibold text-zinc-400">
              <LayoutGrid size={18} /> Todo
            </h3>
            <div 
              onClick={() => triggerUpdate("In Progress")}
              className="p-4 bg-zinc-800 rounded-lg border border-zinc-700 cursor-pointer hover:border-indigo-500 transition-all"
            >
              <h4 className="font-medium">API Integration</h4>
              <p className="text-xs text-zinc-500 mt-2">High Priority • Enterprise</p>
            </div>
          </div>
          <div className="kanban-column">
            <h3 className="flex items-center gap-2 mb-4 font-semibold text-zinc-400">
              <Activity size={18} /> In Progress
            </h3>
          </div>
        </section>

        {/* Real-time Activity Feed */}
        <aside className="space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-4 flex items-center gap-2">
              <MessageSquare size={16} /> Activity Feed
            </h3>
            <div className="space-y-4">
              {logs.map((log, i) => (
                <div key={i} className="text-sm border-l-2 border-indigo-500 pl-4 py-1">
                  <span className="font-bold text-white">{log.user}</span> 
                  <span className="text-zinc-400"> {log.action}</span>
                </div>
              ))}
              {logs.length === 0 && <p className="text-zinc-600 text-xs italic">Waiting for interactions...</p>}
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}