/**
 * FileUploader Utilities
 * Utility functions for FileUploader component
 */

import { FileType } from '@/shared/types/file';
import { FileTypeOption } from './types';

export const FILE_TYPE_OPTIONS: FileTypeOption[] = [
  {
    label: "Structured",
    type: FileType.Structured,
    extensions: ".csv .xls .xlsx",
  },
  { 
    label: "Image", 
    type: FileType.Image, 
    extensions: ".jpg .jpeg .png .bmp" 
  },
  { 
    label: "PDF", 
    type: FileType.Pdf, 
    extensions: ".pdf .docx" 
  },
  { 
    label: "Mainframe", 
    type: FileType.Binary, 
    extensions: ".bin .dat" 
  },
  { 
    label: "SOP/Workflow", 
    type: FileType.SopWorkflow, 
    extensions: ".docx .pdf .bpmn .txt .json",
    description: "SOP and Workflow files for Operations pillar processing"
  },
];

export function getAcceptObject(type: FileType | null) {
  if (!type) return undefined;
  
  switch (type) {
    case FileType.Structured:
      return {
        "text/csv": [".csv"],
        "application/vnd.ms-excel": [".xls"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      };
    case FileType.Image:
      return {
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
        "image/bmp": [".bmp"],
      };
    case FileType.Pdf:
      return {
        "application/pdf": [".pdf"],
        "application/docx": [".docx"],
      };
    case FileType.Binary:
      return {
        "application/octet-stream": [".bin", ".dat"],
      };
    case FileType.SopWorkflow:
      return {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
        "application/pdf": [".pdf"],
        "application/xml": [".bpmn"],
        "text/plain": [".txt"],
        "application/json": [".json"],
      };
    default:
      return undefined;
  }
}

export function validateFile(file: File, fileType: FileType): { valid: boolean; error?: string } {
  const maxSize = 100 * 1024 * 1024; // 100MB
  
  if (file.size > maxSize) {
    return { valid: false, error: 'File size exceeds 100MB limit' };
  }

  const acceptObject = getAcceptObject(fileType);
  if (!acceptObject) {
    return { valid: true }; // No validation if no accept object
  }

  const acceptedTypes = Object.keys(acceptObject);
  const fileTypeValid = acceptedTypes.some(type => file.type === type);
  
  if (!fileTypeValid) {
    return { valid: false, error: 'File type not supported for selected category' };
  }

  return { valid: true };
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function getFileTypeOption(type: FileType): FileTypeOption | undefined {
  return FILE_TYPE_OPTIONS.find(option => option.type === type);
} 