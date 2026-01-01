# Updated Integrated Frontend-Backend Plan
## Symphainy Platform Evolution Strategy

## Executive Summary

After analyzing both platforms, I've identified a significant opportunity to leverage the mature backend architecture (`symphainy-platform`) to transform the frontend (`symphainy-frontend`) into a production-ready, enterprise-grade application that delivers the MVP vision described in the business requirements.

**Key Insight**: The backend has evolved into a sophisticated, micro-module-based architecture with comprehensive business enablement pillars, while the frontend remains fragmented with multiple API patterns and mock data. We can now build a unified, production-ready frontend that fully leverages the backend's capabilities.

## Current State Analysis

### ✅ **Backend Strengths (symphainy-platform)**
- **Sophisticated Architecture**: Micro-module-based business enablement pillars
- **Comprehensive Infrastructure**: 50+ infrastructure abstractions (LLM, storage, analytics, etc.)
- **Real Business Logic**: Content, Insights, Operations, and Business Outcomes pillars with actual implementations
- **Advanced Capabilities**: APG Document Intelligence, Guide Agent, MCP servers, multi-tenant architecture
- **Production-Ready**: Authentication, authorization, telemetry, health monitoring
- **Agentic Integration**: Guide Agent with intent analysis, conversation management, user profiling

### ❌ **Frontend Gaps (symphainy-frontend)**
- **API Fragmentation**: 12+ different API client patterns
- **Mock Data Dependencies**: Hardcoded values and mock responses throughout
- **Authentication Bypass**: No real user context management
- **Inconsistent State Management**: Multiple context providers without coordination
- **Legacy Architecture**: Outdated patterns not leveraging backend capabilities

### 🎯 **MVP Vision Alignment**
The backend already supports the complete MVP journey:
- **Content Pillar**: File upload, parsing, metadata extraction → ✅ Backend Ready
- **Insights Pillar**: Analysis, visualization, recommendations → ✅ Backend Ready  
- **Operations Pillar**: SOP generation, workflow creation, coexistence analysis → ✅ Backend Ready
- **Experience Pillar**: Roadmap generation, POC proposals → ✅ Backend Ready
- **Guide Agent**: Cross-dimensional guidance and concierge services → ✅ Backend Ready

## Strategic Architecture Evolution

### Phase 1: Foundation Consolidation (Week 1-2)

#### 1.1 Create Unified Experience Layer Client

**Objective**: Replace 12+ fragmented API clients with a single, production-ready client that leverages the backend's full capabilities.

**Implementation**:
```typescript
// lib/api/experience-layer-client.ts
export class ExperienceLayerClient {
  private sessionToken: string | null = null;
  private userContext: UserContext | null = null;
  private guideAgent: GuideAgentClient;
  private pillarClients: {
    content: ContentPillarClient;
    insights: InsightsPillarClient;
    operations: OperationsPillarClient;
    businessOutcomes: BusinessOutcomesPillarClient;
  };

  // Real authentication with backend
  async authenticate(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await response.json();
    
    if (data.success && data.token) {
      this.sessionToken = data.token;
      this.userContext = data.user;
      await this.initializePillarClients();
    }
    
    return data;
  }

  // Initialize pillar-specific clients with real backend integration
  private async initializePillarClients() {
    this.pillarClients = {
      content: new ContentPillarClient(this.sessionToken, this.userContext),
      insights: new InsightsPillarClient(this.sessionToken, this.userContext),
      operations: new OperationsPillarClient(this.sessionToken, this.userContext),
      businessOutcomes: new BusinessOutcomesPillarClient(this.sessionToken, this.userContext),
    };
  }

  // Guide Agent integration for cross-dimensional guidance
  async getGuidance(intent: string, context: any): Promise<GuidanceResponse> {
    return await this.guideAgent.analyzeIntent(intent, context);
  }
}
```

#### 1.2 Implement Real User Context Management

**Objective**: Replace mock authentication with real multi-tenant user context management.

