# 🏗️ Data Mash Technical Design

**How to Build Virtual Composition on Your Platform**

---

## 🎯 THE CORE CHALLENGE

**Data Mash Requirement:**
> Query across distributed data sources without moving data (Virtual Composition)

**Current Gap:**
Your platform can orchestrate workflows but not federate queries in real-time.

**Solution:**
Enhance Data Steward with query federation OR create Data Compositor role.

---

## 🏛️ ARCHITECTURE OPTIONS

### **Option 1: Enhanced Data Steward (MVP - 4-6 weeks)**

```python
# backend/smart_city/services/data_steward/data_steward_service.py

class DataStewardService(SmartCityRoleBase):
    """
    WHAT: I manage data quality, transformations, and lineage
    HOW: I use Public Works abstractions + AI for data operations
    
    NEW: I also orchestrate federated queries across distributed sources
    """
    
    def __init__(self, di_container):
        super().__init__(
            service_name="DataStewardService",
            role_name="DataSteward",
            di_container=di_container
        )
        
        # Existing capabilities
        self.schema_validator = None
        self.transformation_engine = None
        self.lineage_tracker = None
        
        # NEW: Federated query capabilities
        self.query_federator = None
        self.source_connectors = {}
        self.query_optimizer = None
    
    # ========================================
    # NEW MODULE: federated_query.py
    # ========================================
    
    async def execute_federated_query(
        self,
        query: Dict[str, Any],
        sources: List[Dict[str, Any]],
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Execute query across multiple sources without moving data.
        
        Args:
            query: Query specification (fields to retrieve, filters, etc.)
            sources: List of data sources to query
            mappings: Field mappings (source_field -> query_field)
        
        Returns:
            Aggregated results from all sources
        
        Example:
            query = {
                "fields": ["policy_id", "premium_amount", "effective_date"],
                "filters": {"policy_status": "active"}
            }
            sources = [
                {"type": "database", "connection": "legacy_postgres", "table": "policies"},
                {"type": "api", "endpoint": "https://fast.example.com/policies"}
            ]
            mappings = {
                "pol_num": "policy_id",  # Legacy field -> standard field
                "premium": "premium_amount"
            }
        """
        # Step 1: Validate query and sources
        await self.validate_federated_query(query, sources, mappings)
        
        # Step 2: Optimize query plan (using AI)
        query_plan = await self.optimize_query_plan(query, sources)
        
        # Step 3: Translate query for each source
        source_queries = await self.translate_query_for_sources(
            query, sources, mappings
        )
        
        # Step 4: Execute queries in parallel (using Conductor)
        raw_results = await self.execute_parallel_queries(source_queries)
        
        # Step 5: Harmonize and aggregate results
        harmonized_results = await self.harmonize_results(
            raw_results, mappings
        )
        
        # Step 6: Track virtual composition for audit
        await self.track_virtual_composition(
            query, sources, harmonized_results
        )
        
        return harmonized_results
    
    async def translate_query_for_sources(
        self,
        query: Dict[str, Any],
        sources: List[Dict[str, Any]],
        mappings: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Translate standard query to source-specific queries.
        
        Uses:
        - Schema mappings from lineage tracker
        - AI for semantic translation
        """
        translated_queries = []
        
        for source in sources:
            if source["type"] == "database":
                # Translate to SQL
                sql_query = await self._translate_to_sql(
                    query, source, mappings
                )
                translated_queries.append({
                    "source": source,
                    "query": sql_query,
                    "type": "sql"
                })
            
            elif source["type"] == "api":
                # Translate to API call
                api_query = await self._translate_to_api_call(
                    query, source, mappings
                )
                translated_queries.append({
                    "source": source,
                    "query": api_query,
                    "type": "api"
                })
            
            elif source["type"] == "file":
                # Translate to file query
                file_query = await self._translate_to_file_query(
                    query, source, mappings
                )
                translated_queries.append({
                    "source": source,
                    "query": file_query,
                    "type": "file"
                })
        
        return translated_queries
    
    async def execute_parallel_queries(
        self,
        source_queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute queries in parallel using Conductor.
        
        Uses:
        - Conductor: Orchestrate parallel execution
        - Post Office: Coordinate result collection
        - Traffic Cop: Route queries to appropriate endpoints
        """
        # Use Conductor to orchestrate
        conductor = await self.get_conductor_api()
        
        # Create parallel workflow
        workflow = await conductor.create_workflow({
            "name": "federated_query_execution",
            "type": "parallel",
            "steps": [
                {
                    "name": f"query_source_{i}",
                    "action": self._execute_single_query,
                    "params": {"query": sq}
                }
                for i, sq in enumerate(source_queries)
            ]
        })
        
        # Execute and collect results
        results = await conductor.execute_workflow(workflow)
        
        return results
    
    async def _execute_single_query(
        self,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute query against a single source."""
        source = query["source"]
        query_spec = query["query"]
        query_type = query["type"]
        
        # Get appropriate connector
        connector = self.source_connectors.get(source["type"])
        
        if not connector:
            raise ValueError(f"No connector for source type: {source['type']}")
        
        # Execute query
        result = await connector.execute_query(source, query_spec)
        
        return {
            "source": source,
            "data": result,
            "metadata": {
                "row_count": len(result) if isinstance(result, list) else 1,
                "execution_time": result.get("execution_time")
            }
        }
    
    async def harmonize_results(
        self,
        raw_results: List[Dict[str, Any]],
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Harmonize results from multiple sources into unified format.
        
        Uses:
        - Field mappings to standardize field names
        - AI for semantic harmonization (e.g., date format differences)
        """
        harmonized_data = []
        
        for result in raw_results:
            source_data = result["data"]
            
            # Apply field mappings
            for row in source_data:
                harmonized_row = {}
                for source_field, target_field in mappings.items():
                    if source_field in row:
                        harmonized_row[target_field] = row[source_field]
                
                harmonized_data.append(harmonized_row)
        
        return {
            "data": harmonized_data,
            "metadata": {
                "total_rows": len(harmonized_data),
                "sources": [r["source"] for r in raw_results],
                "mappings_applied": mappings
            }
        }
```

