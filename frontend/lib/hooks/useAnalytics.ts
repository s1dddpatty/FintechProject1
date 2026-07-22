import { useQuery } from '@tanstack/react-query';
import { AnalyticsService } from '../services/analytics';

export function useExecutiveSummary() {
  return useQuery({
    queryKey: ['executiveSummary'],
    queryFn: AnalyticsService.getExecutiveSummary,
    refetchInterval: 300000, // 5 minutes
  });
}

export function useApplicantAnalytics() {
  return useQuery({
    queryKey: ['applicantAnalytics'],
    queryFn: AnalyticsService.getApplicantAnalytics,
    refetchInterval: 300000,
  });
}

export function usePortfolioAnalytics() {
  return useQuery({
    queryKey: ['portfolioAnalytics'],
    queryFn: AnalyticsService.getPortfolioAnalytics,
    refetchInterval: 300000,
  });
}

export function useLoanAnalytics() {
  return useQuery({
    queryKey: ['loanAnalytics'],
    queryFn: AnalyticsService.getLoanAnalytics,
    refetchInterval: 300000,
  });
}

export function useRiskAnalytics() {
  return useQuery({
    queryKey: ['riskAnalytics'],
    queryFn: AnalyticsService.getRiskAnalytics,
    refetchInterval: 300000,
  });
}

export function useSystemHealth() {
  return useQuery({
    queryKey: ['systemHealth'],
    queryFn: AnalyticsService.getSystemHealth,
    refetchInterval: 60000, // 1 minute
  });
}
