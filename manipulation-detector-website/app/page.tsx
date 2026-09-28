'use client';

import { useEffect, useRef, useState } from 'react';
import type { ChangeEvent, DragEvent } from 'react';

type CsvOverview = { rows: number; columns: number };
type ModelStatus = 'checking' | 'connected' | 'disconnected';
type AnalysisState = 'idle' | 'running' | 'complete' | 'error';

function countCsvRecords(contents: string): CsvOverview {
  let quoted = false;
  let rows = 0;
  let columns = 0;
  let firstRecord = true;

  for (let index = 0; index < contents.length; index += 1) {
    const character = contents[index];
    if (character === '"') {
      if (quoted && contents[index + 1] === '"') index += 1;
      else quoted = !quoted;
    } else if (character === ',' && firstRecord && !quoted) {
      columns += 1;
    } else if (character === '\n' && !quoted) {
      if (firstRecord) {
        columns += 1;
        firstRecord = false;
      } else if (contents.slice(0, index).trim()) {
        rows += 1;
      }
    }
  }

  if (firstRecord && contents.trim()) columns += 1;
  if (!contents.endsWith('\n') && !quoted && !firstRecord) rows += 1;
  return { rows, columns };
}

function formatFileSize(bytes: number) {
  return bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function Home() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [overview, setOverview] = useState<CsvOverview | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus>('checking');
  const [analysisState, setAnalysisState] = useState<AnalysisState>('idle');
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    fetch('/api/predict')
      .then((response) => response.json())
      .then((data: { configured?: boolean }) => setModelStatus(data.configured ? 'connected' : 'disconnected'))
      .catch(() => setModelStatus('disconnected'));
  }, []);

  async function selectFile(selectedFile: File | undefined) {
    if (!selectedFile) return;
    if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
      setAnalysisState('error');
      setMessage('Choose a CSV file to continue.');
      return;
    }
    if (selectedFile.size > 25 * 1024 * 1024) {
      setAnalysisState('error');
      setMessage('This file is larger than the 25 MB upload limit.');
      return;
    }

    setFile(selectedFile);
    setOverview(countCsvRecords(await selectedFile.text()));
    setAnalysisState('idle');
    setMessage('');
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    void selectFile(event.target.files?.[0]);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    void selectFile(event.dataTransfer.files[0]);
  }

  async function loadSample() {
    const response = await fetch('/sample-conversations.csv');
    const sample = new File([await response.blob()], 'sample-conversations.csv', { type: 'text/csv' });
    await selectFile(sample);
  }

  async function analyzeFile() {
    if (!file || modelStatus !== 'connected') return;
    setAnalysisState('running');
    setMessage('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/predict', { method: 'POST', body: formData });
      const responseText = await response.text();
      let responseData: unknown = responseText;
      try {
        responseData = JSON.parse(responseText);
      } catch {
        // Keep plain-text model responses readable.
      }
      if (!response.ok) {
        const errorMessage = typeof responseData === 'object' && responseData !== null && 'error' in responseData
          ? String(responseData.error)
          : responseText || 'The model service returned an error.';
        throw new Error(errorMessage);
      }
      setMessage(typeof responseData === 'string' ? responseData : JSON.stringify(responseData, null, 2));
      setAnalysisState('complete');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'The analysis could not be completed.');
      setAnalysisState('error');
    }
  }

  const statusLabel = {
    checking: 'Checking model',
    connected: 'Model connected',
    disconnected: 'Model not connected',
  }[modelStatus];

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Signal home">
          <span className="brand-mark" aria-hidden="true"><span /><span /><span /></span>
          <span>signal<span className="brand-period">.</span></span>
        </a>
        <div className={`model-status model-status-${modelStatus}`} role="status">
          <span className="status-dot" />{statusLabel}
        </div>
      </header>

      <section className="hero-band" aria-labelledby="hero-title">
        <div className="hero-inner">
          <div className="intro">
            <div className="eyebrow"><span className="eyebrow-line" /> CONVERSATION ANALYSIS</div>
            <h1 id="hero-title">Find the <em>signal.</em></h1>
            <p>Conversation patterns, made visible.</p>
          </div>
          <div className="signal-art" aria-hidden="true">
            <div className="signal-art-label"><span>LIVE TRACE</span><span>01 / 03</span></div>
            <div className="signal-bars">
              <i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i />
            </div>
            <div className="signal-art-footer"><span>LANGUAGE PATTERNS</span><span className="signal-art-live"><span /> READY</span></div>
          </div>
        </div>
      </section>

      <div className="workspace" id="top">

        <section className="workbench" aria-label="Conversation analysis workspace">
          <div className="upload-column">
            <div className="section-heading">
              <div><h2>Dataset</h2></div>
              <span className="file-type">CSV · 25 MB MAX</span>
            </div>
            <div
              className={`dropzone${isDragging ? ' dropzone-active' : ''}${file ? ' dropzone-loaded' : ''}`}
              onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
              onDragOver={(event) => event.preventDefault()}
              onDragLeave={(event) => {
                if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setIsDragging(false);
              }}
              onDrop={handleDrop}
            >
              <input ref={fileInput} className="visually-hidden" type="file" accept=".csv,text/csv" onChange={handleFileChange} aria-label="Choose a CSV file" />
              {file ? (
                <>
                  <div className="file-badge" aria-hidden="true">CSV</div>
                  <div className="file-details">
                    <strong>{file.name}</strong>
                    <span>{formatFileSize(file.size)}{overview ? ` · ${overview.rows.toLocaleString()} records · ${overview.columns} columns` : ''}</span>
                  </div>
                  <button className="icon-button" type="button" onClick={() => fileInput.current?.click()} aria-label="Replace selected file" title="Replace file">
                    <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 4v12M4 10h12" /></svg>
                  </button>
                </>
              ) : (
                <>
                  <div className="upload-icon" aria-hidden="true"><svg viewBox="0 0 28 28"><path d="M14 19V5m0 0L8.5 10.5M14 5l5.5 5.5M5 17v5h18v-5" /></svg></div>
                  <div className="drop-copy">
                    <strong>Drop a CSV here</strong>
                    <span>or <button className="text-button" type="button" onClick={() => fileInput.current?.click()}>browse files</button></span>
                  </div>
                </>
              )}
            </div>

            {analysisState === 'error' && <p className="inline-error" role="alert">{message}</p>}
            <div className="run-row">
              <button className="analyze-button" type="button" onClick={analyzeFile} disabled={!file || modelStatus !== 'connected' || analysisState === 'running'}>
                {analysisState === 'running' ? 'Analyzing…' : 'Analyze data'}
                {analysisState !== 'running' && <span aria-hidden="true">↗</span>}
              </button>
            </div>

            {analysisState === 'complete' && (
              <section className="result-panel" aria-live="polite">
                <div className="result-heading"><span className="result-check">✓</span><h3>Analysis complete</h3></div>
                <pre>{message}</pre>
              </section>
            )}
          </div>

          <aside className="sample-column" aria-labelledby="sample-title">
            <div className="section-heading"><div><h2 id="sample-title">Sample data</h2></div><span className="sample-count">2 RECORDS</span></div>
            <div className="sample-file">
              <div className="sample-file-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M6 3.75h8l4 4v12.5H6zM14 4v4h4M9 12h6M9 15h6" /></svg></div>
              <div className="sample-file-copy"><strong>Conversation examples</strong><span>Manipulation + neutral · CSV</span></div>
              <a className="download-link" href="/sample-conversations.csv" download aria-label="Download sample conversations CSV" title="Download sample CSV">
                <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 3v10m0 0 4-4m-4 4L6 9M4 15v2h12v-2" /></svg>
              </a>
            </div>
            <button className="sample-button" type="button" onClick={loadSample}>Load sample into workspace <span aria-hidden="true">→</span></button>
          </aside>
        </section>

        {modelStatus === 'disconnected' && (
          <div className="connection-note" role="status">
            <span className="connection-icon" aria-hidden="true">!</span>
            <p><strong>Model not connected</strong><span> · Configure <code>MODEL_API_URL</code> to enable analysis.</span></p>
          </div>
        )}

        <footer className="page-footer">
          <span>Signal <span className="footer-divider">/</span> Conversation analysis</span>
          <span>For research use</span>
        </footer>
      </div>
    </main>
  );
}