---

### **Option 2: Data Compositor Role (Full Vision - 12-16 weeks)**

```python
# backend/smart_city/services/data_compositor/data_compositor_service.py

class DataCompositorService(SmartCityRoleBase):
    """
    Data Compositor Service - Federated Data Orchestration
    
    WHAT: I orchestrate federated queries across distributed data sources
    HOW: I use Conductor + Data Steward + AI to compose virtual data views
    
    The "Symphony Conductor" for Data Mash.
    """
    
    def __init__(self, di_container):
        super().__init__(
            service_name="DataCompositorService",
            role_name="DataCompositor",
            di_container=di_container
        )
        
        # Smart City service dependencies
        self.data_steward = None  # Schema validation, transformations
        self.conductor = None  # Workflow orchestration
        self.post_office = None  # Cross-source coordination
        self.librarian = None  # Metadata storage
        self.insights_pillar = None  # AI-powered query optimization
        
        # Composition capabilities
        self.virtual_views = {}  # Active virtual compositions
        self.source_registry = {}  # Registered data sources
        self.query_cache = {}  # Cached query results
        
        # Micro-modules
        self.virtual_composition_module = VirtualComposition(self)
        self.query_federation_module = QueryFederation(self)
        self.source_connector_module = SourceConnector(self)
        self.query_optimization_module = QueryOptimization(self)
        self.result_harmonization_module = ResultHarmonization(self)
        self.soa_mcp_module = SoaMcp(self)
    
    # ========================================
    # CORE CAPABILITY: Virtual Composition
    # ========================================
    
    async def create_virtual_view(
        self,
        view_name: str,
        sources: List[Dict[str, Any]],
        mappings: Dict[str, str],
        relationships: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a virtual view across distributed sources.
        
        This is the "Data Mash Layer" - a just-in-time data fabric.
        
        Args:
            view_name: Name for this virtual view
            sources: Data sources to include
            mappings: Field mappings across sources
            relationships: How to join/relate sources (optional)
        
        Returns:
            Virtual view specification (no data moved yet)
        
        Example:
            view = await compositor.create_virtual_view(
                view_name="policy_migration_view",
                sources=[
                    {"name": "legacy_policies", "type": "postgres", ...},
                    {"name": "fast_policies", "type": "api", ...}
                ],
                mappings={
                    "legacy_policies.pol_num": "policy_id",
                    "fast_policies.policyId": "policy_id",
                    "legacy_policies.premium": "premium_amount"
                },
                relationships=[
                    {
                        "left": "legacy_policies.pol_num",
                        "right": "fast_policies.policyId",
                        "type": "outer_join"
                    }
                ]
            )
        """
        return await self.virtual_composition_module.create_view(
            view_name, sources, mappings, relationships
        )
    
    async def query_virtual_view(
        self,
        view_name: str,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Query a virtual view without moving data.
        
        This is where the "magic" happens - data stays at source,
        but you can query across all sources as if they were one.
        """
        return await self.query_federation_module.execute_query(
            view_name, query
        )
    
    async def materialize_virtual_view(
        self,
        view_name: str,
        destination: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Materialize a virtual view into physical data.
        
        This is the "Execution Layer" - convert virtual into real.
        """
        # Get virtual view specification
        view_spec = self.virtual_views.get(view_name)
        
        # Use Conductor to orchestrate materialization
        conductor = await self.get_conductor_api()
        
        workflow = await conductor.create_workflow({
            "name": f"materialize_{view_name}",
            "steps": [
                {"action": "extract", "sources": view_spec["sources"]},
                {"action": "transform", "mappings": view_spec["mappings"]},
                {"action": "load", "destination": destination}
            ]
        })
        
        result = await conductor.execute_workflow(workflow)
        
        # Track in Data Steward for lineage
        data_steward = await self.get_data_steward_api()
        await data_steward.track_lineage({
            "source": view_spec,
            "destination": destination,
            "workflow": workflow,
            "result": result
        })
        
        return result
    
    async def dissolve_virtual_view(
        self,
        view_name: str
    ) -> bool:
        """
        Dissolve a virtual view when no longer needed.
        
        This is the "just-in-time" aspect - compositions are temporary.
        """
        if view_name in self.virtual_views:
            del self.virtual_views[view_name]
            
            # Clear cache
            if view_name in self.query_cache:
                del self.query_cache[view_name]
            
            return True
        
        return False
    
    # ========================================
    # SOA API Exposure
    # ========================================
    
    async def initialize_soa_api_exposure(self):
        """Expose Data Compositor capabilities as SOA APIs."""
        self.soa_apis = {
            "create_virtual_view": {
                "description": "Create virtual view across distributed sources",
                "handler": self.create_virtual_view
            },
            "query_virtual_view": {
                "description": "Query virtual view without moving data",
                "handler": self.query_virtual_view
            },
            "materialize_virtual_view": {
                "description": "Materialize virtual view into physical data",
                "handler": self.materialize_virtual_view
            },
            "dissolve_virtual_view": {
                "description": "Dissolve virtual view when done",
                "handler": self.dissolve_virtual_view
            }
        }
    
    # ========================================
    # MCP Tools Exposure
    # ========================================
    
    async def initialize_mcp_tool_integration(self):
        """Expose Data Compositor capabilities as MCP Tools."""
        self.mcp_tools = {
            "create_data_mash": {
                "description": "Create Data Mash virtual composition",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "view_name": {"type": "string"},
                        "sources": {"type": "array"},
                        "mappings": {"type": "object"}
                    }
                },
                "handler": self.create_virtual_view
            },
            "query_data_mash": {
                "description": "Query Data Mash without moving data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "view_name": {"type": "string"},
                        "query": {"type": "object"}
                    }
                },
                "handler": self.query_virtual_view
            }
        }
```

