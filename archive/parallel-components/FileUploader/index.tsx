/**
 * FileUploader Orchestrator
 * Unified access point for FileUploader functionality
 */

// Main component
export { FileUploader } from './core';

// Types
export type {
  FileUploaderProps,
  FileTypeOption,
  UploadState,
  // UploadRequest is now ComponentUploadRequest from shared/types/file
} from './types';

// Utilities
export { FILE_TYPE_OPTIONS, getAcceptObject, validateFile, formatFileSize, getFileTypeOption } from './utils';

// Hooks
export { useFileUploader } from './hooks'; 