**Implementation**:
```typescript
// lib/contexts/UserContextProvider.tsx
export interface UserContext {
  user_id: string;
  email: string;
  full_name: string;
  session_id: string;
  tenant_id: string;
  permissions: string[];
  created_at: string;
  last_active: string;
}

export const UserContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userContext, setUserContext] = useState<UserContext | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Real authentication flow
  const authenticate = async (email: string, password: string) => {
    try {
      const response = await experienceLayerClient.authenticate(email, password);
      if (response.success) {
        setUserContext(response.user);
        setIsAuthenticated(true);
        localStorage.setItem('sessionToken', response.token);
      }
      return response;
    } catch (error) {
      console.error('Authentication failed:', error);
      throw error;
    }
  };

  // Real session validation
  const validateSession = async () => {
    const token = localStorage.getItem('sessionToken');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await experienceLayerClient.validateSession(token);
      if (response.success) {
        setUserContext(response.user);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('sessionToken');
      }
    } catch (error) {
      localStorage.removeItem('sessionToken');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    validateSession();
  }, []);

  return (
    <UserContext.Provider value={{
      userContext,
      isAuthenticated,
      isLoading,
      authenticate,
      logout: () => {
        setUserContext(null);
        setIsAuthenticated(false);
        localStorage.removeItem('sessionToken');
      }
    }}>
      {children}
    </UserContext.Provider>
  );
};
```

#### 1.3 Create Pillar-Specific Clients

**Objective**: Create dedicated clients for each pillar that leverage the backend's micro-module architecture.

**Implementation**:
```typescript
// lib/api/pillar-clients/content-pillar-client.ts
export class ContentPillarClient {
  constructor(
    private sessionToken: string,
    private userContext: UserContext
  ) {}

  // Real file upload with backend integration
  async uploadFile(file: File, fileType: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("file_type", fileType);
    
    const response = await fetch(`${API_BASE}/api/content/upload`, {
      method: "POST",
      body: formData,
      headers: this.getAuthHeaders(false),
    });
    
    return response.json();
  }

  // Real file parsing with backend micro-modules
  async parseFile(fileId: string, parseOptions: ParseOptions): Promise<ParseResponse> {
    const response = await fetch(`${API_BASE}/api/content/parse`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ file_id: fileId, options: parseOptions }),
    });
    
    return response.json();
  }

  // Real metadata extraction
  async extractMetadata(fileId: string): Promise<MetadataResponse> {
    const response = await fetch(`${API_BASE}/api/content/extract-metadata`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ file_id: fileId }),
    });
    
    return response.json();
  }

  // Real file listing with user isolation
  async listFiles(): Promise<FileListResponse> {
    const response = await fetch(`${API_BASE}/api/content/files`, {
      headers: this.getAuthHeaders(),
    });
    
    return response.json();
  }

  private getAuthHeaders(includeContentType: boolean = true): Record<string, string> {
    const headers: Record<string, string> = {};
    
    if (includeContentType) {
      headers["Content-Type"] = "application/json";
    }
    
    if (this.sessionToken) {
      headers.Authorization = `Bearer ${this.sessionToken}`;
    }
    
    return headers;
  }
}
```

### Phase 2: MVP Journey Implementation (Week 3-4)

#### 2.1 Enhanced Content Pillar

**Objective**: Transform the content pillar to deliver the complete MVP experience with real backend integration.