---

## 🔌 SOURCE CONNECTORS

```python
# backend/smart_city/services/data_compositor/modules/source_connectors/
# OR (for MVP): backend/smart_city/services/data_steward/modules/source_connectors/

class SourceConnectorBase:
    """Base class for data source connectors."""
    
    async def connect(self, source: Dict[str, Any]) -> bool:
        """Establish connection to source."""
        raise NotImplementedError
    
    async def execute_query(
        self,
        source: Dict[str, Any],
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute query against source."""
        raise NotImplementedError
    
    async def disconnect(self, source: Dict[str, Any]) -> bool:
        """Close connection to source."""
        raise NotImplementedError


class PostgreSQLConnector(SourceConnectorBase):
    """Connector for PostgreSQL databases."""
    
    async def execute_query(self, source, query):
        # Translate to SQL and execute
        pass


class RESTAPIConnector(SourceConnectorBase):
    """Connector for REST APIs."""
    
    async def execute_query(self, source, query):
        # Translate to HTTP requests
        pass


class FileConnector(SourceConnectorBase):
    """Connector for files (CSV, JSON, Parquet, etc.)."""
    
    async def execute_query(self, source, query):
        # Read file and filter
        pass


class OracleConnector(SourceConnectorBase):
    """Connector for Oracle databases."""
    
    async def execute_query(self, source, query):
        # Translate to Oracle SQL
        pass
```

