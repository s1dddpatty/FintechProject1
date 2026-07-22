'use client';

import { useSystemHealth } from '@/lib/hooks/useAnalytics';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Server, Database, Box, MemoryStick, HardDrive, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

export default function SystemStatus() {
  const { data, isLoading, isError } = useSystemHealth();

  if (isLoading) {
    return (
      <Card className="rounded-xl shadow-sm border border-border bg-card">
        <CardHeader className="pb-2 border-b border-border/50">
          <Skeleton className="h-5 w-1/3" />
        </CardHeader>
        <CardContent className="pt-4 space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-8 w-full rounded" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="rounded-xl shadow-sm border border-border bg-card">
        <CardHeader className="pb-2 border-b border-border/50">
          <CardTitle className="text-sm font-medium flex items-center">
            <Server className="w-4 h-4 mr-2 text-muted-foreground" />
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-8 pb-8 flex flex-col items-center justify-center">
          <XCircle className="w-8 h-8 text-destructive mb-2" />
          <p className="text-sm text-muted-foreground">Unable to reach health probe</p>
        </CardContent>
      </Card>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ok':
      case 'healthy':
        return 'text-emerald-500 bg-emerald-500/10';
      case 'degraded':
        return 'text-amber-500 bg-amber-500/10';
      default:
        return 'text-rose-500 bg-rose-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ok':
      case 'healthy':
        return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
      case 'degraded':
        return <AlertCircle className="w-4 h-4 text-amber-500" />;
      default:
        return <XCircle className="w-4 h-4 text-rose-500" />;
    }
  };

  const metrics = [
    { label: 'Overall', value: data.status, icon: <Server className="w-4 h-4" /> },
    { label: 'Database', value: data.database, icon: <Database className="w-4 h-4" /> },
    { label: 'Registry', value: data.registry, icon: <Box className="w-4 h-4" /> },
    { label: 'Memory', value: `${data.memory_usage_percent}%`, icon: <MemoryStick className="w-4 h-4" /> },
    { label: 'Disk', value: `${data.disk_usage_percent}%`, icon: <HardDrive className="w-4 h-4" /> },
  ];

  return (
    <Card className="rounded-xl shadow-sm border border-border bg-card">
      <CardHeader className="pb-2 border-b border-border/50 flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium flex items-center">
          <Server className="w-4 h-4 mr-2 text-muted-foreground" />
          System Status
        </CardTitle>
        {getStatusIcon(data.status)}
      </CardHeader>
      <CardContent className="pt-4">
        <div className="space-y-3">
          {metrics.map((m, idx) => (
            <div key={idx} className="flex justify-between items-center text-sm">
              <div className="flex items-center text-muted-foreground">
                <span className="mr-2 opacity-70">{m.icon}</span>
                {m.label}
              </div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium uppercase tracking-wider ${
                m.label === 'Memory' || m.label === 'Disk' 
                  ? 'text-foreground bg-secondary'
                  : getStatusColor(m.value)
              }`}>
                {m.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
