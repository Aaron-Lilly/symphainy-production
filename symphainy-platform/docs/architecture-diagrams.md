# Architecture Diagrams

This document contains visual architecture diagrams for SymphAIny Platform. Diagrams are created using Mermaid and can be rendered in GitHub, documentation sites, or Mermaid-compatible viewers.

---

## Platform Architecture

```mermaid
graph TB
    subgraph "Heads (Experience Foundation SDK)"
        Frontend[React Frontend]
        Mobile[Mobile App]
        ERP[ERP Systems]
        CRM[CRM Systems]
        CLI[CLI Tools]
        API[API Clients]
    end
    
    subgraph "Experience Foundation"
        ExpSDK[Experience SDK]
        GatewayBuilder[Frontend Gateway Builder]
        SessionBuilder[Session Manager Builder]
        UXBuilder[User Experience Builder]
    end
    
    subgraph "Smart City Realm"
        CityMgr[City Manager]
        Security[Security Guard]
        Librarian[Librarian]
        Content[Content Steward]
        Data[Data Steward]
        PostOffice[Post Office]
        TrafficCop[Traffic Cop]
        Nurse[Nurse]
        Conductor[Conductor]
    end
    
    subgraph "Solution Realm"
        SolMgr[Solution Manager]
        SolOrch[Solution Orchestrator]
    end
    
    subgraph "Journey Realm"
        JourMgr[Journey Manager]
        JourOrch[Journey Orchestrator]
    end
    
    subgraph "Business Enablement Realm"
        DelMgr[Delivery Manager]
        Pillars[4 Pillars]
    end
    
    subgraph "Foundation Services"
        DI[DI Container]
        PublicWorks[Public Works Foundation]
        Curator[Curator Foundation]
        Comm[Communication Foundation]
        Agentic[Agentic Foundation]
    end
    
    Frontend -.->|SDK| ExpSDK
    Mobile -.->|SDK| ExpSDK
    ERP -.->|SDK| ExpSDK
    CRM -.->|SDK| ExpSDK
    CLI -.->|SDK| ExpSDK
    API -.->|SDK| ExpSDK
    
    ExpSDK --> GatewayBuilder
    ExpSDK --> SessionBuilder
    ExpSDK --> UXBuilder
    
    GatewayBuilder --> SolMgr
    SolMgr --> JourMgr
    JourMgr --> DelMgr
    DelMgr --> Pillars
    
    Pillars --> CityMgr
    CityMgr --> Security
    CityMgr --> Librarian
    CityMgr --> Content
    CityMgr --> Data
    
    CityMgr --> PublicWorks
    PublicWorks --> DI
    Curator --> DI
    Comm --> DI
    Agentic --> DI
    ExpSDK --> DI
```

---

## Realm Architecture

```mermaid
graph LR
    subgraph "Smart City Realm"
        SC[Smart City Services]
        SC_Desc["Platform Initiation<br/>Startup<br/>Enablement"]
    end
    
    subgraph "Solution Realm"
        SOL[Solution Services]
        SOL_Desc["Solution Orchestration<br/>User-Centric Routing"]
    end
    
    subgraph "Journey Realm"
        JOUR[Journey Services]
        JOUR_Desc["Journey Orchestration<br/>MVP Execution"]
    end
    
    subgraph "Business Enablement Realm"
        BE[Business Enablement Services]
        BE_Desc["4-Pillar<br/>Business Enablement"]
    end
    
    SC --> SOL
    SOL --> JOUR
    JOUR --> BE
    
    BE --> SC
```

---

## Infrastructure Abstraction

```mermaid
graph TB
    subgraph "Realm Services"
        RS[Realm Service]
    end
    
    subgraph "Platform Gateway"
        PG[Platform Gateway]
        VAL[Validation]
    end
    
    subgraph "Public Works Foundation"
        PWF[Public Works Foundation]
        ABS[Abstractions]
        REG[Registries]
    end
    
    subgraph "Infrastructure Adapters"
        ADAPT1[Redis Adapter]
        ADAPT2[ArangoDB Adapter]
        ADAPT3[GCS Adapter]
        ADAPT4[Custom Adapter]
    end
    
    subgraph "Infrastructure"
        INF1[Redis]
        INF2[ArangoDB]
        INF3[Google Cloud Storage]
        INF4[Custom Infrastructure]
    end
    
    RS --> PG
    PG --> VAL
    VAL --> PWF
    PWF --> ABS
    ABS --> REG
    REG --> ADAPT1
    REG --> ADAPT2
    REG --> ADAPT3
    REG --> ADAPT4
    
    ADAPT1 --> INF1
    ADAPT2 --> INF2
    ADAPT3 --> INF3
    ADAPT4 --> INF4
```

