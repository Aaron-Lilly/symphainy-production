/**
 * ParsePreview Utilities
 * Utility functions for ParsePreview component
 */

import { FileMetadata, FileStatus } from '@/shared/types/file';
import { FileType } from '@/shared/types/file';

export function combineAndDeduplicateFiles(pillarStates: any[]): FileMetadata[] {
  const allFiles: FileMetadata[] = [];
  
  pillarStates.forEach(state => {
    if (state?.files) {
      allFiles.push(...state.files);
    }
  });

  // Deduplicate by UUID
  const uniqueFilesMap = new Map<string, FileMetadata>();
  allFiles.forEach((file) => {
    if (!uniqueFilesMap.has(file.uuid)) {
      uniqueFilesMap.set(file.uuid, file);
    }
  });

  return Array.from(uniqueFilesMap.values())
    .filter((file: FileMetadata) => file.status === FileStatus.Uploaded)
    .sort((a, b) => {
      // Sort by created_at (most recent first)
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();
      return dateB - dateA;
    });
}

export function getTabsForFileType(fileType: FileType): Array<{ id: string; label: string; icon: any }> {
  const baseTabs = [
    { id: "preview", label: "Preview", icon: "FileText" },
    { id: "file-info", label: "File Info", icon: "Info" },
    { id: "issues", label: "Issues", icon: "AlertTriangle" },
  ];

  switch (fileType) {
    case FileType.Structured:
      return [
        ...baseTabs,
        { id: "structured-data", label: "Structured Data", icon: "Table" },
      ];
    case FileType.Pdf:
    case FileType.Image:
      return [
        ...baseTabs,
        { id: "text-data", label: "Text Data", icon: "FileText" },
      ];
    case FileType.SopWorkflow:
      return [
        ...baseTabs,
        { id: "sop-workflow", label: "SOP/Workflow", icon: "Workflow" },
      ];
    default:
      return baseTabs;
  }
}

export function validateParseRequest(file: FileMetadata): { valid: boolean; error?: string } {
  if (!file) {
    return { valid: false, error: 'No file selected' };
  }

  if (file.status !== FileStatus.Uploaded) {
    return { valid: false, error: 'File is not ready for parsing' };
  }

  if (!file.uuid) {
    return { valid: false, error: 'File UUID is missing' };
  }

  return { valid: true };
}

export function formatParseError(error: any): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.error) {
    return error.error;
  }
  
  return 'An unknown error occurred during parsing';
}

export function getParseStatusColor(parseState: string): string {
  switch (parseState) {
    case 'success':
      return 'text-green-600';
    case 'error':
      return 'text-red-600';
    case 'parsing':
      return 'text-blue-600';
    default:
      return 'text-gray-600';
  }
}

export function getParseStatusIcon(parseState: string): string {
  switch (parseState) {
    case 'success':
      return 'CheckCircle';
    case 'error':
      return 'XCircle';
    case 'parsing':
      return 'Loader';
    default:
      return 'FileText';
  }
} 