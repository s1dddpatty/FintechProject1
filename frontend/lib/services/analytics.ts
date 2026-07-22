import axios from 'axios';

// The base API client can be exported here or imported if already defined
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface MetricValue {
  name: string;
  value: number | string;
  description?: string;
}

export interface AggregateMetric {
  name: string;
  distribution: Record<string, number>;
  description?: string;
}

export interface ExecutiveDashboardReport {
  portfolio_kpis: MetricValue[];
  risk_kpis: AggregateMetric[];
  loan_kpis: AggregateMetric[];
}

export interface ApplicantAnalytics {
  home_ownership: AggregateMetric;
  income_stats: AggregateMetric;
}

export interface PortfolioAnalyticsData {
  total_loans: number;
  total_funded: number;
  default_rate: number;
}

export interface LoanAnalyticsData {
  grade_distribution: AggregateMetric;
  status_analysis: AggregateMetric;
}

export interface RiskAnalyticsData {
  default_by_grade: AggregateMetric;
}

export interface SystemHealth {
  status: string;
  version: string;
  uptime_seconds: number;
  database: string;
  registry: string;
  disk_usage_percent: number;
  memory_usage_percent: number;
}

export const AnalyticsService = {
  getExecutiveSummary: async (): Promise<ExecutiveDashboardReport> => {
    const response = await apiClient.get<ExecutiveDashboardReport>('/analytics/executive');
    return response.data;
  },
  
  getApplicantAnalytics: async (): Promise<ApplicantAnalytics> => {
    const response = await apiClient.get<ApplicantAnalytics>('/analytics/applicant');
    return response.data;
  },

  getPortfolioAnalytics: async (): Promise<PortfolioAnalyticsData> => {
    const response = await apiClient.get<PortfolioAnalyticsData>('/analytics/portfolio');
    return response.data;
  },

  getLoanAnalytics: async (): Promise<LoanAnalyticsData> => {
    const response = await apiClient.get<LoanAnalyticsData>('/analytics/loan');
    return response.data;
  },

  getRiskAnalytics: async (): Promise<RiskAnalyticsData> => {
    const response = await apiClient.get<RiskAnalyticsData>('/analytics/risk');
    return response.data;
  },

  getSystemHealth: async (): Promise<SystemHealth> => {
    const response = await apiClient.get<SystemHealth>('/health');
    return response.data;
  }
};
