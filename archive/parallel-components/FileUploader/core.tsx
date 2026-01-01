/**
 * FileUploader Core
 * Core FileUploader component with upload interface
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { UploadCloud } from 'lucide-react';
import { FileUploaderProps } from './types';
import { FILE_TYPE_OPTIONS } from './utils';
import { useFileUploader } from './hooks';

export function FileUploader({ onFileUploaded, onUploadError, className }: FileUploaderProps) {
  const {
    uploadState,
    getRootProps,
    getInputProps,
    isDragActive,
    handleFileTypeChange,
    handleCopybookChange,
    handleUpload,
  } = useFileUploader();

  return (
    <div className={`space-y-4 ${className || ''}`}>
      {/* File Type Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium">File Type</label>
        <Select onValueChange={handleFileTypeChange} value={uploadState.selectedType || ''}>
          <SelectTrigger>
            <SelectValue placeholder="Select file type" />
          </SelectTrigger>
          <SelectContent>
            {FILE_TYPE_OPTIONS.map((option) => (
              <SelectItem key={option.type} value={option.type}>
                <div>
                  <div className="font-medium">{option.label}</div>
                  <div className="text-xs text-gray-500">{option.extensions}</div>
                  {option.description && (
                    <div className="text-xs text-gray-400">{option.description}</div>
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          {isDragActive
            ? 'Drop the file here'
            : 'Drag and drop a file here, or click to select'}
        </p>
        {uploadState.selectedFile && (
          <p className="mt-1 text-sm text-gray-500">
            Selected: {uploadState.selectedFile.name}
          </p>
        )}
      </div>

      {/* Copybook File Upload (for Mainframe files) */}
      {uploadState.selectedType === 'binary' && (
        <div className="space-y-2">
          <label className="text-sm font-medium">Copybook File (Optional)</label>
          <input
            type="file"
            accept=".cpy,.cbl,.txt"
            onChange={handleCopybookChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
      )}

      {/* Error Display */}
      {uploadState.error && (
        <div className="text-red-600 text-sm">{uploadState.error}</div>
      )}

      {/* Upload Button */}
      <Button
        onClick={handleUpload}
        disabled={!uploadState.selectedFile || !uploadState.selectedType || uploadState.uploading}
        className="w-full"
      >
        {uploadState.uploading ? 'Uploading...' : 'Upload File'}
      </Button>

      {/* Processing Status */}
      {uploadState.processingStatus && (
        <div className="text-green-600 text-sm">{uploadState.processingStatus}</div>
      )}
    </div>
  );
} 