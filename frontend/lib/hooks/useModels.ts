import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ModelsService, PredictionRequest, PredictionResponse } from '../services/models';

export function useModels() {
  return useQuery({
    queryKey: ['models'],
    queryFn: ModelsService.getModels,
    refetchInterval: 60000,
  });
}

export function useRetrainModel() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ModelsService.retrainModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
      queryClient.invalidateQueries({ queryKey: ['systemHealth'] });
    },
  });
}

export function usePredict() {
  return useMutation({
    mutationFn: (data: PredictionRequest) => ModelsService.predict(data),
  });
}

export function usePredictBatch() {
  return useMutation({
    mutationFn: (file: File) => ModelsService.predictBatch(file),
  });
}