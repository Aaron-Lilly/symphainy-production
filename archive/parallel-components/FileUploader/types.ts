/**
 * FileUploader Types
 * Type definitions for FileUploader component
 */

import { FileType, ComponentUploadRequest } from '@/shared/types/file';

export interface FileUploaderProps {
  onFileUploaded?: (fileId: string) => void;
  onUploadError?: (error: string) => void;
  className?: string;
}

export interface FileTypeOption {
  label: string;
  type: FileType;
  extensions: string;
  description?: string;
}

export interface UploadState {
  selectedType: FileType | null;
  selectedExtensions: string | null;
  selectedFile: File | null;
  copybookFile: File | null;
  uploading: boolean;
  error: string | null;
  processingStatus: string | null;
  workflowId: string | null;
}

// FileUploadRequest is now imported from canonical types as ComponentUploadRequest 