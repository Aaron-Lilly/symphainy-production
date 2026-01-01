/**
 * FileDashboard Orchestrator
 * Unified access point for FileDashboard functionality
 */

// Main component
export { FileDashboard } from './core';

// Sub-components
export { 
  FileTable, 
  FileStatsCard, 
  EmptyState, 
  LoadingState, 
  ErrorState 
} from './components';

// Types
export type {
  FileDashboardProps,
  FileDashboardState,
  FileTableProps,
  FileStats,
  FileActionRequest,
  FileActionResponse
} from './types';

// Utilities
export { 
  mockFiles,
  calculateFileStats,
  getStatusVariant,
  getStatusColor,
  formatFileSize,
  formatDate,
  filterFilesByStatus,
  sortFilesByDate
} from './utils';

// Hooks
export { useFileDashboard } from './hooks'; 