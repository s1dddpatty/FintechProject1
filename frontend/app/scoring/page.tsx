'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  UploadCloud, CheckCircle2, AlertCircle, FileText, Download, 
  Briefcase, Percent, Activity, Search, Filter, BarChart3, 
  ShieldAlert, Sparkles, X, ChevronRight, Check, Eye, Database, FileSpreadsheet,
  AlertTriangle, DollarSign, UserCheck, ShieldCheck
} from 'lucide-react';
import axios from 'axios';
import useSWR from 'swr';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

interface BorrowerRecord {
  id: string | number;
  loan_amnt: number | string;
  term?: string | number;
  int_rate: number | string;
  grade?: string;
  annual_inc: number | string;
  addr_state?: string;
  fico_range_low?: number | string;
  fico_range_high?: number | string;
  fico_score?: number | string;
  probability_of_default: number;
  risk_label: string;
  credit_decision?: string;
  expected_loss?: number;
  [key: string]: any;
}

export default function PortfolioScoringPage() {
  const { data: latestModel, error: modelError, isLoading: modelLoading } = useSWR('http://localhost:8000/ml/models/latest', fetcher);
  
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Forensic Ledger Filter & Drilldown State
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState<'ALL' | 'HIGH' | 'MED' | 'LOW'>('ALL');
  const [selectedBorrower, setSelectedBorrower] = useState<BorrowerRecord | null>(null);
  const [overrideStatus, setOverrideStatus] = useState<string | null>(null);

  const handleScore = async () => {
    if (!file) return;
    setIsProcessing(true);
    setResult(null);
    setSelectedBorrower(null);
    setOverrideStatus(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      console.log('Sending POST request to /ml/portfolio/score...');
      const res = await axios.post('http://localhost:8000/ml/portfolio/score', formData, {
        timeout: 120000 // 2 minutes for large datasets
      });
      console.log('Received response:', res.data);
      setResult(res.data);
    } catch (e: any) {
      const errMsg = e.response?.data?.detail 
        || (e.code === 'ERR_NETWORK' || !e.response ? 'Backend server unreachable at http://localhost:8000. Please ensure the backend server is running.' : e.message)
        || 'Scoring failed';
      alert(errMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!result?.session_id) return;
    window.open(`http://localhost:8000/ml/portfolio/download/${result.session_id}`, '_blank');
  };

  const handleDownloadTableau = () => {
    if (!result?.session_id) return;
    window.open(`http://localhost:8000/ml/portfolio/download-tableau/${result.session_id}`, '_blank');
  };

  // Filtered scored records for the Granular Forensic Ledger
  const filteredRecords = useMemo(() => {
    if (!result?.scored_records) return [];
    return (result.scored_records as BorrowerRecord[]).filter((record) => {
      // Risk filter
      if (riskFilter === 'HIGH' && record.risk_label !== 'High Risk') return false;
      if (riskFilter === 'MED' && record.risk_label !== 'Medium Risk') return false;
      if (riskFilter === 'LOW' && record.risk_label !== 'Low Risk') return false;

      // Text search (ID, Grade, State, Risk)
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      const idMatch = String(record.id || '').toLowerCase().includes(q);
      const gradeMatch = String(record.grade || '').toLowerCase().includes(q);
      const stateMatch = String(record.addr_state || '').toLowerCase().includes(q);
      const riskMatch = String(record.risk_label || '').toLowerCase().includes(q);
      return idMatch || gradeMatch || stateMatch || riskMatch;
    });
  }, [result, searchQuery, riskFilter]);

  if (modelLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading workspace...</div>;
  }

  if (modelError || !latestModel) {
    return (
      <div className="p-8 max-w-4xl mx-auto mt-16">
        <Card className="border-amber-500/50 bg-amber-500/5 shadow-md">
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center space-y-4">
            <AlertCircle className="w-12 h-12 text-amber-500" />
            <div className="space-y-1">
              <h2 className="text-xl font-bold">No Production Model Available</h2>
              <p className="text-muted-foreground">Please train a production model in the Model Development workspace before scoring a portfolio.</p>
            </div>
            <Button onClick={() => window.location.href='/development'}>Go to Model Development</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 relative">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Portfolio Scoring</h1>
        <p className="text-muted-foreground mt-1">Score new applications and generate business insights using the production model</p>
      </div>

      {!result && !isProcessing && (
        <Card className="border-dashed border-2">
          <CardContent className="pt-6 flex flex-col items-center justify-center p-16 text-center">
            <UploadCloud className="w-16 h-16 text-muted-foreground mb-6" />
            <h2 className="text-2xl font-bold mb-2">Upload Portfolio</h2>
            <p className="text-muted-foreground mb-8 max-w-md">Upload a CSV file containing new loan applications. The file will be processed using the active production model (v{latestModel.version}).</p>
            
            <div className="flex flex-col space-y-4 w-full max-w-sm">
              <label className="border-2 border-dashed border-border rounded-xl p-8 w-full text-center flex flex-col items-center hover:bg-muted/50 cursor-pointer transition-colors">
                <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
                <span className="text-sm font-medium">
                  {file ? file.name : "Click to select Portfolio CSV"}
                </span>
                <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
              </label>
              <Button onClick={handleScore} disabled={isProcessing || !file} className="w-full h-12 text-lg">
                {isProcessing ? "Processing..." : "Process Portfolio"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {isProcessing && (
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center p-16 space-y-4">
            <Activity className="w-12 h-12 text-primary animate-pulse" />
            <h2 className="text-xl font-bold">Processing Portfolio...</h2>
            <div className="w-full max-w-md space-y-2 text-sm text-muted-foreground">
              <div className="flex justify-between items-center"><span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" /> Uploading dataset</span><span>Done</span></div>
              <div className="flex justify-between items-center"><span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" /> Validating schema & auto-imputing</span><span>Done</span></div>
              <div className="flex justify-between items-center"><span className="flex items-center"><Activity className="w-4 h-4 mr-2 text-primary animate-spin" /> Preprocessing features</span><span>Running</span></div>
              <div className="flex justify-between items-center opacity-50"><span className="flex items-center"><FileText className="w-4 h-4 mr-2" /> Running inference & forensic ledger</span><span>Waiting</span></div>
            </div>
          </CardContent>
        </Card>
      )}

      {result && result.status === 'validation_failed' && (
        <Card className="border-rose-500/50 bg-rose-500/5 shadow-md animate-in fade-in duration-500">
          <CardHeader>
            <CardTitle className="text-rose-500 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" /> Dataset Validation Failed
            </CardTitle>
            <CardDescription>
              The uploaded dataset cannot be scored because it is missing critical features.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold mb-2">Missing Features</h4>
              <div className="flex flex-wrap gap-2">
                {result.dataset_intelligence.missing_required.map((col: string) => (
                  <span key={col} className="bg-rose-500 text-white text-xs px-2 py-1 rounded-md">{col}</span>
                ))}
              </div>
            </div>
            
            {Object.keys(result.dataset_intelligence.mapped_features).length > 0 && (
              <div>
                <h4 className="text-sm font-semibold mb-2">Automatically Mapped Features</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.dataset_intelligence.mapped_features).map(([orig, mapped]: [string, any]) => (
                    <span key={orig} className="bg-emerald-500/20 text-emerald-700 text-xs px-2 py-1 rounded-md border border-emerald-500/30">
                      {orig} → {mapped}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            <Button variant="outline" onClick={() => setResult(null)} className="w-full">
              Upload Different Dataset
            </Button>
          </CardContent>
        </Card>
      )}

      {result && result.status === 'success' && (
        <div className="space-y-8 animate-in fade-in duration-500">
          
          {/* Action Header with Multi-Export Capability */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-muted/20 p-4 rounded-xl border">
            <div className="flex items-center space-x-2 text-emerald-500 font-medium">
              <CheckCircle2 className="w-5 h-5" />
              <span>Scoring Complete ({result.processing_summary.processing_time_seconds}s)</span>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full ml-2">
                {result.processing_summary.processed_rows} Applications Evaluated
              </span>
            </div>
            <div className="flex items-center space-x-3 w-full sm:w-auto">
              <Button onClick={handleDownload} variant="outline" size="sm" className="shadow-sm">
                <Download className="w-4 h-4 mr-2" /> Scored CSV
              </Button>
              <Button onClick={handleDownloadTableau} variant="default" size="sm" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md">
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Export Tableau / PowerBI
              </Button>
              <Button onClick={() => setResult(null)} variant="ghost" size="sm">
                Upload New
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Column 1: Processing & Dataset Intelligence */}
            <div className="space-y-6">
              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-lg">Processing Summary</CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Uploaded Rows</span>
                    <span className="font-semibold">{result.processing_summary.uploaded_rows.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Processed Rows</span>
                    <span className="font-semibold text-emerald-500">{result.processing_summary.processed_rows.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Failed Rows</span>
                    <span className="font-semibold text-rose-500">{result.processing_summary.failed_rows}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t mt-2">
                    <span className="text-muted-foreground">Model Engine</span>
                    <span className="font-mono">{result.processing_summary.model_version} ({result.processing_summary.algorithm})</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-lg flex items-center justify-between">
                    <span>Dataset Intelligence</span>
                    <Sparkles className="w-4 h-4 text-primary" />
                  </CardTitle>
                  <CardDescription>Schema validation & self-healing ingestion</CardDescription>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  {/* Self Healing Auto Imputation Badge */}
                  {result.dataset_intelligence.auto_imputed_features && result.dataset_intelligence.auto_imputed_features.length > 0 ? (
                    <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs space-y-1">
                      <div className="font-semibold text-amber-400 flex items-center">
                        <Sparkles className="w-3.5 h-3.5 mr-1" /> Self-Healing Active: Imputed Missing Columns
                      </div>
                      <p className="text-muted-foreground">
                        Synthetic conservative domain defaults were automatically injected for:
                      </p>
                      <div className="flex flex-wrap gap-1 pt-1">
                        {result.dataset_intelligence.auto_imputed_features.map((col: string) => (
                          <span key={col} className="bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded text-[11px] font-mono">
                            {col}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  <div>
                    <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Detected Columns ({result.dataset_intelligence.columns_detected.length})</h4>
                    <div className="flex flex-wrap gap-1">
                      {result.dataset_intelligence.columns_detected.slice(0, 15).map((col: string) => (
                        <span key={col} className="bg-secondary text-secondary-foreground text-xs px-2 py-0.5 rounded-full">{col}</span>
                      ))}
                      {result.dataset_intelligence.columns_detected.length > 15 && <span className="text-xs text-muted-foreground py-0.5">+{result.dataset_intelligence.columns_detected.length - 15} more</span>}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Missing Value Check</h4>
                    {Object.entries(result.dataset_intelligence.missing_values || {})
                        .filter(([_, v]) => Number(v) > 0)
                        .length === 0 ? (
                      <div className="text-sm text-emerald-500 flex items-center"><CheckCircle2 className="w-4 h-4 mr-1" /> Zero raw missing values</div>
                    ) : (
                      <div className="text-sm text-amber-500 flex items-center"><AlertCircle className="w-4 h-4 mr-1" /> Imputation pipeline applied</div>
                    )}
                  </div>
                  {Object.keys(result.dataset_intelligence.mapped_features || {}).length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Auto-Mapped Aliases</h4>
                      <div className="text-xs text-muted-foreground">
                        {Object.keys(result.dataset_intelligence.mapped_features).length} column(s) normalized to enterprise schema.
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Column 2 & 3: Executive Analytics */}
            <div className="lg:col-span-2 space-y-6">
              
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <Card className="p-4 flex flex-col justify-center">
                  <div className="text-xs text-muted-foreground mb-1 flex items-center"><Briefcase className="w-3 h-3 mr-1" /> Requested Funding</div>
                  <div className="text-xl font-bold">${(result.executive_kpis.total_requested_funding / 1000000).toFixed(1)}M</div>
                </Card>
                <Card className="p-4 flex flex-col justify-center border-emerald-500/30">
                  <div className="text-xs text-muted-foreground mb-1 flex items-center text-emerald-500"><CheckCircle2 className="w-3 h-3 mr-1" /> Approval Rec.</div>
                  <div className="text-xl font-bold text-emerald-500">{(result.executive_kpis.recommended_approval_rate * 100).toFixed(1)}%</div>
                </Card>
                <Card className="p-4 flex flex-col justify-center border-rose-500/30">
                  <div className="text-xs text-muted-foreground mb-1 flex items-center text-rose-500"><AlertCircle className="w-3 h-3 mr-1" /> High Risk Apps</div>
                  <div className="text-xl font-bold text-rose-500">{result.executive_kpis.high_risk_applications.toLocaleString()}</div>
                </Card>
                <Card className="p-4 flex flex-col justify-center">
                  <div className="text-xs text-muted-foreground mb-1 flex items-center"><Percent className="w-3 h-3 mr-1" /> Average PD</div>
                  <div className="text-xl font-bold">{(result.executive_kpis.average_pd * 100).toFixed(2)}%</div>
                </Card>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Risk Category Distribution</CardTitle>
                  </CardHeader>
                  <CardContent className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Low Risk', value: result.charts.risk_distribution['Low Risk'] || 0 },
                            { name: 'Medium Risk', value: result.charts.risk_distribution['Medium Risk'] || 0 },
                            { name: 'High Risk', value: result.charts.risk_distribution['High Risk'] || 0 },
                          ]}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {COLORS.map((color, index) => (
                            <Cell key={`cell-${index}`} fill={color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(val: any) => Number(val).toLocaleString()} />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Probability of Default (PD) Spectrum</CardTitle>
                  </CardHeader>
                  <CardContent className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={Object.entries(result.charts.probability_distribution).map(([k, v]) => ({ name: k, count: v }))}>
                        <XAxis dataKey="name" fontSize={10} tickMargin={10} />
                        <Tooltip />
                        <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-lg">Executive Decision Recommendations</CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  <div className="text-sm">
                    <strong>Portfolio Composition:</strong> {result.business_insights.portfolio_composition}
                  </div>
                  <div className="text-sm">
                    <strong>Underwriting Recommendation:</strong> {result.business_insights.approval_recommendation}
                  </div>
                  {Object.keys(result.business_insights.highest_risk_grades || {}).length > 0 && (
                    <div className="text-sm">
                      <strong>Highest Risk Segments (By Sub-Grade):</strong>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {Object.entries(result.business_insights.highest_risk_grades).map(([grade, pd]: [string, any]) => (
                          <div key={grade} className="bg-rose-500/10 text-rose-400 px-3 py-1 rounded-md border border-rose-500/20 text-xs">
                            Grade {grade}: {(Number(pd) * 100).toFixed(1)}% PD
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

            </div>
          </div>

          {/* Granular Borrower Forensic Table & Filtering */}
          <Card className="border shadow-lg">
            <CardHeader className="border-b bg-muted/20 pb-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <CardTitle className="text-xl flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-primary" />
                    Granular Borrower Forensic Ledger
                  </CardTitle>
                  <CardDescription>
                    Applicant-level risk predictions with real-time probability of default (PD) and expected loss forensics
                  </CardDescription>
                </div>
                
                {/* Search & Filter Controls */}
                <div className="flex flex-wrap items-center gap-2">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                    <input 
                      type="text"
                      placeholder="Search ID, Grade, State..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 pr-3 py-1.5 text-xs bg-background border rounded-lg focus:outline-none focus:ring-1 focus:ring-primary w-48 sm:w-56"
                    />
                  </div>

                  <div className="flex border rounded-lg overflow-hidden bg-background">
                    <button
                      onClick={() => setRiskFilter('ALL')}
                      className={`px-3 py-1.5 text-xs font-medium transition-colors ${riskFilter === 'ALL' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}
                    >
                      All ({result.scored_records?.length || 0})
                    </button>
                    <button
                      onClick={() => setRiskFilter('LOW')}
                      className={`px-3 py-1.5 text-xs font-medium transition-colors ${riskFilter === 'LOW' ? 'bg-emerald-600 text-white' : 'text-muted-foreground hover:bg-muted'}`}
                    >
                      Low Risk ({result.executive_kpis.low_risk_applications || 0})
                    </button>
                    <button
                      onClick={() => setRiskFilter('MED')}
                      className={`px-3 py-1.5 text-xs font-medium transition-colors ${riskFilter === 'MED' ? 'bg-amber-600 text-white' : 'text-muted-foreground hover:bg-muted'}`}
                    >
                      Med Risk ({result.executive_kpis.medium_risk_applications || 0})
                    </button>
                    <button
                      onClick={() => setRiskFilter('HIGH')}
                      className={`px-3 py-1.5 text-xs font-medium transition-colors ${riskFilter === 'HIGH' ? 'bg-rose-600 text-white' : 'text-muted-foreground hover:bg-muted'}`}
                    >
                      High Risk ({result.executive_kpis.high_risk_applications || 0})
                    </button>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto max-h-[500px]">
                <table className="w-full text-xs text-left">
                  <thead className="bg-muted/50 text-muted-foreground font-semibold sticky top-0 backdrop-blur-sm z-10 border-b">
                    <tr>
                      <th className="p-3">Applicant ID</th>
                      <th className="p-3">Loan Amount</th>
                      <th className="p-3">Interest Rate</th>
                      <th className="p-3">Annual Income</th>
                      <th className="p-3">FICO Range</th>
                      <th className="p-3">Grade</th>
                      <th className="p-3">State</th>
                      <th className="p-3">Default Prob (PD)</th>
                      <th className="p-3">Risk Tier</th>
                      <th className="p-3 text-right">Credit Copilot</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {filteredRecords.length === 0 ? (
                      <tr>
                        <td colSpan={10} className="p-8 text-center text-muted-foreground">
                          No applicants match the current search / filter criteria.
                        </td>
                      </tr>
                    ) : (
                      filteredRecords.map((borrower, idx) => {
                        const pd = Number(borrower.probability_of_default);
                        const isHigh = borrower.risk_label === 'High Risk';
                        const isMed = borrower.risk_label === 'Medium Risk';
                        const ficoDisplay = borrower.fico && borrower.fico !== 'N/A' 
                          ? borrower.fico 
                          : (borrower.fico_range_low ? `${Math.round(Number(borrower.fico_range_low))}-${Math.round(Number(borrower.fico_range_high))}` : 'N/A');

                        return (
                          <tr key={borrower.id || idx} className="hover:bg-muted/30 transition-colors">
                            <td className="p-3 font-mono font-medium text-foreground">
                              #{borrower.id}
                            </td>
                            <td className="p-3 font-semibold">
                              ${Number(borrower.loan_amnt || 0).toLocaleString()}
                            </td>
                            <td className="p-3">
                              {Number(borrower.int_rate || 0).toFixed(2)}%
                            </td>
                            <td className="p-3">
                              ${Number(borrower.annual_inc || 0).toLocaleString()}
                            </td>
                            <td className="p-3 font-mono">
                              {ficoDisplay}
                            </td>
                            <td className="p-3">
                              <span className="font-bold px-2 py-0.5 rounded bg-muted">
                                {borrower.grade || 'N/A'}
                              </span>
                            </td>
                            <td className="p-3">
                              {borrower.addr_state || 'US'}
                            </td>
                            <td className="p-3 font-mono font-bold">
                              <span className={isHigh ? 'text-rose-400' : (isMed ? 'text-amber-400' : 'text-emerald-400')}>
                                {(pd * 100).toFixed(2)}%
                              </span>
                            </td>
                            <td className="p-3">
                              <span className={`px-2 py-1 rounded-full text-[11px] font-semibold border ${
                                isHigh 
                                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' 
                                  : isMed
                                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                                  : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              }`}>
                                {borrower.risk_label}
                              </span>
                            </td>
                            <td className="p-3 text-right">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => {
                                  setSelectedBorrower(borrower);
                                  setOverrideStatus(null);
                                }}
                                className="h-7 text-xs border-primary/30 hover:bg-primary hover:text-primary-foreground"
                              >
                                <Eye className="w-3.5 h-3.5 mr-1" /> Inspect
                              </Button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
              <div className="p-3 border-t bg-muted/10 text-xs text-muted-foreground flex justify-between items-center">
                <span>Showing {filteredRecords.length} of {result.scored_records?.length || 0} evaluated loan applications</span>
                <span>Powered by XGBoost In-Memory Pipeline</span>
              </div>
            </CardContent>
          </Card>

          {/* Agentic Credit Copilot Modal / Drawer */}
          {selectedBorrower && (
            <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
              <div className="bg-background border border-border rounded-xl shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[90vh]">
                
                {/* Modal Header */}
                <div className="p-5 border-b bg-muted/30 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      selectedBorrower.risk_label === 'High Risk' 
                        ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                        : (selectedBorrower.risk_label === 'Medium Risk' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20')
                    }`}>
                      {selectedBorrower.risk_label === 'High Risk' ? <ShieldAlert className="w-6 h-6" /> : (selectedBorrower.risk_label === 'Medium Risk' ? <AlertTriangle className="w-6 h-6" /> : <ShieldCheck className="w-6 h-6" />)}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold">
                        Underwriting Forensic Memo: Applicant #{selectedBorrower.id}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        Machine Learning Feature Attribution & Compliance Audit Trail
                      </p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setSelectedBorrower(null)}
                    className="p-1 rounded-md text-muted-foreground hover:bg-muted"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Modal Body */}
                <div className="p-6 space-y-6 overflow-y-auto">
                  
                  {/* Financial Metrics Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-3 bg-muted/40 rounded-lg border text-center">
                      <div className="text-[11px] text-muted-foreground uppercase">Loan Amount</div>
                      <div className="text-base font-bold text-foreground mt-0.5">
                        ${Number(selectedBorrower.loan_amnt || 0).toLocaleString()}
                      </div>
                    </div>
                    <div className="p-3 bg-muted/40 rounded-lg border text-center">
                      <div className="text-[11px] text-muted-foreground uppercase">Interest Rate</div>
                      <div className="text-base font-bold text-foreground mt-0.5">
                        {Number(selectedBorrower.int_rate || 0).toFixed(2)}%
                      </div>
                    </div>
                    <div className="p-3 bg-muted/40 rounded-lg border text-center">
                      <div className="text-[11px] text-muted-foreground uppercase">Annual Income</div>
                      <div className="text-base font-bold text-foreground mt-0.5">
                        ${Number(selectedBorrower.annual_inc || 0).toLocaleString()}
                      </div>
                    </div>
                    <div className="p-3 bg-muted/40 rounded-lg border text-center">
                      <div className="text-[11px] text-muted-foreground uppercase">FICO Range</div>
                      <div className="text-base font-bold text-foreground mt-0.5">
                        {selectedBorrower.fico && selectedBorrower.fico !== 'N/A' 
                          ? selectedBorrower.fico 
                          : (selectedBorrower.fico_range_low ? `${Math.round(Number(selectedBorrower.fico_range_low))}-${Math.round(Number(selectedBorrower.fico_range_high))}` : 'N/A')}
                      </div>
                    </div>
                  </div>

                  {/* Quantitative Credit Risk Score Card */}
                  <div className="p-4 rounded-xl border bg-muted/20 space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold uppercase text-muted-foreground">Calibrated Probability of Default (PD)</span>
                      <span className={`text-xl font-mono font-bold ${
                        selectedBorrower.risk_label === 'High Risk' 
                          ? 'text-rose-400' 
                          : (selectedBorrower.risk_label === 'Medium Risk' ? 'text-amber-400' : 'text-emerald-400')
                      }`}>
                        {(Number(selectedBorrower.probability_of_default) * 100).toFixed(2)}%
                      </span>
                    </div>

                    <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-500 ${
                          selectedBorrower.risk_label === 'High Risk' 
                            ? 'bg-rose-500' 
                            : (selectedBorrower.risk_label === 'Medium Risk' ? 'bg-amber-500' : 'bg-emerald-500')
                        }`}
                        style={{ width: `${Math.min(100, Math.max(5, Number(selectedBorrower.probability_of_default) * 100))}%` }}
                      />
                    </div>
                    
                    <div className="flex justify-between text-[11px] text-muted-foreground">
                      <span>Low Risk (PD &lt; 15%)</span>
                      <span>Cutoff Benchmark: 24.00%</span>
                      <span>High Risk (PD &ge; 25%)</span>
                    </div>
                  </div>

                  {/* Automated Agentic Credit Memorandum */}
                  <div className="border border-border/80 rounded-xl p-4 bg-card space-y-3">
                    <div className="flex items-center space-x-2 text-primary font-semibold text-sm">
                      <Sparkles className="w-4 h-4" />
                      <span>Copilot Underwriting Rationale & Supervisory Memo</span>
                    </div>
                    <div className="text-xs text-muted-foreground leading-relaxed space-y-2">
                      {selectedBorrower.risk_label === 'High Risk' ? (
                        <>
                          <p>
                            <strong>Adverse Risk Triggers:</strong> Model identifies elevated default probability (<strong>{(Number(selectedBorrower.probability_of_default) * 100).toFixed(2)}%</strong>) driven by Grade <strong>{selectedBorrower.grade || 'subprime'}</strong> risk profiling, APR pricing of <strong>{Number(selectedBorrower.int_rate).toFixed(2)}%</strong>, and debt burden relative to annual liquidity (${Number(selectedBorrower.annual_inc).toLocaleString()}).
                          </p>
                          <p>
                            <strong>Credit Policy Recommendation:</strong> <span className="text-rose-400 font-semibold">Decline or Restructure.</span> If secondary underwriting approves, mandate compensatory covenants: minimum 25% debt coverage, collateral lien, or loan amount reduction below $10,000.
                          </p>
                        </>
                      ) : selectedBorrower.risk_label === 'Medium Risk' ? (
                        <>
                          <p>
                            <strong>Moderate Risk Profile:</strong> Borrower exhibits near-prime default probability (<strong>{(Number(selectedBorrower.probability_of_default) * 100).toFixed(2)}%</strong>). Debt servicing capability is viable with Grade <strong>{selectedBorrower.grade}</strong> risk profile and ${Number(selectedBorrower.annual_inc).toLocaleString()} annual income.
                          </p>
                          <p>
                            <strong>Credit Policy Recommendation:</strong> <span className="text-amber-400 font-semibold">Conditional Approval.</span> Origination approved subject to income verification documentation and standard pricing adjustment.
                          </p>
                        </>
                      ) : (
                        <>
                          <p>
                            <strong>Favorable Risk Drivers:</strong> Borrower exhibits low credit variance (PD <strong>{(Number(selectedBorrower.probability_of_default) * 100).toFixed(2)}%</strong>) within institutional tolerance (&lt;15%). FICO benchmark with prime interest rate pricing ({Number(selectedBorrower.int_rate).toFixed(2)}%) indicates high debt service stability.
                          </p>
                          <p>
                            <strong>Credit Policy Recommendation:</strong> <span className="text-emerald-400 font-semibold">Straight-Through Processing (STP) Approval.</span> Automated origination approved with standard disbursement covenants.
                          </p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Supervisory Override Action Log */}
                  {overrideStatus && (
                    <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs text-emerald-400 flex items-center">
                      <UserCheck className="w-4 h-4 mr-2" />
                      <span>{overrideStatus}</span>
                    </div>
                  )}

                  {/* Human-in-the-Loop Action Controls */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="flex items-center space-x-2">
                      <Button 
                        size="sm"
                        onClick={() => setOverrideStatus('Audit Trail: Algorithmic decision ratified by Credit Committee.')}
                        variant={selectedBorrower.risk_label === 'High Risk' ? 'destructive' : 'default'}
                        className="text-xs h-8"
                      >
                        <Check className="w-3.5 h-3.5 mr-1" /> Confirm Model Decision
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => setOverrideStatus('Audit Trail: Supervisory Manual Override initiated (Senior Credit Officer approval required).')}
                        className="text-xs h-8 border-amber-500/40 text-amber-400 hover:bg-amber-500/10"
                      >
                        <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Supervisory Override
                      </Button>
                    </div>

                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={() => setSelectedBorrower(null)}
                      className="text-xs h-8 text-muted-foreground"
                    >
                      Close Inspector
                    </Button>
                  </div>

                </div>

              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
}
