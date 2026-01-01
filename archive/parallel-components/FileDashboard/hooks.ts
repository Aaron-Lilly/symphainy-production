/**
 * FileDashboard Hooks
 * Custom hooks for FileDashboard component
 */

import React, { useState, useEffect, useCallback } from 'react';
import { FileMetadata, FileType, FileStatus } from '@/shared/types/file';
import { UnifiedFileAPI } from '@/lib/api/unified-client';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { toast } from 'sonner';
import { FileDashboardState, FileActionRequest, FileActionResponse } from './types';
import { mockFiles } from './utils';

export function useFileDashboard() {
  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();
  
  const [state, setState] = useState<FileDashboardState>({
    files: [],
    deleting: null,
    isLoadingFiles: false,
    error: null,
    showAll: false,
    initialized: false,
  });

  // Initialize from global state only once
  useEffect(() => {
    if (!state.initialized) {
      const currentState = getPillarState("data");
      if (currentState?.files && Array.isArray(currentState.files) && currentState.files.length > 0) {
        setState(prev => ({
          ...prev,
          files: currentState.files,
          showAll: currentState.files.length <= 5,
          initialized: true,
        }));
      }
      if (currentState?.deleting) {
        setState(prev => ({ ...prev, deleting: currentState.deleting }));
      }
    }
  }, [state.initialized, getPillarState]);

  const loadFiles = useCallback(async (): Promise<FileActionResponse> => {
    setState(prev => ({ ...prev, isLoadingFiles: true, error: null }));

    try {
      // Use unified API client to call the correct backend endpoint
      const files = await UnifiedFileAPI.listFiles(undefined, guideSessionToken);
      
      if (files && files.length >= 0) {
        setState(prev => ({
          ...prev,
          files,
          showAll: files.length <= 5,
          isLoadingFiles: false,
        }));
        
        // Update global state
        setPillarState('data', { files });
        
        return { success: true, data: files };
      } else {
        // Fallback to mock data if no files returned
        const fallbackFiles = mockFiles;
        setState(prev => ({
          ...prev,
          files: fallbackFiles,
          showAll: fallbackFiles.length <= 5,
          isLoadingFiles: false,
        }));
        
        setPillarState('data', { files: fallbackFiles });
        return { success: true, data: fallbackFiles };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load files';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isLoadingFiles: false,
      }));
      
      // Fallback to mock data on error
      const fallbackFiles = mockFiles;
      setState(prev => ({
        ...prev,
        files: fallbackFiles,
        showAll: fallbackFiles.length <= 5,
        isLoadingFiles: false,
      }));
      
      setPillarState('data', { files: fallbackFiles });
      return { success: true, data: fallbackFiles };
    }
  }, [guideSessionToken, setPillarState]);

  const handleDelete = useCallback(async (uuid: string): Promise<FileActionResponse> => {
    setState(prev => ({ ...prev, deleting: uuid }));

    try {
      // Use unified API client to call the correct backend endpoint
      const result = await UnifiedFileAPI.deleteFile(uuid, undefined, guideSessionToken);
      
      if (result.success) {
        // Remove file from local state
        const updatedFiles = state.files.filter(file => file.uuid !== uuid);
        setState(prev => ({
          ...prev,
          files: updatedFiles,
          deleting: null,
        }));
        
        // Update global state
        setPillarState('data', { files: updatedFiles });
        
        toast.success('File deleted successfully');
        return { success: true };
      } else {
        setState(prev => ({ ...prev, deleting: null }));
        toast.error(result.error || 'Failed to delete file');
        return { success: false, error: result.error };
      }
    } catch (error) {
      setState(prev => ({ ...prev, deleting: null }));
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete file';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, [state.files, guideSessionToken, setPillarState]);

  const toggleShowAll = useCallback(() => {
    setState(prev => ({ ...prev, showAll: !prev.showAll }));
  }, []);

  const refreshFiles = useCallback(async () => {
    await loadFiles();
  }, [loadFiles]);

  const getDisplayFiles = useCallback(() => {
    return state.showAll ? state.files : state.files.slice(0, 5);
  }, [state.files, state.showAll]);

  return {
    state,
    loadFiles,
    handleDelete,
    toggleShowAll,
    refreshFiles,
    getDisplayFiles,
  };
} 