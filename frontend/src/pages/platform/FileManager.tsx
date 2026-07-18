import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { FileMetadata } from '../../types/platform';
import { FileText, Upload } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const FileManager: React.FC = () => {
  const { accessToken } = useAuth();
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Upload state
  const [uploadModal, setUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/files', { headers: { 'Authorization': `Bearer ${accessToken}` } });
      if (res.ok) setFiles(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchFiles();
    }
  }, [accessToken]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch('/api/v1/files/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` },
        body: formData
      });
      if (res.ok) {
        setUploadModal(false);
        setSelectedFile(null);
        fetchFiles();
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
            Abstract File Storage
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Generic abstraction interface manager tracking file properties and duplicate SHA256 hashes.
          </p>
        </div>

        <button
          onClick={() => setUploadModal(true)}
          className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-semibold transition"
        >
          <Upload size={14} className="mr-2" />
          Upload File
        </button>
      </div>

      {/* Files List Table */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map(i => <div key={i} className="h-14 w-full animate-pulse bg-neutral-800/40 rounded-xl" />)}
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-20 bg-card rounded-2xl border border-border text-muted-foreground text-sm">
          No files stored. Upload some attachments first.
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-secondary/40 text-xs text-muted-foreground font-semibold border-b border-border">
              <tr>
                <th className="px-6 py-4">File Name</th>
                <th className="px-6 py-4">Mime Type</th>
                <th className="px-6 py-4">Size (Bytes)</th>
                <th className="px-6 py-4">SHA256 Checksum</th>
                <th className="px-6 py-4 text-right">Upload Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-white font-medium text-xs">
              {files.map(file => (
                <tr key={file.id} className="hover:bg-secondary/15 transition">
                  <td className="px-6 py-4 font-bold text-neutral-300 flex items-center gap-2">
                    <FileText size={14} className="text-muted-foreground" />
                    {file.name}
                  </td>
                  <td className="px-6 py-4 text-neutral-300">{file.mime_type}</td>
                  <td className="px-6 py-4 font-mono text-neutral-300">{file.file_size_bytes.toLocaleString()} B</td>
                  <td className="px-6 py-4 font-mono text-neutral-400 text-[10px] max-w-xs truncate" title={file.sha256_checksum}>
                    {file.sha256_checksum}
                  </td>
                  <td className="px-6 py-4 text-right text-neutral-400 font-mono text-[10px]">
                    {new Date(file.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {uploadModal && (
          <>
            <div className="fixed inset-0 bg-black/60 z-40" onClick={() => setUploadModal(false)} />
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-sm bg-card border border-border rounded-2xl p-6 z-50 shadow-2xl"
            >
              <h2 className="text-base font-bold text-white mb-4">Upload File</h2>
              <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
                <div className="p-6 bg-secondary/35 border border-dashed border-border rounded-xl text-center flex flex-col items-center justify-center gap-2">
                  <Upload size={24} className="text-muted-foreground mb-1" />
                  <input
                    type="file"
                    required
                    onChange={handleFileChange}
                    className="text-xs text-neutral-400 file:mr-4 file:py-1.5 file:px-3 file:rounded file:border file:border-border file:text-[10px] file:font-semibold file:bg-secondary file:text-white file:hover:bg-neutral-800 cursor-pointer"
                  />
                  {selectedFile && (
                    <span className="text-[10px] text-indigo-400 mt-2 font-bold block">Selected: {selectedFile.name}</span>
                  )}
                </div>

                <div className="flex space-x-3 pt-4 border-t border-border/40">
                  <button type="button" onClick={() => setUploadModal(false)} className="w-1/2 py-2 bg-secondary text-white rounded hover:bg-neutral-800 transition">Cancel</button>
                  <button type="submit" className="w-1/2 py-2 bg-white text-black font-semibold rounded hover:bg-neutral-200 transition">Upload</button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
