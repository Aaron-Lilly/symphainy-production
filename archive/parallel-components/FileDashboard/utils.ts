/**
 * FileDashboard Utilities
 * Utility functions for FileDashboard component
 */

import { FileMetadata, FileStatus, FileType } from '@/shared/types/file';
import { FileStats } from './types';

// DEVELOPMENT ONLY: Mock data for local development and testing
// This should never be used in production API calls
export const mockFiles: FileMetadata[] = [
  {
    uuid: "1",
    user_id: "user1",
    ui_name: "data1.csv",
    file_type: FileType.Structured,
    mime_type: "text/csv",
    original_path: "/uploads/data1.csv",
    parsed_path: "",
    status: FileStatus.Uploaded,
    metadata: { size: 12345 },
    insights: {},
    rejection_reason: "",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted: false,
  },
  {
    uuid: "2",
    user_id: "user1",
    ui_name: "report.pdf",
    file_type: FileType.Pdf,
    mime_type: "application/pdf",
    original_path: "/uploads/report.pdf",
    parsed_path: "",
    status: FileStatus.Parsed,
    metadata: { size: 67890 },
    insights: {},
    rejection_reason: "",
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date(Date.now() - 86400000).toISOString(),
    deleted: false,
  },
  {
    uuid: "3",
    user_id: "user1",
    ui_name: "image.jpg",
    file_type: FileType.Binary,
    mime_type: "image/jpeg",
    original_path: "/uploads/image.jpg",
    parsed_path: "",
    status: FileStatus.Validated,
    metadata: { size: 234567 },
    insights: {},
    rejection_reason: "",
    created_at: new Date(Date.now() - 172800000).toISOString(),
    updated_at: new Date(Date.now() - 172800000).toISOString(),
    deleted: false,
  },
];

export function calculateFileStats(files: FileMetadata[]): FileStats {
  return files.reduce(
    (stats, file) => {
      stats.total++;
      
      switch (file.status) {
        case FileStatus.Uploaded:
          stats.uploaded++;
          break;
        case FileStatus.Parsed:
          stats.parsed++;
          break;
        case FileStatus.Validated:
          stats.validated++;
          break;
        // Note: FileStatus.Rejected doesn't exist in the enum anymore
        // Rejected files are handled via the 'rejection_reason' property
        // Note: FileStatus.Deleted doesn't exist in the enum
        // Deleted files are handled via the 'deleted' boolean property
      }
      
      return stats;
    },
    { total: 0, uploaded: 0, parsed: 0, validated: 0, rejected: 0, deleted: 0 } as FileStats
  );
}

export function getStatusVariant(
  status: FileStatus,
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case FileStatus.Uploaded:
      return "secondary";
    case FileStatus.Parsed:
      return "default";
    case FileStatus.Validated:
      return "default";
    // Note: FileStatus.Rejected doesn't exist in the enum anymore
    // Note: FileStatus.Deleted doesn't exist in the enum
    // Deleted files are handled via the 'deleted' boolean property
    default:
      return "outline";
  }
}

export function getStatusColor(status: FileStatus): string {
  switch (status) {
    case FileStatus.Uploaded:
      return "bg-blue-100 text-blue-800";
    case FileStatus.Parsed:
      return "bg-green-100 text-green-800";
    case FileStatus.Validated:
      return "bg-purple-100 text-purple-800";
    // Note: FileStatus.Rejected doesn't exist in the enum anymore
    // Note: FileStatus.Deleted doesn't exist in the enum
    // Deleted files are handled via the 'deleted' boolean property
    default:
      return "bg-gray-100 text-gray-800";
  }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

export function filterFilesByStatus(files: FileMetadata[], status?: FileStatus): FileMetadata[] {
  if (!status) return files;
  return files.filter(file => file.status === status);
}

export function sortFilesByDate(files: FileMetadata[], ascending: boolean = false): FileMetadata[] {
  return [...files].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    return ascending ? dateA - dateB : dateB - dateA;
  });
} 