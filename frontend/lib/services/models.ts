import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ModelComparison {
  name: string;
  roc_auc: number;
  f1: number;
  recall: number;
  operating_threshold: number;
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  confusion_matrix: number[][];
}

export interface ModelMetadata {
  model_name: string;
  version: string;
  timestamp: string;
  operating_threshold: number;
  threshold_selection_metric: string;
  algorithm: string;
  trained_on_rows: number;
  training_timestamp: string;
  roc_auc: number;
  precision: number;
  recall: number;
  f1: number;
  feature_count: number;
  class_distribution: Record<string, number>;
  dataset_mode: string;
  model_comparison: ModelComparison[];
  metrics: ModelMetrics;
}

export interface PredictionRequest {
  features: Record<string, any>[];
}

export interface PredictionResult {
  id: string;
  probability_of_default: number;
  decision_threshold: number;
  predicted_class: number;
  risk_label: string;
  confidence_score: number;
  model_version: string;
  timestamp: string;
}

export interface PredictionResponse {
  predictions: PredictionResult[];
}

export const ModelsService = {
  getModels: async (): Promise<ModelMetadata[]> => {
    const response = await apiClient.get<ModelMetadata[]>('/models');
    return response.data;
  },

  retrainModel: async (): Promise<ModelMetadata> => {
    const response = await apiClient.post<ModelMetadata>('/ml/train');
    return response.data;
  },

  predict: async (data: any): Promise<PredictionResponse> => {
    const response = await apiClient.post<PredictionResponse>('/ml/predict', data);
    return response.data;
  },

  predictBatch: async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post<PredictionResponse>('http://localhost:8000/ml/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
};