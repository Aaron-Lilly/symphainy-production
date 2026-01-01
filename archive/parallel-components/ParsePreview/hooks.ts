/**
 * ParsePreview Hooks
 * Custom hooks for ParsePreview component
 */

import React, { useState, useEffect } from 'react';
import { UnifiedFileAPI } from '@/lib/api/unified-client';
import { FileMetadata, FileType, FileStatus } from '@/shared/types/file';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { toast } from 'sonner';
import { ParsePreviewState, ParseActionRequest, ParseActionResponse } from './types';
import { combineAndDeduplicateFiles, validateParseRequest, formatParseError } from './utils';

export function useParsePreview() {
  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();
  
  const [state, setState] = useState<ParsePreviewState>({
    selectedFileUuid: null,
    parseState: "idle",
    error: null,
    isApproving: false,
    parsedData: null,
    showDetailsModal: false,
    activeTab: "preview",
  });

  // Get files from all pillar states
  const parsingState = getPillarState("parsing") || { files: [] };
  const dataState = getPillarState("data") || { files: [] };
  const contentState = getPillarState("content") || { files: [] };
  const insightsState = getPillarState("insights") || { files: [] };
  const operationsState = getPillarState("operations") || { files: [] };

  const filesToParse = combineAndDeduplicateFiles([
    parsingState,
    dataState,
    contentState,
    insightsState,
    operationsState,
  ]);

  const selectedFile = filesToParse.find((f) => f.uuid === state.selectedFileUuid);

  // Auto-select first file if none selected
  useEffect(() => {
    if (filesToParse.length > 0 && !state.selectedFileUuid) {
      setState(prev => ({ ...prev, selectedFileUuid: filesToParse[0].uuid }));
    }
    
    // Reset if selected file no longer exists
    if (state.selectedFileUuid && !filesToParse.some((f) => f.uuid === state.selectedFileUuid)) {
      setState(prev => ({ 
        ...prev, 
        selectedFileUuid: null, 
        parseState: "idle" 
      }));
    }
  }, [filesToParse, state.selectedFileUuid]);

  const handleParse = async (): Promise<ParseActionResponse> => {
    const validation = validateParseRequest(selectedFile);
    if (!validation.valid) {
      toast.error(validation.error);
      return { success: false, error: validation.error };
    }

    setState(prev => ({ ...prev, parseState: "parsing", error: null }));

    try {
      const request: ParseActionRequest = {
        fileId: selectedFile.uuid,
        sessionToken: guideSessionToken,
      };

      const result = await UnifiedFileAPI.parseFile(request.fileId, undefined, guideSessionToken);
      
      if (result.success) {
        setState(prev => ({
          ...prev,
          parseState: "success",
          parsedData: result.data,
        }));
        
        toast.success('File parsed successfully');
        return { success: true, data: result.data };
      } else {
        const error = formatParseError(result.error);
        setState(prev => ({
          ...prev,
          parseState: "error",
          error,
        }));
        
        toast.error(error);
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage = formatParseError(error);
      setState(prev => ({
        ...prev,
        parseState: "error",
        error: errorMessage,
      }));
      
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Approve/reject functionality removed - no longer needed

  const resetParse = () => {
    setState(prev => ({
      ...prev,
      parseState: "idle",
      error: null,
      parsedData: null,
    }));
  };

  const setSelectedFileUuid = (uuid: string | null) => {
    setState(prev => ({ ...prev, selectedFileUuid: uuid }));
  };

  const setActiveTab = (tab: string) => {
    setState(prev => ({ ...prev, activeTab: tab }));
  };

  const toggleDetailsModal = () => {
    setState(prev => ({ ...prev, showDetailsModal: !prev.showDetailsModal }));
  };

  return {
    state,
    filesToParse,
    selectedFile,
    handleParse,
    resetParse,
    setSelectedFileUuid,
    setActiveTab,
    toggleDetailsModal,
  };
} 