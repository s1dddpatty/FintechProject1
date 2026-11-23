'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  UploadCloud, CheckCircle2, AlertCircle, FileText, Download, 
  Sparkles, Activity, ShieldCheck, Database, FileSpreadsheet,
  ArrowRight, Check, Copy, RefreshCw, Cpu, Layers, BarChart3,
  User, Building2, FileCheck2, TrendingUp, Filter
} from 'lucide-react';
import axios from 'axios';
import useSWR from 'swr';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

type DomainKey = 'all' | 'borrower' | 'bureau' | 'facility' | 'solvency';

export default function DataPipelinePage() {
  const { data: llmStatus } = useSWR('http://localhost:8000/pipeline/llm-status', fetcher);

  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [activeDomainTab, setActiveDomainTab] = useState<DomainKey>('all');
  const [showRawMemo, setShowRawMemo] = useState(false);

  const handleProcess = async () => {
    if (!file) return;
    setIsProcessing(true);
    setResult(null);
    setCopied(false);
    setActiveDomainTab('all');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/pipeline/clean-and-engineer', formData, {
        timeout: 120000 // 2 minutes for large datasets
      });
      setResult(res.data);
    } catch (e: any) {
      const errMsg = e.response?.data?.detail 
        || (e.code === 'ERR_NETWORK' || !e.response ? 'Backend server unreachable at http://localhost:8000. Please ensure the backend server is running.' : e.message)
        || 'Pipeline processing failed';
      alert(errMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownloadClean = () => {
    if (!result?.session_id) return;
    window.open(`http://localhost:8000/pipeline/download-clean/${result.session_id}`, '_blank');
  };

  const handleCopyMemo = () => {
    if (!result?.llm_audit?.audit_memo) return;
    navigator.clipboard.writeText(result.llm_audit.audit_memo);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 relative">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center">
            <Sparkles className="w-8 h-8 mr-3 text-primary" />
            Data Pipeline & Autonomous LLM Audit
          </h1>
          <p className="text-muted-foreground mt-1">
            Universal self-healing ingestion, 4-domain canonical architecture (3 Entities + 1 Stream), and Basel III audit reporting
          </p>
        </div>

        {/* Ollama Engine Status Badge */}
        <div className="flex items-center space-x-2 bg-muted/40 px-3 py-1.5 rounded-lg border text-xs">
          <Cpu className="w-4 h-4 text-primary" />
          <span>LLM Engine:</span>
          {llmStatus?.available ? (
            <span className="text-emerald-400 font-semibold flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
              Ollama Active ({llmStatus.active_model})
            </span>
          ) : (
            <span className="text-amber-400 font-medium flex items-center" title="Run 'ollama run llama3.2' for full generative mode">
              <span className="w-2 h-2 rounded-full bg-amber-500 mr-1.5" />
              Autonomous Engine (Ollama Offline)
            </span>
          )}
        </div>
      </div>

      {/* Upload State */}
      {!result && !isProcessing && (
        <Card className="border-dashed border-2">
          <CardContent className="pt-6 flex flex-col items-center justify-center p-16 text-center">
            <UploadCloud className="w-16 h-16 text-muted-foreground mb-6" />
            <h2 className="text-2xl font-bold mb-2">Ingest Any Loan Dataset (CSV)</h2>
            <p className="text-muted-foreground mb-8 max-w-xl">
              Upload any raw, unformatted, or dirty loan portfolio. The universal cleaner normalizes column variations, eliminates string artifacts ($, %, commas), synthesizes advanced financial ratios, and standardizes the output strictly into the <strong>3 Entities + 1 Solvency Stream</strong> canonical architecture.
            </p>
            
            <div className="flex flex-col space-y-4 w-full max-w-sm">
              <label className="border-2 border-dashed border-border rounded-xl p-8 w-full text-center flex flex-col items-center hover:bg-muted/50 cursor-pointer transition-colors">
                <FileSpreadsheet className="w-12 h-12 text-muted-foreground mb-4" />
                <span className="text-sm font-medium">
                  {file ? file.name : "Click to select any CSV file"}
                </span>
                <span className="text-xs text-muted-foreground mt-1">Accepts raw Kaggle, LendingClub, or bank exports</span>
                <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
              </label>

              <Button onClick={handleProcess} disabled={isProcessing || !file} className="w-full h-12 text-base font-semibold shadow-md">
                <Sparkles className="w-4 h-4 mr-2" /> Clean & Enforce Canonical Schema
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Processing State */}
      {isProcessing && (
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center p-16 space-y-4">
            <Activity className="w-12 h-12 text-primary animate-pulse" />
            <h2 className="text-xl font-bold">Executing Universal Data Pipeline...</h2>
            <div className="w-full max-w-md space-y-2 text-sm text-muted-foreground">
              <div className="flex justify-between items-center"><span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" /> Normalizing schema & column aliases</span><span>Done</span></div>
              <div className="flex justify-between items-center"><span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" /> Sanitizing currency, term, & percent strings</span><span>Done</span></div>
              <div className="flex justify-between items-center"><span className="flex items-center"><Activity className="w-4 h-4 mr-2 text-primary animate-spin" /> Synthesizing financial ratios (FICO, PTI, Ordinals)</span><span>Running</span></div>
              <div className="flex justify-between items-center opacity-70"><span className="flex items-center"><Layers className="w-4 h-4 mr-2 text-emerald-400" /> Partitioning into 3 Entities + 1 Solvency Stream</span><span>Waiting</span></div>
              <div className="flex justify-between items-center opacity-50"><span className="flex items-center"><Sparkles className="w-4 h-4 mr-2" /> Generating LLM Audit Memorandum</span><span>Waiting</span></div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-500">
          
          {/* Executive Action Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-muted/20 p-5 rounded-xl border shadow-sm">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                <span>Refinement Complete ({result.processing_time_seconds}s)</span>
              </div>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full font-mono">
                {result.telemetry.cleaned_rows.toLocaleString()} Records Output (Strictly 21 Canonical Features)
              </span>
              <span className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                result.data_quality_score >= 90 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}>
                Quality Score: {result.data_quality_score}/100
              </span>
            </div>

            <div className="flex items-center space-x-3 w-full sm:w-auto">
              <Button 
                onClick={handleDownloadClean} 
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md text-sm font-semibold"
              >
                <Download className="w-4 h-4 mr-2" /> Download Cleaned Dataset (21 Columns)
              </Button>
              <Button onClick={() => setResult(null)} variant="outline" size="sm">
                <RefreshCw className="w-3.5 h-3.5 mr-1" /> Ingest Another
              </Button>
            </div>
          </div>

          {/* 4 Architectural Domain Cards: 3 Entities + 1 Stream */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center">
                <Layers className="w-4 h-4 mr-2 text-primary" />
                Canonical Enterprise Architecture (3 Entities + 1 Solvency Stream)
              </h3>
              <span className="text-xs text-muted-foreground font-mono">20 Engineered & Underwriting Features + 1 ID</span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              
              {/* Domain 1: Individual / Borrower Profile */}
              <Card className="border-blue-500/20 bg-blue-500/5 hover:border-blue-500/40 transition-colors">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center">
                      <User className="w-3.5 h-3.5 mr-1.5" /> Entity 1
                    </span>
                    <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full font-mono">
                      4 Features
                    </span>
                  </div>
                  <CardTitle className="text-base text-foreground mt-1">Borrower Profile</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-1 text-xs text-muted-foreground space-y-2">
                  <p>Individual earning capacity, employment tenure, and geographic residence.</p>
                  <div className="flex flex-wrap gap-1 font-mono text-[11px] text-blue-300">
                    <span className="bg-blue-500/10 px-1.5 py-0.5 rounded">annual_inc</span>
                    <span className="bg-blue-500/10 px-1.5 py-0.5 rounded">emp_length</span>
                    <span className="bg-blue-500/10 px-1.5 py-0.5 rounded">home_ownership</span>
                    <span className="bg-blue-500/10 px-1.5 py-0.5 rounded">addr_state</span>
                  </div>
                </CardContent>
              </Card>

              {/* Domain 2: Credit Bureau Profile */}
              <Card className="border-amber-500/20 bg-amber-500/5 hover:border-amber-500/40 transition-colors">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center">
                      <Building2 className="w-3.5 h-3.5 mr-1.5" /> Entity 2
                    </span>
                    <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full font-mono">
                      6 Features
                    </span>
                  </div>
                  <CardTitle className="text-base text-foreground mt-1">Credit Bureau Profile</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-1 text-xs text-muted-foreground space-y-2">
                  <p>External bureau credit score midpoint, range bounds, DTI, and credit line age.</p>
                  <div className="flex flex-wrap gap-1 font-mono text-[11px] text-amber-300">
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">fico_score</span>
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">fico_low</span>
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">fico_high</span>
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">dti</span>
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">revol_util</span>
                    <span className="bg-amber-500/10 px-1.5 py-0.5 rounded">credit_months</span>
                  </div>
                </CardContent>
              </Card>

              {/* Domain 3: Loan Facility / Agreement */}
              <Card className="border-purple-500/20 bg-purple-500/5 hover:border-purple-500/40 transition-colors">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center">
                      <FileCheck2 className="w-3.5 h-3.5 mr-1.5" /> Entity 3
                    </span>
                    <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-mono">
                      7 Features
                    </span>
                  </div>
                  <CardTitle className="text-base text-foreground mt-1">Loan Facility Agreement</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-1 text-xs text-muted-foreground space-y-2">
                  <p>Contractual terms: principal size, amortized tenor, APR, installment, and grade.</p>
                  <div className="flex flex-wrap gap-1 font-mono text-[11px] text-purple-300">
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">loan_amnt</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">term</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">int_rate</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">installment</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">grade</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">ordinal</span>
                    <span className="bg-purple-500/10 px-1.5 py-0.5 rounded">purpose</span>
                  </div>
                </CardContent>
              </Card>

              {/* Domain 4: Solvency & Performance Stream */}
              <Card className="border-emerald-500/20 bg-emerald-500/5 hover:border-emerald-500/40 transition-colors">
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                      <TrendingUp className="w-3.5 h-3.5 mr-1.5" /> Stream 1
                    </span>
                    <span className="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full font-mono">
                      3 Features
                    </span>
                  </div>
                  <CardTitle className="text-base text-foreground mt-1">Solvency & Repayment</CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-1 text-xs text-muted-foreground space-y-2">
                  <p>Dynamic cash flow debt burden (PTI), capital leverage (LTI), and repayment state.</p>
                  <div className="flex flex-wrap gap-1 font-mono text-[11px] text-emerald-300">
                    <span className="bg-emerald-500/10 px-1.5 py-0.5 rounded">installment_to_income</span>
                    <span className="bg-emerald-500/10 px-1.5 py-0.5 rounded">loan_to_income</span>
                    <span className="bg-emerald-500/10 px-1.5 py-0.5 rounded">loan_status</span>
                  </div>
                </CardContent>
              </Card>

            </div>
          </div>

          {/* Main 2-Column Section: Telemetry vs AI Audit Memo */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Left Column: Data Engineering Telemetry */}
            <div className="space-y-6">
              
              {/* Newly Engineered Features Card */}
              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-base flex items-center">
                    <Sparkles className="w-4 h-4 mr-2 text-primary" />
                    Synthesized Financial Risk Features
                  </CardTitle>
                  <CardDescription>Advanced econometric ratios synthesized for nonlinear tree splits</CardDescription>
                </CardHeader>
                <CardContent className="pt-4 space-y-3">
                  {Object.entries(result.telemetry.engineered_features).map(([feat, desc]: [string, any]) => (
                    <div key={feat} className="p-3 bg-muted/40 rounded-lg border text-xs space-y-1">
                      <div className="font-mono font-bold text-foreground flex items-center">
                        <span className="w-2 h-2 rounded-full bg-primary mr-2" />
                        {feat}
                      </div>
                      <p className="text-muted-foreground">{desc}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Schema Normalization & Type Cleaning Card */}
              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-base flex items-center">
                    <Layers className="w-4 h-4 mr-2 text-primary" />
                    Schema Normalization & Self-Healing Log
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-4 text-xs">
                  <div>
                    <h4 className="font-semibold text-muted-foreground uppercase mb-2">Auto-Mapped Column Aliases</h4>
                    {Object.keys(result.telemetry.mapped_aliases).length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(result.telemetry.mapped_aliases).map(([orig, canon]: [string, any]) => (
                          <span key={orig} className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-1 rounded font-mono">
                            {orig} → {canon}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <div className="text-muted-foreground">Input columns conformed natively to canonical definitions.</div>
                    )}
                  </div>

                  <div>
                    <h4 className="font-semibold text-muted-foreground uppercase mb-2">Domain-Aware Imputations</h4>
                    {result.telemetry.imputed_features.length > 0 ? (
                      <div className="space-y-1">
                        {result.telemetry.imputed_features.map((item: string, i: number) => (
                          <div key={i} className="text-amber-400 font-mono bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                            {item}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-emerald-400 flex items-center">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Zero structural missingness detected.
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

            </div>

            {/* Right Column: AI Transformation Audit Memorandum */}
            <Card className="border shadow-lg flex flex-col">
              <CardHeader className="border-b bg-muted/30 pb-4 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center">
                    <ShieldCheck className="w-4 h-4 mr-2 text-primary" />
                    Executive Transformation Audit Memorandum
                  </CardTitle>
                  <CardDescription>
                    Generated by: <span className="text-foreground font-mono font-medium">{result.llm_audit.engine}</span>
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    size="sm" 
                    variant="ghost" 
                    onClick={() => setShowRawMemo(!showRawMemo)} 
                    className="text-xs h-8 text-muted-foreground"
                  >
                    {showRawMemo ? "Styled View" : "Raw Markdown"}
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleCopyMemo} className="text-xs h-8">
                    {copied ? <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                    {copied ? "Copied" : "Copy Memo"}
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="pt-5 flex-1 overflow-y-auto max-h-[600px] text-xs leading-relaxed space-y-4">
                {showRawMemo ? (
                  <div className="p-4 bg-muted/20 border rounded-xl font-mono text-[11px] whitespace-pre-wrap leading-relaxed text-muted-foreground">
                    {result.llm_audit.audit_memo}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Header Banner */}
                    <div className="p-4 rounded-xl border bg-muted/30 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-foreground text-sm flex items-center">
                          📋 Basel III / SR 11-7 Transformation Audit
                        </span>
                        <span className={`px-2.5 py-1 rounded-full font-bold text-[11px] border ${
                          result.data_quality_score >= 90
                            ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                            : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        }`}>
                          {result.data_quality_score >= 90 ? "INVESTMENT GRADE" : "CONDITIONALLY APPROVED"}
                        </span>
                      </div>
                      <p className="text-muted-foreground text-[11px]">
                        Governed by Basel Committee on Banking Supervision (BCBS 239) & SR 11-7 Model Risk Management Standards.
                      </p>
                    </div>

                    {/* Formatted Text Box */}
                    <div className="p-4 bg-muted/10 border rounded-xl font-sans text-xs leading-relaxed text-muted-foreground whitespace-pre-line space-y-3">
                      {result.llm_audit.audit_memo
                        .split('\n\n')
                        .filter((para: string) => !para.startsWith('### 📋') && !para.startsWith('**Audit Standard:**'))
                        .map((para: string, idx: number) => {
                          if (para.startsWith('####')) {
                            return (
                              <h4 key={idx} className="text-foreground font-bold text-xs pt-2 border-t border-border/50 flex items-center">
                                <span className="w-1.5 h-1.5 rounded-full bg-primary mr-2" />
                                {para.replace(/####\s*/, '')}
                              </h4>
                            );
                          }
                          return (
                            <p key={idx} className="leading-relaxed">
                              {para.replace(/\*\*/g, '')}
                            </p>
                          );
                        })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

          </div>

          {/* Bottom Section: Clean Dataset Preview Ledger */}
          <Card className="border shadow-md">
            <CardHeader className="border-b bg-muted/20 pb-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <CardTitle className="text-base flex items-center">
                    <Database className="w-4 h-4 mr-2 text-primary" />
                    Refined Model-Ready Dataset Preview (First 50 Records)
                  </CardTitle>
                  <CardDescription>
                    All strings sanitized, missing values filled, and engineered ratios attached
                  </CardDescription>
                </div>

                {/* Domain Filter Tabs */}
                <div className="flex flex-wrap items-center gap-1.5 bg-muted/40 p-1 rounded-lg border text-xs">
                  <span className="text-[11px] text-muted-foreground px-2 flex items-center">
                    <Filter className="w-3 h-3 mr-1" /> View:
                  </span>
                  <button
                    onClick={() => setActiveDomainTab('all')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                      activeDomainTab === 'all' 
                        ? 'bg-primary text-primary-foreground shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    All Features (21)
                  </button>
                  <button
                    onClick={() => setActiveDomainTab('borrower')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                      activeDomainTab === 'borrower' 
                        ? 'bg-blue-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    👤 Borrower (4)
                  </button>
                  <button
                    onClick={() => setActiveDomainTab('bureau')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                      activeDomainTab === 'bureau' 
                        ? 'bg-amber-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    🏛️ Bureau (6)
                  </button>
                  <button
                    onClick={() => setActiveDomainTab('facility')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                      activeDomainTab === 'facility' 
                        ? 'bg-purple-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    📜 Facility (7)
                  </button>
                  <button
                    onClick={() => setActiveDomainTab('solvency')}
                    className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                      activeDomainTab === 'solvency' 
                        ? 'bg-emerald-600 text-white shadow-sm' 
                        : 'text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    📈 Solvency (3)
                  </button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div className="overflow-x-auto max-h-[460px]">
                <table className="w-full text-xs text-left">
                  <thead className="bg-muted/70 text-muted-foreground font-semibold sticky top-0 backdrop-blur-md z-10 border-b">
                    <tr>
                      <th className="p-3 sticky left-0 bg-muted/90 z-20">Loan ID</th>

                      {/* Domain 1: Borrower Profile */}
                      {(activeDomainTab === 'all' || activeDomainTab === 'borrower') && (
                        <>
                          <th className="p-3 bg-blue-500/5 text-blue-300">
                            <div>Annual Income</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">annual_inc</div>
                          </th>
                          <th className="p-3 bg-blue-500/5 text-blue-300">
                            <div>Emp Length</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">emp_length</div>
                          </th>
                          <th className="p-3 bg-blue-500/5 text-blue-300">
                            <div>Home Ownership</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">home_ownership</div>
                          </th>
                          <th className="p-3 bg-blue-500/5 text-blue-300">
                            <div>State</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">addr_state</div>
                          </th>
                        </>
                      )}

                      {/* Domain 2: Credit Bureau Profile */}
                      {(activeDomainTab === 'all' || activeDomainTab === 'bureau') && (
                        <>
                          <th className="p-3 bg-amber-500/5 text-amber-300">
                            <div>FICO Score</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">fico_score</div>
                          </th>
                          <th className="p-3 bg-amber-500/5 text-amber-300">
                            <div>FICO Bounds</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">range_low / high</div>
                          </th>
                          <th className="p-3 bg-amber-500/5 text-amber-300">
                            <div>DTI Ratio</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">dti</div>
                          </th>
                          <th className="p-3 bg-amber-500/5 text-amber-300">
                            <div>Revol Util</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">revol_util</div>
                          </th>
                          <th className="p-3 bg-amber-500/5 text-amber-300">
                            <div>Credit History</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">history_months</div>
                          </th>
                        </>
                      )}

                      {/* Domain 3: Loan Facility */}
                      {(activeDomainTab === 'all' || activeDomainTab === 'facility') && (
                        <>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>Loan Amount</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">loan_amnt</div>
                          </th>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>Term</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">term</div>
                          </th>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>APR</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">int_rate</div>
                          </th>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>Monthly Installment</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">installment</div>
                          </th>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>Risk Grade</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">grade (ordinal)</div>
                          </th>
                          <th className="p-3 bg-purple-500/5 text-purple-300">
                            <div>Purpose</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">purpose</div>
                          </th>
                        </>
                      )}

                      {/* Domain 4: Solvency & Repayment Stream */}
                      {(activeDomainTab === 'all' || activeDomainTab === 'solvency') && (
                        <>
                          <th className="p-3 bg-emerald-500/5 text-emerald-300">
                            <div>PTI Debt Burden</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">installment_to_income</div>
                          </th>
                          <th className="p-3 bg-emerald-500/5 text-emerald-300">
                            <div>Loan / Income (LTI)</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">loan_to_income</div>
                          </th>
                          <th className="p-3 bg-emerald-500/5 text-emerald-300">
                            <div>Loan Trajectory</div>
                            <div className="text-[10px] font-normal font-mono opacity-70">loan_status</div>
                          </th>
                        </>
                      )}
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-border font-mono text-xs">
                    {result.preview_records.map((row: any, idx: number) => (
                      <tr key={idx} className="hover:bg-muted/40 transition-colors">
                        
                        {/* ID */}
                        <td className="p-3 font-bold text-foreground sticky left-0 bg-background/95 z-10 border-r">
                          {row.id || `LNC-${1000000 + idx}`}
                        </td>

                        {/* Domain 1: Borrower Profile */}
                        {(activeDomainTab === 'all' || activeDomainTab === 'borrower') && (
                          <>
                            <td className="p-3 text-foreground font-semibold">
                              ${Number(row.annual_inc || 0).toLocaleString()}
                            </td>
                            <td className="p-3 text-muted-foreground">
                              {Number(row.emp_length || 0).toFixed(0)} yrs
                            </td>
                            <td className="p-3">
                              <span className="bg-muted px-2 py-0.5 rounded text-[11px] text-foreground">
                                {row.home_ownership || 'RENT'}
                              </span>
                            </td>
                            <td className="p-3 text-muted-foreground font-semibold">
                              {row.addr_state || 'US'}
                            </td>
                          </>
                        )}

                        {/* Domain 2: Credit Bureau Profile */}
                        {(activeDomainTab === 'all' || activeDomainTab === 'bureau') && (
                          <>
                            <td className="p-3 font-bold text-primary">
                              {row.fico_score || 'N/A'}
                            </td>
                            <td className="p-3 text-muted-foreground text-[11px]">
                              {row.fico_range_low}-{row.fico_range_high}
                            </td>
                            <td className="p-3 text-foreground">
                              {Number(row.dti || 0).toFixed(1)}%
                            </td>
                            <td className="p-3 text-foreground">
                              {Number(row.revol_util || 0).toFixed(1)}%
                            </td>
                            <td className="p-3 text-muted-foreground">
                              {row.credit_history_months} mo
                            </td>
                          </>
                        )}

                        {/* Domain 3: Loan Facility */}
                        {(activeDomainTab === 'all' || activeDomainTab === 'facility') && (
                          <>
                            <td className="p-3 font-semibold text-foreground">
                              ${Number(row.loan_amnt || 0).toLocaleString()}
                            </td>
                            <td className="p-3 text-muted-foreground">
                              {row.term} mo
                            </td>
                            <td className="p-3 text-foreground">
                              {Number(row.int_rate || 0).toFixed(2)}%
                            </td>
                            <td className="p-3 text-foreground">
                              ${Number(row.installment || 0).toFixed(2)}
                            </td>
                            <td className="p-3">
                              <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2 py-0.5 rounded font-bold">
                                {row.grade || 'C'} ({row.grade_ordinal || 3})
                              </span>
                            </td>
                            <td className="p-3 text-muted-foreground text-[11px] capitalize truncate max-w-[120px]" title={row.purpose}>
                              {row.purpose || 'other'}
                            </td>
                          </>
                        )}

                        {/* Domain 4: Solvency & Repayment Stream */}
                        {(activeDomainTab === 'all' || activeDomainTab === 'solvency') && (
                          <>
                            <td className="p-3 font-semibold text-emerald-400">
                              {(Number(row.installment_to_income || 0) * 100).toFixed(2)}%
                            </td>
                            <td className="p-3 text-foreground font-semibold">
                              {(Number(row.loan_to_income || 0)).toFixed(2)}x
                            </td>
                            <td className="p-3">
                              <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                                row.loan_status === 'Fully Paid'
                                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                                  : row.loan_status === 'Charged Off'
                                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                                  : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                              }`}>
                                {row.loan_status || 'UNSCORED'}
                              </span>
                            </td>
                          </>
                        )}

                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Table Footer */}
              <div className="p-3 border-t bg-muted/10 text-xs text-muted-foreground flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <span>Displaying 50 preview samples from {result.telemetry.cleaned_rows.toLocaleString()} total refined records</span>
                <Button size="sm" variant="ghost" onClick={handleDownloadClean} className="text-xs h-7 text-primary hover:text-primary">
                  <Download className="w-3.5 h-3.5 mr-1" /> Download Full Cleaned Dataset (21 Features)
                </Button>
              </div>
            </CardContent>
          </Card>

        </div>
      )}

    </div>
  );
}