**Implementation**:
```typescript
// app/pillars/content/page.tsx
export default function ContentPage() {
  const { userContext, isAuthenticated } = useUserContext();
  const { contentClient } = useExperienceLayer();
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileMetadata | null>(null);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [metadata, setMetadata] = useState<ContentMetadata | null>(null);

  // Real file upload with progress tracking
  const handleFileUpload = async (file: File, fileType: string) => {
    try {
      const response = await contentClient.uploadFile(file, fileType);
      if (response.success) {
        await fetchFiles(); // Refresh file list
        setSelectedFile(response.data);
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  // Real file parsing with backend micro-modules
  const handleParseFile = async (fileId: string) => {
    try {
      const response = await contentClient.parseFile(fileId, {
        format: 'json_structured',
        include_metadata: true
      });
      
      if (response.success) {
        setParseResult(response.parse_result);
      }
    } catch (error) {
      console.error('Parsing failed:', error);
    }
  };

  // Real metadata extraction
  const handleExtractMetadata = async (fileId: string) => {
    try {
      const response = await contentClient.extractMetadata(fileId);
      if (response.success) {
        setMetadata(response.metadata);
      }
    } catch (error) {
      console.error('Metadata extraction failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <ContentHeader />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FileUploader 
          onUpload={handleFileUpload}
          userContext={userContext}
        />
        
        <FileDashboard 
          files={files}
          onFileSelect={setSelectedFile}
          onParse={handleParseFile}
          onExtractMetadata={handleExtractMetadata}
        />
      </div>

      {parseResult && (
        <ParsePreview 
          parseResult={parseResult}
          onMetadataExtract={handleExtractMetadata}
        />
      )}

      {metadata && (
        <MetadataPreview 
          metadata={metadata}
          onProceedToInsights={() => router.push('/pillars/insights')}
        />
      )}

      <ContentLiaisonAgent 
        selectedFile={selectedFile}
        parseResult={parseResult}
        metadata={metadata}
      />
    </div>
  );
}
```

#### 2.2 Intelligent Insights Pillar

**Objective**: Leverage the backend's insights pillar with real analysis and visualization capabilities.

**Implementation**:
```typescript
// app/pillars/insights/page.tsx
export default function InsightsPage() {
  const { insightsClient } = useExperienceLayer();
  const [selectedFiles, setSelectedFiles] = useState<FileMetadata[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [visualization, setVisualization] = useState<VisualizationData | null>(null);
  const [insightsSummary, setInsightsSummary] = useState<InsightsSummary | null>(null);

  // Real file selection from content pillar
  const handleFileSelection = async (fileIds: string[]) => {
    try {
      const response = await insightsClient.selectFilesForAnalysis(fileIds);
      if (response.success) {
        setSelectedFiles(response.selected_files);
      }
    } catch (error) {
      console.error('File selection failed:', error);
    }
  };

  // Real business analysis with backend micro-modules
  const handleAnalyze = async () => {
    try {
      const response = await insightsClient.analyzeBusinessData({
        file_ids: selectedFiles.map(f => f.file_id),
        analysis_type: 'comprehensive',
        include_visualizations: true
      });
      
      if (response.success) {
        setAnalysisResult(response.analysis);
        setVisualization(response.visualization);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  // Real insights summary generation
  const handleGenerateSummary = async () => {
    try {
      const response = await insightsClient.generateInsightsSummary({
        analysis_result: analysisResult,
        visualization_data: visualization
      });
      
      if (response.success) {
        setInsightsSummary(response.summary);
      }
    } catch (error) {
      console.error('Summary generation failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <InsightsHeader />
      
      <FileSelectionPanel 
        onFileSelection={handleFileSelection}
        selectedFiles={selectedFiles}
      />

      {selectedFiles.length > 0 && (
        <AnalysisPanel 
          onAnalyze={handleAnalyze}
          analysisResult={analysisResult}
          visualization={visualization}
        />
      )}

      {analysisResult && (
        <InsightsSummaryPanel 
          onGenerateSummary={handleGenerateSummary}
          insightsSummary={insightsSummary}
          onProceedToOperations={() => router.push('/pillars/operations')}
        />
      )}

      <InsightsLiaisonAgent 
        analysisResult={analysisResult}
        visualization={visualization}
        insightsSummary={insightsSummary}
      />
    </div>
  );
}
```

#### 2.3 Advanced Operations Pillar

**Objective**: Implement the complete operations pillar with SOP generation, workflow creation, and coexistence analysis.

