import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AdminService, ResetDatasetRequest } from '../services/admin';

export function useResetDataset() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ResetDatasetRequest) => AdminService.resetDataset(data),
    onSuccess: () => {
      queryClient.invalidateQueries(); // Invalidate everything since dataset is reset
    },
  });
}