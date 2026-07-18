import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Upload, Check, AlertTriangle, ArrowRight, ArrowLeft } from 'lucide-react';

interface RowError {
  index: number;
  field: string;
  message: string;
}

export const CSVImportPage: React.FC = () => {
  const { accessToken } = useAuth();
  const [step, setStep] = useState(1);
  const [csvData, setCsvData] = useState<{ headers: string[]; rows: any[] }>({ headers: [], rows: [] });
  
  // Validation details
  const [errors, setErrors] = useState<RowError[]>([]);
  const [isValidated, setIsValidated] = useState(false);
  const [isImporting, setIsImporting] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      parseAndSetCSV(text);
      setStep(2);
    };
    reader.readAsText(file);
  };

  const parseAndSetCSV = (text: string) => {
    const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length === 0) return;
    
    const rawHeaders = lines[0].split(',');
    const headers = rawHeaders.map(h => h.trim().toLowerCase());
    
    const rows = lines.slice(1).map(line => {
      const vals = line.split(',');
      const obj: any = {};
      headers.forEach((h, idx) => {
        obj[h] = vals[idx] ? vals[idx].trim() : '';
      });
      return obj;
    });

    setCsvData({ headers: rawHeaders.map(h => h.trim()), rows });
    validateRows(rows, headers);
  };

  const validateRows = (rows: any[], headers: string[]) => {
    const tempErrors: RowError[] = [];
    const emailsSeen = new Set<string>();

    // 1. Check required headers
    const required = ['first_name', 'last_name', 'email'];
    required.forEach(req => {
      if (!headers.includes(req)) {
        tempErrors.push({ index: 0, field: 'Header', message: `Missing required header: "${req}"` });
      }
    });

    if (tempErrors.length > 0) {
      setErrors(tempErrors);
      setIsValidated(true);
      return;
    }

    // 2. Validate row fields
    rows.forEach((row, idx) => {
      const lineNum = idx + 2; // 1-indexed plus header row
      
      if (!row.first_name) {
        tempErrors.push({ index: lineNum, field: 'first_name', message: 'First name is required' });
      }
      if (!row.last_name) {
        tempErrors.push({ index: lineNum, field: 'last_name', message: 'Last name is required' });
      }
      
      if (!row.email) {
        tempErrors.push({ index: lineNum, field: 'email', message: 'Email address is required' });
      } else {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(row.email)) {
          tempErrors.push({ index: lineNum, field: 'email', message: 'Invalid email address format' });
        }
        if (emailsSeen.has(row.email)) {
          tempErrors.push({ index: lineNum, field: 'email', message: 'Duplicate email detected in CSV' });
        }
        emailsSeen.add(row.email);
      }
    });

    setErrors(tempErrors);
    setIsValidated(true);
  };

  const handleImportSubmit = async () => {
    if (errors.length > 0) return;
    setIsImporting(true);
    
    // Commit rows to backend (sequentially/batch creations)
    try {
      for (const row of csvData.rows) {
        await fetch('/api/v1/employees', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({
            first_name: row.first_name || '',
            last_name: row.last_name || '',
            email: row.email || '',
            phone: row.phone || undefined,
            status: 'PROBATION',
            employment_type: 'FULL_TIME',
            location: row.location || undefined,
          })
        });
      }
      setStep(3);
    } catch (e) {
      console.error(e);
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Wizard Steps indicator bar */}
      <div className="flex justify-between items-center bg-card border border-border p-4 rounded-xl text-xs font-semibold text-muted-foreground mb-6">
        <span className={step === 1 ? 'text-blue-500 font-bold' : ''}>1. Upload File</span>
        <ArrowRight size={14} />
        <span className={step === 2 ? 'text-blue-500 font-bold' : ''}>2. Preview & Validate</span>
        <ArrowRight size={14} />
        <span className={step === 3 ? 'text-blue-500 font-bold' : ''}>3. Success</span>
      </div>

      {step === 1 && (
        <div className="glass-card rounded-2xl border border-neutral-800 p-12 text-center flex flex-col items-center">
          <Upload size={48} className="text-muted-foreground mb-4" />
          <h2 className="text-lg font-bold text-white mb-2">Upload CSV Directory</h2>
          <p className="text-xs text-muted-foreground max-w-sm mb-8">
            Upload a CSV file containing columns: <code className="text-white font-mono bg-neutral-900 px-1 py-0.5 rounded">first_name</code>, <code className="text-white font-mono bg-neutral-900 px-1 py-0.5 rounded">last_name</code>, and <code className="text-white font-mono bg-neutral-900 px-1 py-0.5 rounded">email</code>.
          </p>
          
          <label className="px-5 py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-bold cursor-pointer transition">
            Select CSV File
            <input type="file" accept=".csv" className="hidden" onChange={handleFileSelect} />
          </label>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6">
          {/* Validation Alert */}
          {isValidated && errors.length > 0 ? (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-start space-x-2 text-xs text-red-400">
              <AlertTriangle size={18} className="shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-white">CSV contains validation errors</h4>
                <ul className="list-disc pl-4 mt-2 space-y-1">
                  {errors.slice(0, 5).map((err, idx) => (
                    <li key={idx}>Line {err.index} ({err.field}): {err.message}</li>
                  ))}
                  {errors.length > 5 && <li>And {errors.length - 5} more errors...</li>}
                </ul>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center space-x-2 text-xs text-emerald-400">
              <Check size={18} className="shrink-0" />
              <span className="font-semibold text-white">Validation passed. No errors found. Ready to import.</span>
            </div>
          )}

          {/* Table Preview */}
          <div className="glass-card rounded-2xl overflow-hidden border border-neutral-800">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider p-6 bg-secondary/40 border-b border-border">Data Preview ({csvData.rows.length} rows)</h3>
            <div className="overflow-auto max-h-[300px]">
              <table className="w-full text-left text-xs">
                <thead className="bg-neutral-900 text-muted-foreground border-b border-border font-semibold">
                  <tr>
                    {csvData.headers.map((h, i) => <th key={i} className="px-6 py-3 capitalize">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/40 text-white">
                  {csvData.rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-secondary/10">
                      {csvData.headers.map((h, i) => (
                        <td key={i} className="px-6 py-3">{row[h.toLowerCase()]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Footer Action buttons */}
          <div className="flex space-x-4">
            <button 
              onClick={() => setStep(1)}
              className="w-1/2 py-3 bg-secondary text-white hover:bg-neutral-850 rounded-lg text-xs font-semibold border border-border flex items-center justify-center transition"
            >
              <ArrowLeft size={14} className="mr-2" />
              Upload different file
            </button>
            <button 
              onClick={handleImportSubmit}
              disabled={errors.length > 0 || isImporting}
              className="w-1/2 py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-bold flex items-center justify-center transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isImporting ? 'Importing...' : 'Confirm & Import'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="glass-card rounded-2xl border border-neutral-800 p-12 text-center flex flex-col items-center">
          <div className="w-12 h-12 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 flex items-center justify-center mb-4">
            <Check size={24} />
          </div>
          <h2 className="text-lg font-bold text-white mb-2">Import Successful</h2>
          <p className="text-xs text-muted-foreground max-w-sm mb-8">
            All employee profiles have been created and mapped to the active directory workspace.
          </p>
          
          <Link
            to="/dashboard/hcm"
            className="px-5 py-3 bg-white text-black hover:bg-neutral-200 rounded-lg text-xs font-bold transition"
          >
            Go to Directory
          </Link>
        </div>
      )}
    </div>
  );
};
