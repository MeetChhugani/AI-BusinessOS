import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { SystemSetting } from '../../types/platform';
import { Save } from 'lucide-react';

export const SystemSettings: React.FC = () => {
  const { accessToken } = useAuth();
  const [settingsList, setSettingsList] = useState<SystemSetting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState('');

  const fetchSettings = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/settings', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setSettingsList(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchSettings();
    }
  }, [accessToken]);

  const handleUpdate = async (key: string, val: string) => {
    setSaveSuccess('');
    try {
      const res = await fetch(`/api/v1/settings/${key}?value=${encodeURIComponent(val)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setSaveSuccess('Setting saved successfully!');
        fetchSettings();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
          System Administration Settings
        </h1>
        <p className="text-sm text-muted-foreground mt-1.5">
          General SMTP servers, generic upload repository directories, and administrative key-value parameters.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded text-xs font-semibold">
          {saveSuccess}
        </div>
      )}

      {/* Settings inputs list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : settingsList.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No system settings registered.
        </div>
      ) : (
        <div className="space-y-4 text-xs">
          {settingsList.map(setting => (
            <div key={setting.id} className="p-5 bg-card border border-neutral-800 rounded-2xl space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <span className="px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-[9px] font-mono text-neutral-400 mr-2 uppercase inline-block">
                    {setting.category}
                  </span>
                  <span className="font-bold text-white font-mono">{setting.key}</span>
                </div>
              </div>
              <p className="text-muted-foreground text-[10px]">{setting.description}</p>
              
              <div className="flex gap-3">
                <input
                  className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                  value={setting.value}
                  onChange={e => {
                    const updated = settingsList.map(s => s.id === setting.id ? { ...s, value: e.target.value } : s);
                    setSettingsList(updated);
                  }}
                />
                <button
                  onClick={() => handleUpdate(setting.key, setting.value)}
                  className="px-4 py-2 bg-white text-black hover:bg-neutral-200 rounded font-semibold transition inline-flex items-center gap-1.5"
                >
                  <Save size={12} />
                  Save
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
