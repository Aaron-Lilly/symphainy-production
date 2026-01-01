/**
 * FileDashboard Components
 * Sub-components for FileDashboard functionality
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { RefreshCw, Trash2, Database, Zap } from 'lucide-react';
import { FileMetadata, FileStatus } from '@/shared/types/file';
import { FileTableProps, FileStats } from './types';
import { getStatusVariant, getStatusColor, formatFileSize, formatDate } from './utils';

export function FileTable({ files, onDelete, onSelect, onEnhancedProcessing, deleting }: FileTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>File Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Size</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Created</TableHead>
          <TableHead>Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {files.map((file) => (
          <TableRow key={file.uuid}>
            <TableCell>
              <button
                onClick={() => onSelect(file)}
                className="text-left hover:text-blue-600 hover:underline"
              >
                {file.ui_name}
              </button>
            </TableCell>
            <TableCell>
              <Badge variant="outline">{file.file_type}</Badge>
            </TableCell>
            <TableCell>
              {formatFileSize(file.metadata?.size || 0)}
            </TableCell>
            <TableCell>
              <Badge variant={getStatusVariant(file.status)}>
                {file.status}
              </Badge>
            </TableCell>
            <TableCell>{formatDate(file.created_at)}</TableCell>
            <TableCell>
              <div className="flex gap-1">
                {file.status === 'uploaded' && onEnhancedProcessing && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEnhancedProcessing(file)}
                    title="Enhanced Processing"
                  >
                    <Zap className="h-4 w-4" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(file.uuid)}
                  disabled={deleting === file.uuid}
                  title="Delete File"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function FileStatsCard({ stats }: { stats: FileStats }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Database className="h-5 w-5" />
          <span>File Statistics</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-gray-500">Total Files</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.validated}</div>
            <div className="text-sm text-gray-500">Validated</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.uploaded}</div>
            <div className="text-sm text-gray-500">Uploaded</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.parsed}</div>
            <div className="text-sm text-gray-500">Parsed</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function EmptyState() {
  return (
    <div className="text-center py-12">
      <Database className="mx-auto h-12 w-12 text-gray-400" />
      <h3 className="mt-2 text-sm font-medium text-gray-900">No files</h3>
      <p className="mt-1 text-sm text-gray-500">
        Get started by uploading a file to begin processing.
      </p>
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="text-center py-12">
      <RefreshCw className="mx-auto h-12 w-12 text-gray-400 animate-spin" />
      <h3 className="mt-2 text-sm font-medium text-gray-900">Loading files...</h3>
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="text-center py-12">
      <div className="mx-auto h-12 w-12 text-red-400">⚠️</div>
      <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading files</h3>
      <p className="mt-1 text-sm text-gray-500">{error}</p>
      <Button onClick={onRetry} className="mt-4">
        <RefreshCw className="h-4 w-4 mr-2" />
        Retry
      </Button>
    </div>
  );
} 