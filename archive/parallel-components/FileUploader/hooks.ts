/**
 * FileUploader Hooks
 * Custom hooks for FileUploader component
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileType, FileMetadata, FileStatus, ComponentUploadRequest } from '@/shared/types/file';
import { UploadState } from './types';
import { getAcceptObject, validateFile } from './utils';
import { UnifiedFileAPI } from '@/lib/api/unified-client';
import { uploadAndProcessFile } from '@/lib/api/file-processing';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { toast } from 'sonner';

export function useFileUploader() {
  const { getPillarState, setPillarState, guideSessionToken } = useGlobalSession();
  
  const [uploadState, setUploadState] = useState<UploadState>({
    selectedType: null,
    selectedExtensions: null,
    selectedFile: null,
    copybookFile: null,
    uploading: false,
    error: null,
    processingStatus: null,
    workflowId: null,
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadState(prev => ({ ...prev, selectedFile: acceptedFiles[0] }));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptObject(uploadState.selectedType),
    multiple: false,
  });

  const handleFileTypeChange = useCallback((value: string) => {
    const fileType = value as FileType;
    setUploadState(prev => ({
      ...prev,
      selectedType: fileType,
      selectedExtensions: null,
      selectedFile: null,
      copybookFile: null,
      error: null,
    }));
  }, []);

  const handleCopybookChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setUploadState(prev => ({ ...prev, copybookFile: file }));
  }, []);

  const handleUpload = useCallback(async () => {
    if (!uploadState.selectedFile || !uploadState.selectedType) {
      setUploadState(prev => ({ ...prev, error: 'Please select a file and type' }));
      return;
    }

    const validation = validateFile(uploadState.selectedFile, uploadState.selectedType);
    if (!validation.valid) {
      setUploadState(prev => ({ ...prev, error: validation.error }));
      return;
    }

    setUploadState(prev => ({ ...prev, uploading: true, error: null }));

    try {
      const uploadRequest: ComponentUploadRequest = {
        file: uploadState.selectedFile,
        fileType: uploadState.selectedType,
        copybookFile: uploadState.copybookFile || undefined,
        sessionToken: guideSessionToken,
      };

      // Use unified API client to upload file
      const result = await UnifiedFileAPI.uploadFile(
        uploadState.selectedFile,
        {
          file_type: uploadState.selectedType,
          ui_name: uploadState.selectedFile.name,
          mime_type: uploadState.selectedFile.type,
          original_path: uploadState.selectedFile.name,
          metadata: {
            copybookFile: uploadState.copybookFile?.name
          }
        },
        undefined, // token
        guideSessionToken
      );
      
      if (result.success && result.data) {
        setUploadState(prev => ({
          ...prev,
          uploading: false,
          processingStatus: 'File uploaded successfully',
          workflowId: result.data?.uuid, // Use file UUID as workflow ID
        }));

        // Update pillar state
        const currentState = getPillarState('content');
        const updatedFiles = [...(currentState?.files || []), result.data];
        setPillarState('content', { ...currentState, files: updatedFiles });

        toast.success('File uploaded successfully');
      } else {
        setUploadState(prev => ({
          ...prev,
          uploading: false,
          error: result.error || 'Upload failed',
        }));
        toast.error(result.error || 'Upload failed');
      }
    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      }));
      toast.error('Upload failed');
    }
  }, [uploadState, guideSessionToken, getPillarState, setPillarState]);

  const resetUpload = useCallback(() => {
    setUploadState({
      selectedType: null,
      selectedExtensions: null,
      selectedFile: null,
      copybookFile: null,
      uploading: false,
      error: null,
      processingStatus: null,
      workflowId: null,
    });
  }, []);

  return {
    uploadState,
    setUploadState,
    onDrop,
    getRootProps,
    getInputProps,
    isDragActive,
    handleFileTypeChange,
    handleCopybookChange,
    handleUpload,
    resetUpload,
  };
} 