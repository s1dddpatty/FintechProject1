'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UploadCloud, CheckCircle2, AlertCircle, FileText, Download, Briefcase, Percent, Activity } from 'lucide-react';
import axios from 'axios';
import useSWR from 'swr';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

export default function PortfolioScoringPage() {
  const { data: latestModel, error: modelError, isLoading: modelLoading } = useSWR('http://localhost:8000/ml/models/latest', fetcher);
  
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleScore = async () => {
    if (!file) return;
    setIsProcessing(true);
    setResult(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      console.log('Sending POST request to /ml/portfolio/score...');
      const res = await axios.post('http://localhost:8000/ml/portfolio/score', formData);
      console.log('Received response:', res.data);
      setResult(res.data);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Scoring failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!result?.session_id) return;
    window.open(`http://localhost:8000/ml/portfolio/download/${result.session_id}`, '_blank');
  };

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
              <div className="flex justify-between items-center"><span className="flex items-center"><CheckCircle2 className="w-4 h-4 mr-2 text-emerald-500" /> Validating schema</span><span>Done</span></div>
              <div className="flex justify-between items-center"><span className="flex items-center"><Activity className="w-4 h-4 mr-2 text-primary animate-spin" /> Preprocessing features</span><span>Running</span></div>
              <div className="flex justify-between items-center opacity-50"><span className="flex items-center"><FileText className="w-4 h-4 mr-2" /> Running inference</span><span>Waiting</span></div>
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
              The uploaded dataset cannot be scored because it is missing required features.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h4 className="text-sm font-semibold mb-2">Missing Required Features</h4>
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
          
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2 text-emerald-500 font-medium">
              <CheckCircle2 className="w-5 h-5" />
              <span>Scoring Complete ({result.processing_summary.processing_time_seconds}s)</span>
            </div>
            <Button onClick={handleDownload} variant="default" className="shadow-md">
              <Download className="w-4 h-4 mr-2" /> Download Scored Portfolio
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Column 1: Processing & Intelligence */}
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
                    <span className="text-muted-foreground">Model Version</span>
                    <span className="font-mono">{result.processing_summary.model_version} ({result.processing_summary.algorithm})</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="bg-muted/30 border-b pb-4">
                  <CardTitle className="text-lg">Dataset Intelligence</CardTitle>
                  <CardDescription>Schema validation & feature detection</CardDescription>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
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
                      <div className="text-sm text-emerald-500 flex items-center"><CheckCircle2 className="w-4 h-4 mr-1" /> No missing values found</div>
                    ) : (
                      <div className="text-sm text-amber-500 flex items-center"><AlertCircle className="w-4 h-4 mr-1" /> Imputation applied by pipeline</div>
                    )}
                  </div>
                  {Object.keys(result.dataset_intelligence.mapped_features || {}).length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Auto-Mapped Features</h4>
                      <div className="text-xs text-muted-foreground">
                        {Object.keys(result.dataset_intelligence.mapped_features).length} column(s) successfully mapped to required schema.
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
                    <CardTitle className="text-base">Risk Distribution</CardTitle>
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
                    <CardTitle className="text-base">Probability of Default Distribution</CardTitle>
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
                  <CardTitle className="text-lg">Business Insights</CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                  <div className="text-sm">
                    <strong>Portfolio Composition:</strong> {result.business_insights.portfolio_composition}
                  </div>
                  <div className="text-sm">
                    <strong>Decision Recommendation:</strong> {result.business_insights.approval_recommendation}
                  </div>
                  {Object.keys(result.business_insights.highest_risk_grades).length > 0 && (
                    <div className="text-sm">
                      <strong>Highest Risk Segments (By Grade):</strong>
                      <div className="flex space-x-4 mt-2">
                        {Object.entries(result.business_insights.highest_risk_grades).map(([grade, pd]: [string, any]) => (
                          <div key={grade} className="bg-rose-500/10 text-rose-700 px-3 py-1 rounded-md border border-rose-500/20">
                            Grade {grade}: {(pd * 100).toFixed(1)}% PD
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