---

## 🧠 AI-POWERED QUERY OPTIMIZATION

```python
# modules/query_optimization.py

class QueryOptimization:
    """AI-powered query optimization for federated queries."""
    
    def __init__(self, service):
        self.service = service
        self.insights_pillar = None  # AI analysis
    
    async def optimize_query_plan(
        self,
        query: Dict[str, Any],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use AI to optimize query execution plan.
        
        Considers:
        - Source performance characteristics
        - Data volume at each source
        - Network latency
        - Query complexity
        - Join strategies
        """
        # Use Insights Pillar + AI agents
        insights = await self.insights_pillar.analyze_query_optimization({
            "query": query,
            "sources": sources,
            "historical_performance": self.service.query_cache
        })
        
        # Generate optimized plan
        optimized_plan = {
            "execution_order": insights["recommended_order"],
            "parallelization": insights["parallelizable_queries"],
            "caching_strategy": insights["cache_recommendations"],
            "estimated_cost": insights["estimated_execution_time"]
        }
        
        return optimized_plan
```

---

## 📊 USE CASE EXAMPLE

```python
# Example: Insurance Policy Migration with Data Mash

async def migrate_policies_with_data_mash():
    """
    Example: Use Data Compositor to test migration before moving data.
    """
    
    # Step 1: Create virtual view across legacy + FAST
    compositor = await get_data_compositor()
    
    virtual_view = await compositor.create_virtual_view(
        view_name="policy_migration_preview",
        sources=[
            {
                "name": "legacy_db",
                "type": "postgres",
                "connection": "postgresql://legacy.db/insurance",
                "table": "policies"
            },
            {
                "name": "fast_api",
                "type": "api",
                "endpoint": "https://fast.example.com/api/policies"
            }
        ],
        mappings={
            # Legacy -> Standard
            "legacy_db.pol_num": "policy_id",
            "legacy_db.pol_holder": "policy_holder_name",
            "legacy_db.premium": "premium_amount",
            "legacy_db.eff_date": "effective_date",
            
            # FAST -> Standard
            "fast_api.policyId": "policy_id",
            "fast_api.premiumAmount": "premium_amount"
        },
        relationships=[
            {
                "left": "legacy_db.pol_num",
                "right": "fast_api.policyId",
                "type": "outer_join"  # See which exist in both, legacy only, FAST only
            }
        ]
    )
    
    # Step 2: Query virtual view to find data quality issues
    quality_check = await compositor.query_virtual_view(
        view_name="policy_migration_preview",
        query={
            "fields": [
                "policy_id",
                "policy_holder_name",
                "premium_amount",
                "effective_date",
                "_source"  # Which source: legacy, fast, both
            ],
            "filters": {
                "or": [
                    {"premium_amount": {"is_null": True}},  # Missing premiums
                    {"effective_date": {"invalid_format": True}},  # Bad dates
                    {"_source": "legacy_only"}  # Not yet in FAST
                ]
            }
        }
    )
    
    print(f"Found {quality_check['metadata']['total_rows']} data quality issues")
    print(f"Issues breakdown:")
    print(f"  - Missing premiums: {quality_check['stats']['null_premiums']}")
    print(f"  - Invalid dates: {quality_check['stats']['invalid_dates']}")
    print(f"  - Not migrated: {quality_check['stats']['legacy_only']}")
    
    # Step 3: Fix issues in source systems (no data moved yet!)
    # ... client fixes data ...
    
    # Step 4: Re-query to verify fixes
    recheck = await compositor.query_virtual_view(
        view_name="policy_migration_preview",
        query={"filters": {"_has_issues": True}}
    )
    
    print(f"Remaining issues: {recheck['metadata']['total_rows']}")
    
    # Step 5: When satisfied, materialize (execute migration)
    if recheck['metadata']['total_rows'] == 0:
        migration_result = await compositor.materialize_virtual_view(
            view_name="policy_migration_preview",
            destination={
                "type": "database",
                "connection": "postgresql://prod.db/insurance",
                "table": "policies_migrated"
            }
        )
        
        print(f"✅ Migrated {migration_result['rows_migrated']} policies")
    
    # Step 6: Dissolve virtual view
    await compositor.dissolve_virtual_view("policy_migration_preview")
```

