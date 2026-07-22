import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ResetDatasetRequest {
  keep_models?: boolean;
  dry_run?: boolean;
}

export interface ResetDatasetResponse {
  loans_deleted: number;
  predictions_deleted: number;
  payments_deleted: number;
  models_deleted: boolean;
  database_ready: boolean;
  message: string;
}

export const AdminService = {
  resetDataset: async (data: ResetDatasetRequest): Promise<ResetDatasetResponse> => {
    const response = await apiClient.post<ResetDatasetResponse>('/admin/reset-dataset', data);
    return response.data;
  }
};