**Implementation**:
```typescript
// app/pillars/operations/page.tsx
export default function OperationsPage() {
  const { operationsClient } = useExperienceLayer();
  const [selectedFiles, setSelectedFiles] = useState<FileMetadata[]>([]);
  const [sopResult, setSopResult] = useState<SOPResult | null>(null);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResult | null>(null);
  const [coexistenceBlueprint, setCoexistenceBlueprint] = useState<CoexistenceBlueprint | null>(null);

  // Real SOP generation
  const handleGenerateSOP = async () => {
    try {
      const response = await operationsClient.generateSOP({
        file_ids: selectedFiles.map(f => f.file_id),
        sop_type: 'comprehensive'
      });
      
      if (response.success) {
        setSopResult(response.sop);
      }
    } catch (error) {
      console.error('SOP generation failed:', error);
    }
  };

  // Real workflow creation
  const handleCreateWorkflow = async () => {
    try {
      const response = await operationsClient.createWorkflow({
        file_ids: selectedFiles.map(f => f.file_id),
        workflow_type: 'bpmn'
      });
      
      if (response.success) {
        setWorkflowResult(response.workflow);
      }
    } catch (error) {
      console.error('Workflow creation failed:', error);
    }
  };

  // Real coexistence analysis
  const handleAnalyzeCoexistence = async () => {
    try {
      const response = await operationsClient.analyzeCoexistence({
        sop_result: sopResult,
        workflow_result: workflowResult
      });
      
      if (response.success) {
        setCoexistenceBlueprint(response.blueprint);
      }
    } catch (error) {
      console.error('Coexistence analysis failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <OperationsHeader />
      
      <FileSelectionPanel 
        onFileSelection={setSelectedFiles}
        selectedFiles={selectedFiles}
      />

      {selectedFiles.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SOPGenerationPanel 
            onGenerateSOP={handleGenerateSOP}
            sopResult={sopResult}
          />
          
          <WorkflowCreationPanel 
            onCreateWorkflow={handleCreateWorkflow}
            workflowResult={workflowResult}
          />
        </div>
      )}

      {sopResult && workflowResult && (
        <CoexistenceAnalysisPanel 
          onAnalyzeCoexistence={handleAnalyzeCoexistence}
          coexistenceBlueprint={coexistenceBlueprint}
          onProceedToExperience={() => router.push('/pillars/experience')}
        />
      )}

      <OperationsLiaisonAgent 
        sopResult={sopResult}
        workflowResult={workflowResult}
        coexistenceBlueprint={coexistenceBlueprint}
      />
    </div>
  );
}
```

#### 2.4 Experience Pillar with Roadmap Generation

**Objective**: Implement the experience pillar that synthesizes all pillar outputs into actionable roadmaps and POC proposals.

**Implementation**:
```typescript
// app/pillars/experience/page.tsx
export default function ExperiencePage() {
  const { experienceClient } = useExperienceLayer();
  const [pillarOutputs, setPillarOutputs] = useState<PillarOutputs | null>(null);
  const [roadmap, setRoadmap] = useState<StrategicRoadmap | null>(null);
  const [pocProposal, setPocProposal] = useState<POCProposal | null>(null);

  // Real pillar output aggregation
  const handleAggregateOutputs = async () => {
    try {
      const response = await experienceClient.aggregatePillarOutputs();
      if (response.success) {
        setPillarOutputs(response.outputs);
      }
    } catch (error) {
      console.error('Output aggregation failed:', error);
    }
  };

  // Real roadmap generation
  const handleGenerateRoadmap = async () => {
    try {
      const response = await experienceClient.generateStrategicRoadmap({
        pillar_outputs: pillarOutputs,
        roadmap_type: 'comprehensive'
      });
      
      if (response.success) {
        setRoadmap(response.roadmap);
      }
    } catch (error) {
      console.error('Roadmap generation failed:', error);
    }
  };

  // Real POC proposal generation
  const handleGeneratePOC = async () => {
    try {
      const response = await experienceClient.generatePOCProposal({
        roadmap: roadmap,
        pillar_outputs: pillarOutputs
      });
      
      if (response.success) {
        setPocProposal(response.proposal);
      }
    } catch (error) {
      console.error('POC generation failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <ExperienceHeader />
      
      <PillarOutputsSummary 
        outputs={pillarOutputs}
        onAggregate={handleAggregateOutputs}
      />

      {pillarOutputs && (
        <RoadmapGenerationPanel 
          onGenerateRoadmap={handleGenerateRoadmap}
          roadmap={roadmap}
        />
      )}

      {roadmap && (
        <POCProposalPanel 
          onGeneratePOC={handleGeneratePOC}
          pocProposal={pocProposal}
        />
      )}

      <ExperienceLiaisonAgent 
        pillarOutputs={pillarOutputs}
        roadmap={roadmap}
        pocProposal={pocProposal}
      />
    </div>
  );
}
```