---

## ✅ IMPLEMENTATION CHECKLIST

### **MVP (4-6 weeks) - Enhanced Data Steward**

**Week 1-2: Source Connectors**
- [ ] Create `SourceConnectorBase`
- [ ] Implement `PostgreSQLConnector`
- [ ] Implement `RESTAPIConnector`
- [ ] Implement `FileConnector`
- [ ] Add connector registry to Data Steward

**Week 3-4: Query Federation**
- [ ] Add `execute_federated_query()` to Data Steward
- [ ] Implement query translation logic
- [ ] Add parallel execution using Conductor
- [ ] Implement result harmonization

**Week 5: Virtual View Management**
- [ ] Add virtual view storage
- [ ] Implement query caching
- [ ] Add lineage tracking for virtual compositions

**Week 6: Testing & Documentation**
- [ ] E2E test with sample sources
- [ ] Performance benchmarking
- [ ] Client documentation
- [ ] Demo environment

---

### **Full Vision (12-16 weeks) - Data Compositor Role**

**Week 7-8: Data Compositor Service**
- [ ] Create new Smart City role
- [ ] Implement `SmartCityRoleBase`
- [ ] Micro-modular architecture (7 modules)
- [ ] Register with Curator

**Week 9-11: Advanced Federation**
- [ ] Query optimization engine
- [ ] AI-powered query planning (Insights Pillar integration)
- [ ] Advanced join strategies
- [ ] Result caching with invalidation

**Week 12-13: Production Features**
- [ ] Connection pooling
- [ ] Query performance monitoring
- [ ] Cost estimation
- [ ] Multi-tenancy support

**Week 14-15: Security & Governance**
- [ ] Zero-trust validation
- [ ] Data access audit trails
- [ ] Policy integration
- [ ] Encryption in transit

**Week 16: Hardening**
- [ ] Load testing
- [ ] Production deployment
- [ ] Client training
- [ ] Sales enablement

---

## 🎯 SUCCESS METRICS

**Technical:**
- ✅ Query 3+ sources without ETL
- ✅ < 5 second response time for typical queries
- ✅ Support 100+ concurrent virtual views
- ✅ 99.9% uptime

**Business:**
- ✅ Reduce migration risk by 80% (find issues before moving data)
- ✅ Accelerate migration timeline by 50% (faster testing)
- ✅ Enable parallel processing (old + new systems in sync)
- ✅ 2-10X ROI on first client

---

_Technical design document  
Version: 1.0  
Date: November 4, 2024_











