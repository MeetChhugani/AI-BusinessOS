import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { CRMTask, CRMMeeting } from '../../types/crm';
import { Plus, Calendar, Clock, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const TasksCalendarPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [tasks, setTasks] = useState<CRMTask[]>([]);
  const [meetings, setMeetings] = useState<CRMMeeting[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Requisitions modally
  const [taskModal, setTaskModal] = useState(false);
  const [meetModal, setMeetModal] = useState(false);

  // Form states
  const [taskForm, setTaskForm] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'LOW'
  });
  const [meetForm, setMeetForm] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    location: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const taskRes = await fetch('/api/v1/tasks', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      const meetRes = await fetch('/api/v1/tasks/meetings', { headers: { 'Authorization': `Bearer ${accessToken}` } });

      if (taskRes.ok) setTasks(await taskRes.json());
      if (meetRes.ok) setMeetings(await meetRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchData();
    }
  }, [accessToken]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          title: taskForm.title,
          description: taskForm.description || undefined,
          due_date: new Date(taskForm.due_date).toISOString(),
          priority: taskForm.priority
        })
      });
      if (res.ok) {
        setTaskModal(false);
        setTaskForm({ title: '', description: '', due_date: '', priority: 'LOW' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateMeeting = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/v1/tasks/meetings?title=${encodeURIComponent(meetForm.title)}&description=${encodeURIComponent(meetForm.description)}&start_time=${new Date(meetForm.start_time).toISOString()}&end_time=${new Date(meetForm.end_time).toISOString()}&location=${encodeURIComponent(meetForm.location)}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setMeetModal(false);
        setMeetForm({ title: '', description: '', start_time: '', end_time: '', location: '' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold font-display text-white tracking-tight">
            Tasks & Meetings Calendar
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Log call logs, track pending followups, and sync shared meeting calendar grids.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setTaskModal(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 bg-secondary text-white hover:bg-neutral-800 rounded-lg text-xs font-semibold transition border border-border"
          >
            Create Task
          </button>
          <button
            onClick={() => setMeetModal(true)}
            className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
          >
            <Plus size={14} className="mr-2" />
            Schedule Meeting
          </button>
        </div>
      </div>

      {/* Main split details view */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Follow-up Tasks */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <AlertCircle size={16} className="text-blue-400" />
            Follow Up Tasks
          </h3>

          {isLoading ? (
            <div className="space-y-3">
              <div className="h-12 w-full animate-pulse bg-neutral-800/40 rounded-xl" />
            </div>
          ) : tasks.length === 0 ? (
            <p className="text-xs text-muted-foreground">All tasks completed successfully.</p>
          ) : (
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
              {tasks.map(task => (
                <div key={task.id} className="p-4 bg-secondary/35 border border-border/60 rounded-xl flex justify-between items-center text-xs">
                  <div>
                    <span className="font-bold text-white block">{task.title}</span>
                    <span className="text-[10px] text-muted-foreground font-mono mt-0.5">Due: {task.due_date.slice(0, 16).replace('T', ' ')}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[8px] font-bold border ${
                    task.priority === 'HIGH' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                  }`}>
                    {task.priority}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Meeting Calendar List */}
        <div className="glass-card rounded-2xl p-6 border border-neutral-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Calendar size={16} className="text-purple-400" />
            Meeting Schedules
          </h3>

          {isLoading ? (
            <div className="space-y-3">
              <div className="h-12 w-full animate-pulse bg-neutral-800/40 rounded-xl" />
            </div>
          ) : meetings.length === 0 ? (
            <p className="text-xs text-muted-foreground">No upcoming meetings scheduled.</p>
          ) : (
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
              {meetings.map(meet => (
                <div key={meet.id} className="p-4 bg-secondary/35 border border-border/60 rounded-xl flex justify-between items-center text-xs">
                  <div>
                    <span className="font-bold text-white block">{meet.title}</span>
                    <span className="text-[10px] text-muted-foreground font-mono mt-0.5">
                      Start: {meet.start_time.slice(0, 16).replace('T', ' ')} | Location: {meet.location || 'Online'}
                    </span>
                  </div>
                  <Clock size={16} className="text-muted-foreground" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Task Creation Modal */}
      <AnimatePresence>
        {taskModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setTaskModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Create Task Requisition</h2>
              <form onSubmit={handleCreateTask} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Task Title</label>
                  <input
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={taskForm.title}
                    onChange={e => setTaskForm(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Description</label>
                  <textarea
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none h-20"
                    value={taskForm.description}
                    onChange={e => setTaskForm(prev => ({ ...prev, description: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Due Date & Time</label>
                    <input
                      required
                      type="datetime-local"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={taskForm.due_date}
                      onChange={e => setTaskForm(prev => ({ ...prev, due_date: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Priority</label>
                    <select
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={taskForm.priority}
                      onChange={e => setTaskForm(prev => ({ ...prev, priority: e.target.value }))}
                    >
                      <option value="LOW">LOW</option>
                      <option value="MEDIUM">MEDIUM</option>
                      <option value="HIGH">HIGH</option>
                    </select>
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setTaskModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Save Task</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Meeting Creation Modal */}
      <AnimatePresence>
        {meetModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setMeetModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Schedule Calendar Meeting</h2>
              <form onSubmit={handleCreateMeeting} className="space-y-4 text-xs">
                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Meeting Subject</label>
                  <input
                    required
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={meetForm.title}
                    onChange={e => setMeetForm(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>

                <div>
                  <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Location</label>
                  <input
                    className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                    value={meetForm.location}
                    onChange={e => setMeetForm(prev => ({ ...prev, location: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">Start Time</label>
                    <input
                      required
                      type="datetime-local"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={meetForm.start_time}
                      onChange={e => setMeetForm(prev => ({ ...prev, start_time: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1.5 uppercase font-semibold text-[10px]">End Time</label>
                    <input
                      required
                      type="datetime-local"
                      className="w-full px-3 py-2 bg-secondary text-white rounded border border-border focus:outline-none"
                      value={meetForm.end_time}
                      onChange={e => setMeetForm(prev => ({ ...prev, end_time: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setMeetModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Confirm Meeting</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
