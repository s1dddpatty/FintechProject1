'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Cpu, CheckCircle2, AlertCircle } from "lucide-react";
import { useModels } from "@/lib/hooks/useModels";
import { Skeleton } from "@/components/ui/skeleton";

export default function ModelStatus() {
  const { data: models, error, isLoading } = useModels();
  
  const sortedModels = models ? [...models].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()) : [];
  const activeModel = sortedModels.length > 0 ? sortedModels[0] : null;

  return (
    <Card className="rounded-xl shadow-sm border border-border bg-card">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex justify-between items-center">
          <span className="flex items-center"><Cpu className="w-4 h-4 mr-2" /> Model Status</span>
          {!isLoading && !error && activeModel && (
            <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground">
              Production
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3 mt-2">
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : error || !activeModel ? (
          <div className="flex items-start space-x-2 text-sm text-muted-foreground mt-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-amber-500" />
            <span>No model trained yet. Run the training pipeline to generate models.</span>
          </div>
        ) : (
          <div className="space-y-4 mt-2">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Active Model</p>
              <p className="font-semibold text-sm">{activeModel.algorithm} (v{activeModel.version})</p>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-muted/50 p-2 rounded-md">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">ROC-AUC</p>
                <p className="font-medium text-sm">{activeModel.roc_auc?.toFixed(4)}</p>
              </div>
              <div className="bg-muted/50 p-2 rounded-md">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">F1 Score</p>
                <p className="font-medium text-sm">{activeModel.f1?.toFixed(4)}</p>
              </div>
              <div className="bg-muted/50 p-2 rounded-md">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Threshold</p>
                <p className="font-medium text-sm">{(activeModel.operating_threshold * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-muted/50 p-2 rounded-md">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Trained On</p>
                <p className="font-medium text-sm">{activeModel.trained_on_rows?.toLocaleString()}</p>
              </div>
            </div>
            
            <div className="flex items-center text-xs text-emerald-500 font-medium pt-1">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Ready for Prediction
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
