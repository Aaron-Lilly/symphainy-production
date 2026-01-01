/**
 * FileDashboard Types
 * Type definitions for FileDashboard component
 */

import { FileMetadata, FileStatus } from '@/shared/types/file';

export interface FileDashboardProps {
  className?: string;
  onFileDeleted?: (fileId: string) => void;
  onFileSelected?: (file: FileMetadata) => void;
  onEnhancedProcessing?: (file: FileMetadata) => void;
  showAll?: boolean;
}

export interface FileDashboardState {
  files: FileMetadata[];
  deleting: string | null;
  isLoadingFiles: boolean;
  error: string | null;
  showAll: boolean;
  initialized: boolean;
}

export interface FileTableProps {
  files: FileMetadata[];
  onDelete: (uuid: string) => void;
  onSelect: (file: FileMetadata) => void;
  onEnhancedProcessing?: (file: FileMetadata) => void;
  deleting: string | null;
}

export interface FileStats {
  total: number;
  uploaded: number;
  parsed: number;
  validated: number;
  rejected: number;
  deleted: number;
}

export interface FileActionRequest {
  fileId: string;
  sessionToken?: string;
  userId?: string;
}

export interface FileActionResponse {
  success: boolean;
  error?: string;
  data?: any;
} 