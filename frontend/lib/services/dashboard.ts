import { apiClient } from '../api/client';

export interface DashboardStats {
  status: string;
  version: string;
  uptime_seconds: number;
  database: string;
  registry: string;
  disk_usage_percent: number;
  memory_usage_percent: number;
}

export const DashboardService = {
  // Currently fetching from the real health endpoint to show actual data on the dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/health');
    return response.data;
  },
};
