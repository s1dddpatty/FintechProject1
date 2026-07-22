import { useQuery } from '@tanstack/react-query';
import { DashboardService } from '../services/dashboard';

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => DashboardService.getDashboardStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}
