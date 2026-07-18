import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { NotificationLog } from '../../types/platform';
import { CheckCheck } from 'lucide-react';

export const NotificationCenter: React.FC = () => {
  const { accessToken } = useAuth();
  const [notifications, setNotifications] = useState<NotificationLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/notifications', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setNotifications(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchNotifications();
    }
  }, [accessToken]);

  const markRead = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/notifications/${id}/read`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        fetchNotifications();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          In-App Notification Logs
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          Review critical system updates, warehouse thresholds, and audit review requests.
        </p>
      </div>

      {/* Notifications Table Log */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          Notification Inbox is empty.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Title</th>
                <th className="px-6 py-4">Message</th>
                <th className="px-6 py-4">Channel</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {notifications.map(n => (
                <tr key={n.id} className={`hover:bg-secondary/15 transition ${!n.read_status ? 'bg-indigo-500/[0.02]' : ''}`}>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                      !n.read_status ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 'bg-neutral-800 text-neutral-500 border-neutral-700'
                    }`}>
                      {n.read_status ? 'READ' : 'NEW'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-300 font-semibold">{n.title}</td>
                  <td className="px-6 py-4 text-neutral-400 max-w-sm truncate">{n.message}</td>
                  <td className="px-6 py-4 text-neutral-400">
                    <span className="px-1.5 py-0.5 bg-secondary border border-border/60 rounded text-[9px]">
                      {n.channel}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-400 font-mono text-[10px]">
                    {new Date(n.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {!n.read_status && (
                      <button
                        onClick={() => markRead(n.id)}
                        className="inline-flex items-center justify-center px-2 py-1 bg-white text-black hover:bg-neutral-200 rounded text-[10px] font-bold gap-1"
                      >
                        <CheckCheck size={10} />
                        Mark Read
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