### Phase 3: Guide Agent Integration (Week 5)

#### 3.1 Cross-Dimensional Guide Agent

**Objective**: Integrate the backend's Guide Agent for intelligent user guidance throughout the MVP journey.

**Implementation**:
```typescript
// components/guide-agent/GuideAgentProvider.tsx
export const GuideAgentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [guideAgent, setGuideAgent] = useState<GuideAgentClient | null>(null);
  const [currentGuidance, setCurrentGuidance] = useState<GuidanceResponse | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);

  // Real guide agent initialization
  useEffect(() => {
    const initializeGuideAgent = async () => {
      try {
        const agent = new GuideAgentClient();
        await agent.initialize();
        setGuideAgent(agent);
      } catch (error) {
        console.error('Guide agent initialization failed:', error);
      }
    };

    initializeGuideAgent();
  }, []);

  // Real intent analysis and guidance
  const analyzeIntent = async (userInput: string, context: any) => {
    if (!guideAgent) return;

    try {
      const response = await guideAgent.analyzeIntent(userInput, context);
      setCurrentGuidance(response);
      
      // Add to conversation history
      setConversationHistory(prev => [
        ...prev,
        { type: 'user', content: userInput },
        { type: 'agent', content: response.guidance }
      ]);
      
      return response;
    } catch (error) {
      console.error('Intent analysis failed:', error);
    }
  };

  // Real pillar routing
  const routeToPillar = async (intent: string, context: any) => {
    if (!guideAgent) return;

    try {
      const response = await guideAgent.routeToPillar(intent, context);
      return response;
    } catch (error) {
      console.error('Pillar routing failed:', error);
    }
  };

  return (
    <GuideAgentContext.Provider value={{
      guideAgent,
      currentGuidance,
      conversationHistory,
      analyzeIntent,
      routeToPillar
    }}>
      {children}
    </GuideAgentContext.Provider>
  );
};
```

#### 3.2 Intelligent Landing Page

**Objective**: Create a landing page that leverages the Guide Agent to understand user goals and direct them appropriately.

**Implementation**:
```typescript
// app/page.tsx
export default function LandingPage() {
  const { analyzeIntent, routeToPillar } = useGuideAgent();
  const [userGoals, setUserGoals] = useState<string>('');
  const [suggestedData, setSuggestedData] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Real goal analysis with Guide Agent
  const handleGoalAnalysis = async () => {
    if (!userGoals.trim()) return;

    setIsAnalyzing(true);
    try {
      const response = await analyzeIntent(userGoals, {
        current_page: 'landing',
        user_context: 'new_user'
      });
      
      if (response.success) {
        setSuggestedData(response.suggested_data_types);
      }
    } catch (error) {
      console.error('Goal analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Real pillar routing
  const handleProceedToContent = async () => {
    try {
      const response = await routeToPillar('content_upload', {
        user_goals: userGoals,
        suggested_data: suggestedData
      });
      
      if (response.success) {
        router.push('/pillars/content');
      }
    } catch (error) {
      console.error('Pillar routing failed:', error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <LandingHeader />
      
      <div className="max-w-4xl mx-auto">
        <WelcomeSection />
        
        <GoalInputSection 
          value={userGoals}
          onChange={setUserGoals}
          onAnalyze={handleGoalAnalysis}
          isAnalyzing={isAnalyzing}
        />
        
        {suggestedData.length > 0 && (
          <SuggestedDataSection 
            dataTypes={suggestedData}
            onProceed={handleProceedToContent}
          />
        )}
        
        <PillarOverviewSection />
      </div>

      <GuideAgentChat 
        onGoalAnalysis={handleGoalAnalysis}
        suggestedData={suggestedData}
      />
    </div>
  );
}
```

### Phase 4: Production Readiness (Week 6)

#### 4.1 Error Handling & Logging

