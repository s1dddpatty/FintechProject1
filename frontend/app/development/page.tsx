'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UploadCloud, Database, Activity, BrainCircuit, CheckCircle2, Play, AlertCircle, Cpu, ArrowRight } from 'lucide-react';
import axios from 'axios';
import useSWR from 'swr';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

export default function ModelDevelopmentPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  
  const { data: dbStatus, mutate: mutateDb, error: dbError } = useSWR('http://localhost:8000/analytics/portfolio', fetcher);
  const { data: latestModel, mutate: mutateModel } = useSWR('http://localhost:8000/ml/models/latest', fetcher);

  const hasData = dbStatus && dbStatus.total_loans?.value > 0;

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadResult(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      // Use the correct ingestion endpoint
      const res = await axios.post('http://localhost:8000/ingestion/upload', formData);
      setUploadResult(res.data);
      mutateDb();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleTrain = async () => {
    setIsTraining(true);
    try {
      await axios.post('http://localhost:8000/ml/train');
      mutateModel();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Training failed');
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Model Development</h1>
        <p className="text-muted-foreground mt-1">End-to-end ML lifecycle for the credit risk model</p>
      </div>

      <div className="space-y-6 relative border-l-2 border-muted ml-4 pl-8 py-4">
        
        {/* Step 1: Dataset Upload */}
        <div className="relative">
          <div className="absolute -left-[41px] top-4 bg-primary text-primary-foreground w-8 h-8 rounded-full flex items-center justify-center font-bold">1</div>
          <Card className={hasData ? "border-muted" : "border-primary"}>
            <CardHeader>
              <CardTitle className="flex items-center">Upload Training Dataset</CardTitle>
              <CardDescription>Upload labelled historical data (CSV) to form the basis of the new model.</CardDescription>
            </CardHeader>
            <CardContent>
              {!hasData ? (
                <div className="flex flex-col space-y-4">
                  <label className="border-2 border-dashed border-border rounded-xl p-8 text-center flex flex-col items-center hover:bg-muted/50 cursor-pointer transition-colors">
                    <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
                    <span className="text-sm font-medium">
                      {file ? file.name : "Click to select CSV file"}
                    </span>
                    <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
                  </label>
                  <Button onClick={handleUpload} disabled={isUploading || !file} className="w-full">
                    {isUploading ? "Uploading & Processing..." : "Upload & Process"}
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center text-emerald-500 text-sm font-medium">
                    <CheckCircle2 className="w-4 h-4 mr-2" /> Dataset successfully loaded into system database.
                  </div>
                  <Button variant="outline" size="sm" onClick={() => {
                    axios.post('http://localhost:8000/admin/reset-dataset').then(() => {
                        mutateDb();
                        setUploadResult(null);
                    });
                  }}>
                    Reset Dataset
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Step 2: Dataset Intelligence & Processing (Only visible if data exists) */}
        <div className={`relative transition-opacity duration-500 ${hasData ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
          <div className={`absolute -left-[41px] top-4 ${hasData ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} w-8 h-8 rounded-full flex items-center justify-center font-bold`}>2</div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">Dataset Intelligence & Processing</CardTitle>
              <CardDescription>System analysis and automated data cleaning</CardDescription>
            </CardHeader>
            <CardContent>
              {hasData ? (
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-muted/50 p-4 rounded-lg">
                      <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total Database Rows</div>
                      <div className="text-2xl font-semibold">{dbStatus?.total_loans?.value?.toLocaleString()}</div>
                    </div>
                    {uploadResult ? (
                        <div className="bg-emerald-500/10 p-4 rounded-lg border border-emerald-500/20">
                            <div className="text-xs text-emerald-700 uppercase tracking-wider mb-1">Ingestion Success Rate</div>
                            <div className="text-2xl font-semibold text-emerald-600">{uploadResult.success_rate}%</div>
                            <div className="text-xs text-emerald-700 mt-1">Processed in {uploadResult.ingestion_time?.toFixed(2)}s</div>
                        </div>
                    ) : (
                        <div className="bg-muted/50 p-4 rounded-lg flex items-center text-muted-foreground">
                            <CheckCircle2 className="w-5 h-5 mr-2" /> Data is ready for ML pipeline.
                        </div>
                    )}
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">Upload data to unlock this step.</div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Step 3: Model Training */}
        <div className={`relative transition-opacity duration-500 ${hasData ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
          <div className={`absolute -left-[41px] top-4 ${hasData ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'} w-8 h-8 rounded-full flex items-center justify-center font-bold`}>3</div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">Train Model Pipeline</CardTitle>
              <CardDescription>Executes feature engineering, scaling, target generation, and trains the production model.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleTrain} disabled={isTraining || !hasData} className="w-full h-14 text-lg font-medium" variant={latestModel ? "outline" : "default"}>
                {isTraining ? (
                    <span className="flex items-center"><Activity className="w-5 h-5 mr-2 animate-spin" /> Training in progress (this may take a minute)...</span>
                ) : (
                    <span className="flex items-center"><BrainCircuit className="w-5 h-5 mr-2" /> {latestModel ? 'Retrain Model Pipeline' : 'Run ML Pipeline'}</span>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Step 4: Production Model */}
        <div className={`relative transition-opacity duration-500 ${latestModel ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>
          <div className={`absolute -left-[41px] top-4 ${latestModel ? 'bg-emerald-500 text-white' : 'bg-muted text-muted-foreground'} w-8 h-8 rounded-full flex items-center justify-center font-bold`}>4</div>
          <Card className={latestModel ? "border-emerald-500/50 shadow-md ring-1 ring-emerald-500/20" : ""}>
            <CardHeader className={latestModel ? "bg-emerald-500/5 border-b pb-4" : ""}>
              <CardTitle className="flex items-center justify-between">
                <span>Production Model</span>
                {latestModel && <span className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-full flex items-center"><CheckCircle2 className="w-3 h-3 mr-1" /> Active</span>}
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {latestModel ? (
                <div className="space-y-6">
                    <div>
                        <div className="text-sm font-semibold">{latestModel.algorithm}</div>
                        <div className="text-xs text-muted-foreground">Version: {latestModel.version} • Trained: {new Date(latestModel.timestamp).toLocaleString()}</div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div className="bg-card border rounded-lg p-3 text-center">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">ROC-AUC</div>
                            <div className="text-2xl font-bold">{latestModel.roc_auc?.toFixed(4)}</div>
                        </div>
                        <div className="bg-card border rounded-lg p-3 text-center">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">F1 Score</div>
                            <div className="text-2xl font-bold">{latestModel.f1?.toFixed(4)}</div>
                        </div>
                        <div className="bg-card border rounded-lg p-3 text-center">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Threshold</div>
                            <div className="text-2xl font-bold">{(latestModel.operating_threshold * 100).toFixed(1)}%</div>
                        </div>
                        <div className="bg-card border rounded-lg p-3 text-center">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Trained Rows</div>
                            <div className="text-2xl font-bold">{latestModel.trained_on_rows?.toLocaleString()}</div>
                        </div>
                    </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2" /> No production model available. Complete training to activate.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
