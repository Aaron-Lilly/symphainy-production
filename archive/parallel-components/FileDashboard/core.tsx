/**
 * FileDashboard Core
 * Core FileDashboard component with file management interface
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { FileDashboardProps } from './types';
import { useFileDashboard } from './hooks';
import { calculateFileStats } from './utils';
import { 
  FileTable, 
  FileStatsCard, 
  EmptyState, 
  LoadingState, 
  ErrorState 
} from './components';

export function FileDashboard({ 
  onFileDeleted, 
  onFileSelected, 
  onEnhancedProcessing,
  showAll: propShowAll,
  className 
}: FileDashboardProps) {
  const {
    state,
    loadFiles,
    handleDelete,
    toggleShowAll,
    refreshFiles,
    getDisplayFiles,
  } = useFileDashboard();

  const handleDeleteFile = async (uuid: string) => {
    const result = await handleDelete(uuid);
    if (result.success && onFileDeleted) {
      onFileDeleted(uuid);
    }
  };

  const handleSelectFile = (file: any) => {
    if (onFileSelected) {
      onFileSelected(file);
    }
  };

  const stats = calculateFileStats(state.files);
  const displayFiles = getDisplayFiles();

  return (
    <div className={`space-y-6 ${className || ''}`} data-testid="files-dashboard">
      {/* Header with Stats and Refresh */}
      <div className="flex justify-between items-center">
        <FileStatsCard stats={stats} />
        <Button onClick={refreshFiles} disabled={state.isLoadingFiles}>
          <RefreshCw className={`h-4 w-4 mr-2 ${state.isLoadingFiles ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {state.isLoadingFiles ? (
          <LoadingState />
        ) : state.error ? (
          <ErrorState error={state.error} onRetry={loadFiles} />
        ) : displayFiles.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            <FileTable
              files={displayFiles}
              onDelete={handleDeleteFile}
              onSelect={handleSelectFile}
              onEnhancedProcessing={onEnhancedProcessing}
              deleting={state.deleting}
            />
            
            {state.files.length > 5 && (
              <div className="text-center">
                <Button variant="outline" onClick={toggleShowAll}>
                  {state.showAll ? 'Show Less' : `Show All (${state.files.length})`}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 