**Implementation**:
```typescript
// lib/error-handling/ErrorBoundary.tsx
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Real error logging to backend
    this.logError(error, errorInfo);
  }

  private async logError(error: Error, errorInfo: ErrorInfo) {
    try {
      await fetch(`${API_BASE}/api/telemetry/error`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: error.message,
          stack: error.stack,
          component_stack: errorInfo.componentStack,
          timestamp: new Date().toISOString()
        })
      });
    } catch (loggingError) {
      console.error('Failed to log error:', loggingError);
    }
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

#### 4.2 Performance Optimization

**Implementation**:
```typescript
// lib/performance/PerformanceMonitor.tsx
export const PerformanceMonitor: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    // Real performance monitoring
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          // Log page load performance
          console.log('Page load time:', entry.loadEventEnd - entry.loadEventStart);
        }
      }
    });

    observer.observe({ entryTypes: ['navigation', 'measure'] });

    return () => observer.disconnect();
  }, []);

  return <>{children}</>;
};
```

#### 4.3 Real-Time Updates

**Implementation**:
```typescript
// lib/websocket/WebSocketProvider.tsx
export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`${WS_BASE}/ws`);
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };
      
      setSocket(ws);
    };

    connectWebSocket();

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'file_processing_update':
        // Update file processing status
        break;
      case 'analysis_complete':
        // Update analysis results
        break;
      case 'guidance_update':
        // Update guide agent guidance
        break;
    }
  };

  return (
    <WebSocketContext.Provider value={{ socket, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
};
```

## Implementation Timeline

### Week 1-2: Foundation Consolidation
- **Day 1-3**: Create unified experience layer client
- **Day 4-5**: Implement real user context management
- **Day 6-7**: Create pillar-specific clients
- **Day 8-10**: Remove legacy API clients and mock data

### Week 3-4: MVP Journey Implementation
- **Day 1-3**: Enhanced content pillar with real backend integration
- **Day 4-6**: Intelligent insights pillar with analysis and visualization
- **Day 7-9**: Advanced operations pillar with SOP/workflow generation
- **Day 10-12**: Experience pillar with roadmap and POC generation

### Week 5: Guide Agent Integration
- **Day 1-3**: Cross-dimensional guide agent integration
- **Day 4-5**: Intelligent landing page with goal analysis
- **Day 6-7**: Pillar liaison agents for specialized guidance

### Week 6: Production Readiness
- **Day 1-2**: Error handling and logging
- **Day 3-4**: Performance optimization
- **Day 5-7**: Real-time updates and WebSocket integration

## Success Criteria

### ✅ **Technical Success**
- Single, unified API client replacing 12+ fragmented clients
- Real authentication and user context management
- All components using real backend data (no mocks)
- Complete MVP journey working end-to-end
- Guide Agent providing intelligent guidance throughout

### ✅ **Business Success**
- Users can complete the full MVP journey (Content → Insights → Operations → Experience)
- Guide Agent understands user goals and provides relevant suggestions
- Real file processing, analysis, and visualization capabilities
- Strategic roadmap and POC proposal generation
- Multi-tenant architecture supporting multiple users

### ✅ **User Experience Success**
- Seamless navigation between pillars
- Real-time feedback and progress updates
- Intelligent guidance and recommendations
- Professional, production-ready interface
- No authentication bypass or context errors

## Risk Mitigation

1. **Incremental Implementation**: Build and test each pillar independently
2. **Backend-First Approach**: Leverage existing backend capabilities
3. **Real Data Only**: Never use mock data or stubs
4. **User Context Validation**: Ensure proper multi-tenant isolation
5. **Performance Monitoring**: Track and optimize performance throughout

## Conclusion

This updated plan leverages the sophisticated backend architecture to create a production-ready frontend that delivers the complete MVP vision. By consolidating the fragmented frontend architecture and fully utilizing the backend's micro-module capabilities, we can create a unified, intelligent platform that provides real business value to users.

The key insight is that the backend has already solved the complex business logic problems - we just need to create a frontend that properly interfaces with these capabilities and provides an intuitive user experience for the complete MVP journey.
