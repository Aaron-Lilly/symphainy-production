/**
 * ParsePreview Types
 * Type definitions for ParsePreview component
 */

import { FileType } from '@/shared/types/file';

export type ParseState = "idle" | "parsing" | "success" | "error";

export interface ParsePreviewProps {
  className?: string;
  onParseComplete?: (fileId: string, data: any) => void;
  onParseError?: (error: string) => void;
}

export interface ParsePreviewState {
  selectedFileUuid: string | null;
  parseState: ParseState;
  error: string | null;
  isApproving: boolean;
  parsedData: any;
  showDetailsModal: boolean;
  activeTab: string;
}

export interface ParsedDataModalProps {
  data: any;
  onClose: () => void;
}

export interface TabbedParsedDataProps {
  data: any;
  fileType: FileType;
}

export interface ParseActionRequest {
  fileId: string;
  sessionToken?: string;
  userId?: string;
}

export interface ParseActionResponse {
  success: boolean;
  data?: any;
  error?: string;
  workflowId?: string;
} 