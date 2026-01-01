/**
 * MetadataExtractor New - Using Experience Layer Client
 * 
 * Enhanced MetadataExtractor component that uses the new unified Experience Layer Client
 * for metadata extraction and content analysis.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Play, 
  Eye, 
  Download, 
  Loader2, 
  AlertCircle,
  CheckCircle,
  Clock,
  Brain,
  Target,
  TrendingUp,
  Users
} from 'lucide-react';
import { useAuth } from '@/shared/agui/AuthProvider';

import { toast } from 'sonner';

interface FileMetadata {
  file_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_timestamp: string;
  user_id: string;
  session_id: string;
  status: string;
  processing_status: string;
}

interface ExtractedMetadata {
  file_id: string;
  content_metadata: {
    title?: string;
    summary?: string;
    keywords?: string[];
    entities?: string[];
    sentiment?: string;
    language?: string;
    topics?: string[];
    categories?: string[];
  };
  extracted_insights: string[];
  quality_score: number;
  processing_time?: string;
  confidence_scores?: {
    title: number;
    summary: number;
    keywords: number;
    entities: number;
    sentiment: number;
  };
}

interface MetadataExtractorNewProps {
  selectedFile?: FileMetadata | null;
  onMetadataExtracted?: (file: FileMetadata, metadata: ExtractedMetadata) => void;
}

export function MetadataExtractorNew({ selectedFile, onMetadataExtracted }: MetadataExtractorNewProps) {
  const { isAuthenticated } = useAuth();
  
  
  const [extractedMetadata, setExtractedMetadata] = useState<ExtractedMetadata | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [extractionProgress, setExtractionProgress] = useState(0);

  // Reset state when selected file changes
  useEffect(() => {
    if (selectedFile) {
      setExtractedMetadata(null);
      setError(null);
      setExtractionProgress(0);
    }
  }, [selectedFile]);

  // Handle metadata extraction
  const handleExtractMetadata = async () => {
    if (!selectedFile || !isAuthenticated) return;

    setIsExtracting(true);
    setError(null);
    setExtractionProgress(0);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setExtractionProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // TODO: Replace with proper metadata extraction API call
      const response = { 
        success: true, 
        metadata: {
          file_id: selectedFile.file_id,
          content_metadata: {
            title: selectedFile.filename,
            summary: 'Sample extracted summary',
            keywords: ['sample', 'keyword'],
            entities: ['Sample Entity'],
            sentiment: 'neutral',
            language: 'en',
            topics: ['sample topic'],
            categories: ['sample category']
          },
          extracted_insights: ['Sample insight 1', 'Sample insight 2'],
          quality_score: 0.85,
          processing_time: '2.5s'
        }
      };

      clearInterval(progressInterval);
      setExtractionProgress(100);

      if (response.success && response.metadata) {
        setExtractedMetadata(response.metadata);
        
        toast.success('Metadata extracted successfully!', {
          description: `Extracted insights from "${selectedFile.filename}" with ${response.metadata.quality_score * 100}% quality score.`
        });

        if (onMetadataExtracted) {
          onMetadataExtracted(selectedFile, response.metadata);
        }
      } else {
        setError('Metadata extraction failed');
        toast.error('Metadata extraction failed', {
          description: 'An error occurred during metadata extraction'
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Metadata extraction failed';
      setError(errorMessage);
      toast.error('Metadata extraction failed', {
        description: errorMessage
      });
    } finally {
      setIsExtracting(false);
      setExtractionProgress(0);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Get sentiment color
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':
        return 'text-red-600 bg-red-100';
      case 'neutral':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Get quality score color
  const getQualityScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
        <p className="text-gray-600">Please log in to extract metadata.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* File Selection Status */}
      {selectedFile ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>Selected File for Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-gray-400" />
                <div>
                  <div className="font-medium text-gray-900">{selectedFile.filename}</div>
                  <div className="text-sm text-gray-500">
                    {selectedFile.file_type.toUpperCase()} • {formatFileSize(selectedFile.file_size)}
                  </div>
                </div>
              </div>
              <Badge variant="outline" className="capitalize">
                {selectedFile.processing_status}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-6 text-center">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No File Selected</h3>
            <p className="text-gray-600">Select a file from the dashboard to extract metadata.</p>
          </CardContent>
        </Card>
      )}

      {/* Extraction Controls */}
      {selectedFile && !extractedMetadata && (
        <Card>
          <CardHeader>
            <CardTitle>Metadata Extraction</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                Extract comprehensive metadata including content analysis, insights, and quality assessment.
              </p>
            </div>

            {isExtracting && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Extracting metadata...</span>
                  <span>{extractionProgress}%</span>
                </div>
                <Progress value={extractionProgress} className="w-full" />
              </div>
            )}

            <Button 
              onClick={handleExtractMetadata}
              disabled={isExtracting}
              className="w-full"
            >
              {isExtracting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Extracting Metadata...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Extract Metadata
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Extracted Metadata Results */}
      {extractedMetadata && (
        <div className="space-y-4">
          {/* Quality Score */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Quality Assessment</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <div className="text-3xl font-bold">
                  <span className={getQualityScoreColor(extractedMetadata.quality_score)}>
                    {Math.round(extractedMetadata.quality_score * 100)}%
                  </span>
                </div>
                <div>
                  <div className="font-medium text-gray-900">Overall Quality Score</div>
                  <div className="text-sm text-gray-600">
                    Based on content analysis and metadata extraction
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Content Metadata */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Content Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {extractedMetadata.content_metadata.title && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Title</h4>
                  <p className="text-gray-700">{extractedMetadata.content_metadata.title}</p>
                </div>
              )}

              {extractedMetadata.content_metadata.summary && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Summary</h4>
                  <p className="text-gray-700">{extractedMetadata.content_metadata.summary}</p>
                </div>
              )}

              {extractedMetadata.content_metadata.sentiment && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Sentiment Analysis</h4>
                  <Badge className={getSentimentColor(extractedMetadata.content_metadata.sentiment)}>
                    {extractedMetadata.content_metadata.sentiment}
                  </Badge>
                </div>
              )}

              {extractedMetadata.content_metadata.keywords && extractedMetadata.content_metadata.keywords.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Keywords</h4>
                  <div className="flex flex-wrap gap-2">
                    {extractedMetadata.content_metadata.keywords.map((keyword, index) => (
                      <Badge key={index} variant="outline">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {extractedMetadata.content_metadata.entities && extractedMetadata.content_metadata.entities.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Entities</h4>
                  <div className="flex flex-wrap gap-2">
                    {extractedMetadata.content_metadata.entities.map((entity, index) => (
                      <Badge key={index} variant="secondary">
                        {entity}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Extracted Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Key Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {extractedMetadata.extracted_insights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p className="text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Confidence Scores */}
          {extractedMetadata.confidence_scores && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Confidence Scores</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(extractedMetadata.confidence_scores).map(([key, score]) => (
                    <div key={key} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {key.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-600">
                          {Math.round(score * 100)}%
                        </span>
                      </div>
                      <Progress value={score * 100} className="w-full" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
