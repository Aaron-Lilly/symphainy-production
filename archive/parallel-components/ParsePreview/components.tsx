/**
 * ParsePreview Components
 * Sub-components for ParsePreview functionality
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { CheckCircle, FileText, XCircle, Loader } from 'lucide-react';
import { FileType } from '@/shared/types/file';
import { ParsedDataModalProps, TabbedParsedDataProps } from './types';
import { getTabsForFileType, getParseStatusColor, getParseStatusIcon } from './utils';
import { StructuredDataTab } from '@/components/content/tabs/StructuredDataTab';
import { TextDataTab } from '@/components/content/tabs/TextDataTab';
import { SOPWorkflowTab } from '@/components/content/tabs/SOPWorkflowTab';
import { FileInfoTab } from '@/components/content/tabs/FileInfoTab';
import { IssuesTab } from '@/components/content/tabs/IssuesTab';
import { ExportOptions } from '@/components/content/ExportOptions';

export function ParsedDataModal({ data, onClose }: ParsedDataModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Parsed Data Details</h3>
          <Button variant="ghost" onClick={onClose}>
            <XCircle className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Data Summary</h4>
            <pre className="text-sm overflow-x-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <ExportOptions 
              data={data} 
              fileType={data?.file_type || FileType.Structured} 
              fileName={data?.ui_name || 'parsed_data'} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export function TabbedParsedData({ data, fileType }: TabbedParsedDataProps) {
  const tabs = getTabsForFileType(fileType);

  const renderTabContent = (tabId: string) => {
    switch (tabId) {
      case "preview":
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium mb-2">Data Preview</h4>
              <pre className="text-sm overflow-x-auto max-h-60">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        );
      
      case "structured-data":
        return <StructuredDataTab data={data} metadata={data?.metadata || {}} />;
      
      case "text-data":
        return <TextDataTab data={data} metadata={data?.metadata || {}} />;
      
      case "sop-workflow":
        return <SOPWorkflowTab file={data} metadata={data?.metadata || {}} />;
      
      case "file-info":
        return <FileInfoTab data={data} metadata={data?.metadata || {}} />;
      
      case "issues":
        return <IssuesTab data={data} />;
      
      default:
        return <div>Tab content not found</div>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className="py-2 px-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      
      <div className="mt-4">
        {renderTabContent(tabs[0]?.id || "preview")}
      </div>
    </div>
  );
}

export function ParseStatusIndicator({ parseState }: { parseState: string }) {
  const color = getParseStatusColor(parseState);
  const iconName = getParseStatusIcon(parseState);
  
  const getIcon = () => {
    switch (iconName) {
      case 'CheckCircle':
        return <CheckCircle className="h-5 w-5" />;
      case 'XCircle':
        return <XCircle className="h-5 w-5" />;
      case 'Loader':
        return <Loader className="h-5 w-5 animate-spin" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${color}`}>
      {getIcon()}
      <span className="text-sm font-medium capitalize">{parseState}</span>
    </div>
  );
} 