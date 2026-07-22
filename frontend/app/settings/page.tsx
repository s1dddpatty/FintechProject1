'use client';

import PageContainer from '@/components/layout/PageContainer';
import PageHeader from '@/components/layout/PageHeader';
import EmptyState from '@/components/ui/EmptyState';
import { Settings } from 'lucide-react';

export default function SettingsPage() {
  return (
    <PageContainer>
      <PageHeader title="Settings" description="Manage platform configurations and preferences." />
      <div className="mt-6">
        <EmptyState 
          title="Settings Configuration"
          description="User preferences and global platform configurations will live here."
          icon={<Settings className="mx-auto h-12 w-12 text-muted-foreground" />}
        />
      </div>
    </PageContainer>
  );
}
