/**
 * ParsePreview Core
 * Core ParsePreview component with parsing interface
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { FileType } from '@/shared/types/file';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { CheckCircle, XCircle } from 'lucide-react';
import { ParsePreviewProps } from './types';
import { useParsePreview } from './hooks';
import { ParsedDataModal, TabbedParsedData, ParseStatusIndicator } from './components';

export function ParsePreview({ onParseComplete, onParseError, className }: ParsePreviewProps) {
  const {
    state,
    filesToParse,
    selectedFile,
    handleParse,
    // Approve/reject functionality removed
    resetParse,
    setSelectedFileUuid,
    setActiveTab,
    toggleDetailsModal,
  } = useParsePreview();

  const handleParseClick = async () => {
    const result = await handleParse();
    if (result.success && onParseComplete) {
      onParseComplete(selectedFile?.uuid || '', result.data);
    } else if (!result.success && onParseError) {
      onParseError(result.error || 'Parse failed');
    }
  };

  return (
    <div className={`space-y-4 ${className || ''}`}>
      {/* File Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Select File to Parse</label>
        <Select
          value={state.selectedFileUuid || ''}
          onValueChange={setSelectedFileUuid}
        >
          <SelectTrigger>
            <SelectValue placeholder="Choose a file to parse" />
          </SelectTrigger>
          <SelectContent>
            {filesToParse.map((file) => (
              <SelectItem key={file.uuid} value={file.uuid}>
                <div className="flex flex-col">
                  <span className="font-medium">{file.ui_name}</span>
                  <span className="text-xs text-gray-500">{file.file_type}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Parse Status */}
      {state.parseState !== 'idle' && (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <ParseStatusIndicator parseState={state.parseState} />
          {state.parseState === 'success' && (
            <Button variant="outline" size="sm" onClick={toggleDetailsModal}>
              View Details
            </Button>
          )}
        </div>
      )}

      {/* Error Display */}
      {state.error && (
        <div className="text-red-600 text-sm p-3 bg-red-50 rounded-lg">
          {state.error}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <Button
          onClick={handleParseClick}
          disabled={!selectedFile || state.parseState === 'parsing'}
          className="flex-1"
        >
          {state.parseState === 'parsing' ? 'Parsing...' : 'Parse File'}
        </Button>

        {/* Approve/reject buttons removed - no longer needed */}

        {state.parseState !== 'idle' && (
          <Button onClick={resetParse} variant="ghost" size="sm">
            Reset
          </Button>
        )}
      </div>

      {/* Parsed Data Display */}
      {state.parseState === 'success' && state.parsedData && (
        <div className="mt-4 p-4 border rounded-lg">
          <TabbedParsedData 
            data={state.parsedData} 
            fileType={selectedFile?.file_type || FileType.Structured} 
          />
        </div>
      )}

      {/* Details Modal */}
      {state.showDetailsModal && state.parsedData && (
        <ParsedDataModal
          data={state.parsedData}
          onClose={toggleDetailsModal}
        />
      )}
    </div>
  );
} 