---

## Service Discovery

```mermaid
graph TB
    subgraph "Services"
        S1[Service 1]
        S2[Service 2]
        S3[Service 3]
    end
    
    subgraph "Curator Foundation"
        CF[Curator Foundation]
        REG[Service Registry]
        CAP[Capability Registry]
        SOA[SOA API Registry]
        MCP[MCP Tool Registry]
    end
    
    subgraph "Discovery"
        DISC[Service Discovery]
        LOOKUP[Capability Lookup]
    end
    
    S1 --> CF
    S2 --> CF
    S3 --> CF
    
    CF --> REG
    CF --> CAP
    CF --> SOA
    CF --> MCP
    
    REG --> DISC
    CAP --> LOOKUP
    SOA --> DISC
    MCP --> LOOKUP
```

---

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Head as "Head (Frontend/ERP/CRM)"
    participant ExpSDK as "Experience Foundation SDK"
    participant Solution Realm
    participant Journey Realm
    participant Business Enablement
    participant Smart City
    participant Public Works
    
    User->>Head: Request
    Head->>ExpSDK: SDK Call
    ExpSDK->>Solution Realm: Route Request
    Solution Realm->>Journey Realm: Orchestrate Journey
    Journey Realm->>Business Enablement: Execute Pillar
    Business Enablement->>Smart City: Use Platform Service
    Smart City->>Public Works: Get Abstraction
    Public Works-->>Smart City: Abstraction
    Smart City-->>Business Enablement: Result
    Business Enablement-->>Journey Realm: Result
    Journey Realm-->>Solution Realm: Result
    Solution Realm-->>ExpSDK: Result
    ExpSDK-->>Head: Response
    Head-->>User: Display Result
```

---

## Infrastructure Swapping

```mermaid
graph LR
    subgraph "Application Code"
        APP[Business Logic]
    end
    
    subgraph "Abstraction Layer"
        ABS[Infrastructure Abstraction]
    end
    
    subgraph "Adapter Options"
        ADAPT1[Redis Adapter]
        ADAPT2[Memcached Adapter]
        ADAPT3[In-Memory Adapter]
    end
    
    subgraph "Infrastructure"
        INF1[Redis]
        INF2[Memcached]
        INF3[In-Memory]
    end
    
    APP --> ABS
    ABS --> ADAPT1
    ABS --> ADAPT2
    ABS --> ADAPT3
    
    ADAPT1 -.->|Swap| ADAPT2
    ADAPT2 -.->|Swap| ADAPT3
    
    ADAPT1 --> INF1
    ADAPT2 --> INF2
    ADAPT3 --> INF3
```

---

## Headless Architecture (Experience Foundation)

```mermaid
graph TB
    subgraph "Heads (Experience Foundation SDK)"
        REACT[React App]
        VUE[Vue App]
        MOBILE[Mobile App]
        ERP[ERP Systems]
        CRM[CRM Systems]
        CLI[CLI Tool]
        API_CLIENT[API Client]
    end
    
    subgraph "Experience Foundation"
        ExpSDK[Experience SDK]
        GatewayBuilder[Frontend Gateway Builder]
        SessionBuilder[Session Manager Builder]
        UXBuilder[User Experience Builder]
    end
    
    subgraph "Platform Core"
        CORE[Platform Services]
        Realms[4 Realms]
    end
    
    REACT -.->|SDK| ExpSDK
    VUE -.->|SDK| ExpSDK
    MOBILE -.->|SDK| ExpSDK
    ERP -.->|SDK| ExpSDK
    CRM -.->|SDK| ExpSDK
    CLI -.->|SDK| ExpSDK
    API_CLIENT -.->|SDK| ExpSDK
    
    ExpSDK --> GatewayBuilder
    ExpSDK --> SessionBuilder
    ExpSDK --> UXBuilder
    
    GatewayBuilder --> CORE
    SessionBuilder --> CORE
    UXBuilder --> CORE
    
    CORE --> Realms
```

---

**Note**: These diagrams are placeholders. Actual mermaid diagrams should be created based on the current architecture implementation. Diagrams can be rendered in:
- GitHub (native Mermaid support)
- Documentation sites (MkDocs, Docusaurus, etc.)
- Mermaid Live Editor: https://mermaid.live

