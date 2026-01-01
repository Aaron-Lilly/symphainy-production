#!/usr/bin/env python3
"""
Database Broker MCP Server - Core Data Infrastructure

This MCP server abstracts structured data storage operations, combining functionality from:
- database_server: SQLite database operations, schema management, data quality
- business_server: ArangoDB operations, business data management, knowledge search

Provides a unified interface for structured data storage across the Smart City platform.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import sqlite3
import asyncio
from contextlib import asynccontextmanager

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import base class
from common.utilities.domain_bases import Core4MCPBase

class DatabaseBrokerMCPServer(Core4MCPBase):
    """
    Database Broker MCP Server - abstracts structured data storage operations
    
    This server provides a unified interface for structured data storage across the Smart City platform,
    combining SQLite operations with ArangoDB capabilities for business data management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Database Broker MCP Server."""
        # Initialize base class with service name and domain
        super().__init__("database_broker", "core4")
        
        # Keep existing initialization
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Server metadata
        self.name = "database_broker"
        self.version = "1.0.0"
        self.status = "active"
        
        # Database configuration
        self.database_backends = self.config.get("database_backends", ["sqlite", "arangodb"])
        self.default_backend = self.config.get("default_backend", "sqlite")
        self.database_path = self.config.get("database_path", "./data/database.db")
        
        # Business data configuration
        self.business_roots = [
            "./data/business_experience",  # Business experience files
            "./data/business_insights",    # Business insights and analytics
            "./data/business_metadata",    # Business metadata and schemas
            "./data/business_operations",  # Business operations files
            "./data/business_content",     # Business content files
            "./data/business_files"        # General business files
        ]
        
        # Database connections
        self.sqlite_connection = None
        self.arangodb_client = None
        
        # Performance tracking
        self.operation_count = 0
        self.total_query_time = 0.0
        
        # Initialize databases
        self._initialize_databases()
        
        # Define MCP tools
        self.tools = [
            "execute_query",
            "create_table",
            "insert_data",
            "update_data",
            "delete_data",
            "get_schema",
            "validate_data",
            "get_data_quality",
            "query_arangodb",
            "list_collections",
            "search_knowledge",
            "get_business_data",
            "create_business_record",
            "update_business_record",
            "delete_business_record",
            "get_database_stats"
        ]
        
        # Define MCP resources
        self.resources = [
            "/database/schema.json",
            "/database/stats.json",
            "/database/quality_report.json",
            "/business/collections.json",
            "/business/knowledge_base.json"
        ]
        
        # Define MCP prompts
        self.prompts = [
            "How to query structured data",
            "Database schema management",
            "Data quality validation",
            "Business data operations",
            "ArangoDB AQL queries"
        ]
        
        self.logger.info(f"Database Broker MCP Server initialized with database: {self.database_path}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the MCP server."""
        logger = logging.getLogger("database_broker_mcp")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_databases(self):
        """Initialize database connections and create sample data."""
        # Initialize SQLite
        self._initialize_sqlite()
        
        # Initialize ArangoDB (mock for now)
        self._initialize_arangodb()
        
        # Ensure business directories exist
        for root in self.business_roots:
            Path(root).mkdir(parents=True, exist_ok=True)
    
    def _initialize_sqlite(self):
        """Initialize SQLite database connection and create sample tables."""
        try:
            # Ensure database directory exists
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.sqlite_connection = sqlite3.connect(self.database_path)
            self.sqlite_connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create sample tables
            self._create_sample_tables()
            
            self.logger.info("SQLite database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SQLite database: {e}")
            raise
    
    def _create_sample_tables(self):
        """Create sample tables for testing and demonstration."""
        try:
            cursor = self.sqlite_connection.cursor()
            
            # Data objects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_objects (
                    id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id TEXT PRIMARY KEY,
                    data_object_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT,
                    data_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_object_id) REFERENCES data_objects (id)
                )
            """)
            
            # Data quality table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality (
                    id TEXT PRIMARY KEY,
                    data_object_id TEXT,
                    quality_score REAL,
                    validation_rules TEXT,
                    issues TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_object_id) REFERENCES data_objects (id)
                )
            """)
            
            # Business data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_data (
                    id TEXT PRIMARY KEY,
                    business_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Insert sample data
            self._insert_sample_data(cursor)
            
            self.sqlite_connection.commit()
            self.logger.info("Sample tables and data created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create sample tables: {e}")
            raise
    
    def _insert_sample_data(self, cursor):
        """Insert sample data for testing."""
        try:
            # Sample data objects
            sample_objects = [
                ("obj_001", "user_profile", '{"name": "John Doe", "email": "john@example.com"}', '{"source": "registration", "priority": "high"}'),
                ("obj_002", "product_catalog", '{"name": "Widget Pro", "price": 99.99}', '{"category": "electronics", "inventory": 50}'),
                ("obj_003", "order_data", '{"order_id": "ORD_001", "total": 199.98}', '{"status": "pending", "customer_id": "CUST_001"}'),
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO data_objects (id, data_type, content, metadata)
                VALUES (?, ?, ?, ?)
            """, sample_objects)
            
            # Sample metadata
            sample_metadata = [
                ("meta_001", "obj_001", "verification_status", "verified", "string"),
                ("meta_002", "obj_001", "last_login", "2024-01-15", "datetime"),
                ("meta_003", "obj_002", "supplier", "TechCorp Inc", "string"),
                ("meta_004", "obj_003", "shipping_method", "express", "string"),
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO metadata (id, data_object_id, key, value, data_type)
                VALUES (?, ?, ?, ?)
            """, sample_metadata)
            
            # Sample data quality
            sample_quality = [
                ("qual_001", "obj_001", 0.95, '["email_format", "name_length"]', '[]'),
                ("qual_002", "obj_002", 0.88, '["price_range", "inventory_positive"]', '["price_missing_currency"]'),
                ("qual_003", "obj_003", 0.92, '["order_id_format", "total_positive"]', '[]'),
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO data_quality (id, data_object_id, quality_score, validation_rules, issues)
                VALUES (?, ?, ?, ?, ?)
            """, sample_quality)
            
            # Sample business data
            sample_business = [
                ("biz_001", "customer_profile", '{"name": "Acme Corp", "industry": "Technology"}', '{"tier": "enterprise", "region": "US"}'),
                ("biz_002", "product_catalog", '{"name": "Enterprise Widget", "price": 999.99}', '{"category": "enterprise", "inventory": 100}'),
                ("biz_003", "order_data", '{"order_id": "BIZ_001", "total": 1999.98}', '{"status": "processing", "customer_id": "biz_001"}'),
            ]
            
            cursor.executemany("""
                INSERT OR REPLACE INTO business_data (id, business_type, content, metadata)
                VALUES (?, ?, ?, ?)
            """, sample_business)
            
        except Exception as e:
            self.logger.warning(f"Failed to insert sample data: {e}")
    
    def _initialize_arangodb(self):
        """Initialize ArangoDB client (mock implementation for now)."""
        try:
            # Mock ArangoDB client - in production, this would be a real ArangoDB client
            self.arangodb_client = {
                "connected": True,
                "collections": ["business_data", "customer_profiles", "product_catalog", "orders"],
                "version": "3.11.0"
            }
            
            self.logger.info("ArangoDB client initialized (mock)")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize ArangoDB client: {e}")
            self.arangodb_client = {"connected": False}
    
    # ============================================================================
    # MCP TOOLS - SQLite Operations
    # ============================================================================
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a database query and return results.
        
        Args:
            query: SQL query string
            parameters: Query parameters
            
        Returns:
            Query execution result
        """
        start_time = datetime.now()
        self.operation_count += 1
        
        try:
            cursor = self.sqlite_connection.cursor()
            
            if parameters:
                # Convert dict parameters to list for SQLite
                param_list = list(parameters.values())
                cursor.execute(query, param_list)
            else:
                cursor.execute(query)
            
            # Handle different query types
            query_upper = query.strip().upper()
            if query_upper.startswith('SELECT') or query_upper.startswith('PRAGMA') or query_upper.startswith('SHOW'):
                results = cursor.fetchall()
                # Convert to list of dicts
                columns = [description[0] for description in cursor.description]
                rows = [dict(zip(columns, row)) for row in results]
                
                result = {
                    "type": "select",
                    "rows": rows,
                    "count": len(rows),
                    "columns": columns
                }
            else:
                # INSERT, UPDATE, DELETE
                self.sqlite_connection.commit()
                result = {
                    "type": "modify",
                    "affected_rows": cursor.rowcount,
                    "last_row_id": cursor.lastrowid
                }
            
            # Track performance
            end_time = datetime.now()
            query_time = (end_time - start_time).total_seconds()
            self.total_query_time += query_time
            
            self.logger.info(f"Query executed successfully: {query[:50]}...")
            
            return {
                "success": True,
                "result": result,
                "execution_time": query_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute query: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_table(self, table_name: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new table with the specified schema.
        
        Args:
            table_name: Name of the table to create
            schema: Table schema definition
            
        Returns:
            Table creation result
        """
        try:
            # Build CREATE TABLE statement from schema
            columns = []
            for column_name, column_def in schema.items():
                columns.append(f"{column_name} {column_def}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            
            result = self.execute_query(create_sql)
            
            if result["success"]:
                self.logger.info(f"Table created successfully: {table_name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create table: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into a table.
        
        Args:
            table_name: Name of the table
            data: Data to insert
            
        Returns:
            Insert result
        """
        try:
            columns = list(data.keys())
            placeholders = ['?' for _ in columns]
            values = list(data.values())
            
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            # Execute directly with values instead of using execute_query
            cursor = self.sqlite_connection.cursor()
            cursor.execute(insert_sql, values)
            self.sqlite_connection.commit()
            
            result = {
                "success": True,
                "affected_rows": cursor.rowcount,
                "last_row_id": cursor.lastrowid
            }
            
            self.logger.info(f"Data inserted successfully into {table_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to insert data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_data(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update data in a table.
        
        Args:
            table_name: Name of the table
            data: Data to update
            where_clause: WHERE clause
            where_params: WHERE clause parameters
            
        Returns:
            Update result
        """
        try:
            set_clauses = [f"{key} = ?" for key in data.keys()]
            set_sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            # Combine data and where parameters
            all_params = list(data.values())
            if where_params:
                all_params.extend(list(where_params.values()))
            
            # Execute directly with values
            cursor = self.sqlite_connection.cursor()
            cursor.execute(set_sql, all_params)
            self.sqlite_connection.commit()
            
            result = {
                "success": True,
                "affected_rows": cursor.rowcount
            }
            
            self.logger.info(f"Data updated successfully in {table_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_data(self, table_name: str, where_clause: str, where_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Delete data from a table.
        
        Args:
            table_name: Name of the table
            where_clause: WHERE clause
            where_params: WHERE clause parameters
            
        Returns:
            Delete result
        """
        try:
            delete_sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            params = []
            if where_params:
                params = list(where_params.values())
            
            # Execute directly with values
            cursor = self.sqlite_connection.cursor()
            cursor.execute(delete_sql, params)
            self.sqlite_connection.commit()
            
            result = {
                "success": True,
                "affected_rows": cursor.rowcount
            }
            
            self.logger.info(f"Data deleted successfully from {table_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_schema(self, table_name: str = None) -> Dict[str, Any]:
        """
        Get database schema information.
        
        Args:
            table_name: Specific table name (optional)
            
        Returns:
            Schema information
        """
        try:
            if table_name:
                # Get specific table schema
                query = f"PRAGMA table_info({table_name})"
                result = self.execute_query(query)
                
                if result["success"]:
                    columns = result["result"]["rows"]
                    schema = {
                        "table_name": table_name,
                        "columns": columns
                    }
                else:
                    return result
            else:
                # Get all tables
                query = "SELECT name FROM sqlite_master WHERE type='table'"
                result = self.execute_query(query)
                
                if result["success"]:
                    tables = [row["name"] for row in result["result"]["rows"]]
                    schema = {
                        "tables": tables,
                        "table_count": len(tables)
                    }
                else:
                    return result
            
            return {
                "success": True,
                "schema": schema
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get schema: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_data(self, table_name: str, data: Dict[str, Any], validation_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate data against schema and rules.
        
        Args:
            table_name: Name of the table
            data: Data to validate
            validation_rules: Custom validation rules
            
        Returns:
            Validation result
        """
        try:
            # Get table schema
            schema_result = self.get_schema(table_name)
            if not schema_result["success"]:
                return schema_result
            
            # Basic validation
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields
            required_fields = [col["name"] for col in schema_result["schema"]["columns"] if not col["notnull"] == 0]
            for field in required_fields:
                if field not in data:
                    validation_result["errors"].append(f"Required field missing: {field}")
                    validation_result["valid"] = False
            
            # Check data types (basic)
            for col in schema_result["schema"]["columns"]:
                col_name = col["name"]
                if col_name in data:
                    # Basic type checking
                    if col["type"].upper() == "INTEGER" and not isinstance(data[col_name], int):
                        validation_result["warnings"].append(f"Field {col_name} should be integer")
                    elif col["type"].upper() == "TEXT" and not isinstance(data[col_name], str):
                        validation_result["warnings"].append(f"Field {col_name} should be text")
            
            # Custom validation rules
            if validation_rules:
                for rule_name, rule_func in validation_rules.items():
                    try:
                        if not rule_func(data):
                            validation_result["errors"].append(f"Validation rule failed: {rule_name}")
                            validation_result["valid"] = False
                    except Exception as e:
                        validation_result["warnings"].append(f"Validation rule error: {rule_name} - {str(e)}")
            
            return {
                "success": True,
                "validation": validation_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_data_quality(self, table_name: str = None) -> Dict[str, Any]:
        """
        Get data quality metrics.
        
        Args:
            table_name: Specific table name (optional)
            
        Returns:
            Data quality metrics
        """
        try:
            if table_name:
                # Get quality for specific table
                query = """
                    SELECT dq.*, do.data_type, do.status
                    FROM data_quality dq
                    JOIN data_objects do ON dq.data_object_id = do.id
                    WHERE do.data_type = ?
                """
                result = self.execute_query(query, {"values": [table_name]})
            else:
                # Get overall quality metrics
                query = """
                    SELECT 
                        AVG(quality_score) as avg_quality,
                        MIN(quality_score) as min_quality,
                        MAX(quality_score) as max_quality,
                        COUNT(*) as total_records
                    FROM data_quality
                """
                result = self.execute_query(query)
            
            if result["success"]:
                return {
                    "success": True,
                    "quality_metrics": result["result"]["rows"]
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get data quality: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # MCP TOOLS - ArangoDB Operations (Mock)
    # ============================================================================
    
    def query_arangodb(self, collection: str, query: str, bind_vars: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query ArangoDB collection (mock implementation).
        
        Args:
            collection: Collection name
            query: AQL query string
            bind_vars: Bind variables
            
        Returns:
            Query result
        """
        try:
            if not self.arangodb_client.get("connected", False):
                return {
                    "success": False,
                    "error": "ArangoDB client not connected"
                }
            
            # Mock query result
            mock_result = {
                "collection": collection,
                "query": query,
                "bind_vars": bind_vars or {},
                "result": [
                    {"_key": "doc1", "name": "Sample Document 1", "type": "business"},
                    {"_key": "doc2", "name": "Sample Document 2", "type": "business"}
                ],
                "count": 2
            }
            
            self.logger.info(f"ArangoDB query executed (mock): {collection}")
            
            return {
                "success": True,
                "result": mock_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to query ArangoDB: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_collections(self) -> Dict[str, Any]:
        """
        List available ArangoDB collections.
        
        Returns:
            List of collections
        """
        try:
            if not self.arangodb_client.get("connected", False):
                return {
                    "success": False,
                    "error": "ArangoDB client not connected"
                }
            
            collections = self.arangodb_client.get("collections", [])
            
            return {
                "success": True,
                "collections": collections,
                "count": len(collections)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_knowledge(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search knowledge base for relevant information.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            # Mock knowledge search
            mock_results = [
                {
                    "id": "kb_001",
                    "title": "Smart City Data Management",
                    "content": "Best practices for managing data in smart city environments...",
                    "relevance_score": 0.95,
                    "tags": ["data", "smart_city", "management"]
                },
                {
                    "id": "kb_002", 
                    "title": "Business Process Automation",
                    "content": "How to automate business processes using AI and machine learning...",
                    "relevance_score": 0.88,
                    "tags": ["automation", "business", "ai"]
                }
            ]
            
            # Filter results based on query
            filtered_results = [result for result in mock_results if query.lower() in result["title"].lower() or query.lower() in result["content"].lower()]
            
            return {
                "success": True,
                "results": filtered_results[:limit],
                "count": len(filtered_results),
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Failed to search knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # MCP TOOLS - Business Data Operations
    # ============================================================================
    
    def get_business_data(self, business_type: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get business data records.
        
        Args:
            business_type: Type of business data to retrieve
            limit: Maximum number of records
            
        Returns:
            Business data records
        """
        try:
            if business_type:
                query = "SELECT * FROM business_data WHERE business_type = ? LIMIT ?"
                result = self.execute_query(query, {"param1": business_type, "param2": limit})
            else:
                query = "SELECT * FROM business_data LIMIT ?"
                result = self.execute_query(query, {"param1": limit})
            
            if result["success"]:
                return {
                    "success": True,
                    "business_data": result["result"]["rows"],
                    "count": result["result"]["count"]
                }
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get business data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_business_record(self, business_type: str, content: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new business record.
        
        Args:
            business_type: Type of business record
            content: Record content
            metadata: Record metadata
            
        Returns:
            Creation result
        """
        try:
            record_id = str(uuid.uuid4())
            data = {
                "id": record_id,
                "business_type": business_type,
                "content": json.dumps(content),
                "metadata": json.dumps(metadata or {}),
                "status": "active"
            }
            
            result = self.insert_data("business_data", data)
            
            if result["success"]:
                self.logger.info(f"Business record created: {record_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create business record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_business_record(self, record_id: str, content: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update an existing business record.
        
        Args:
            record_id: Record ID to update
            content: Updated content
            metadata: Updated metadata
            
        Returns:
            Update result
        """
        try:
            update_data = {}
            if content:
                update_data["content"] = json.dumps(content)
            if metadata:
                update_data["metadata"] = json.dumps(metadata)
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            result = self.update_data("business_data", update_data, "id = ?", {"id": record_id})
            
            if result["success"]:
                self.logger.info(f"Business record updated: {record_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update business record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_business_record(self, record_id: str) -> Dict[str, Any]:
        """
        Delete a business record.
        
        Args:
            record_id: Record ID to delete
            
        Returns:
            Delete result
        """
        try:
            result = self.delete_data("business_data", "id = ?", {"id": record_id})
            
            if result["success"]:
                self.logger.info(f"Business record deleted: {record_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete business record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Database statistics
        """
        try:
            # Get table counts
            tables_result = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            if not tables_result["success"]:
                return tables_result
            
            table_names = [row["name"] for row in tables_result["result"]["rows"]]
            
            # Get record counts for each table
            table_stats = {}
            for table_name in table_names:
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                if count_result["success"]:
                    table_stats[table_name] = count_result["result"]["rows"][0]["count"]
            
            # Get overall stats
            stats = {
                "total_tables": len(table_names),
                "table_stats": table_stats,
                "total_operations": self.operation_count,
                "total_query_time": self.total_query_time,
                "average_query_time": self.total_query_time / max(self.operation_count, 1),
                "database_backends": self.database_backends,
                "default_backend": self.default_backend,
                "arangodb_connected": self.arangodb_client.get("connected", False)
            }
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # MCP RESOURCES
    # ============================================================================
    
    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Get MCP resource data.
        
        Args:
            resource_path: Resource path
            
        Returns:
            Resource data
        """
        if resource_path == "/database/schema.json":
            return self.get_schema()
        elif resource_path == "/database/stats.json":
            return self.get_database_stats()
        elif resource_path == "/database/quality_report.json":
            return self.get_data_quality()
        elif resource_path == "/business/collections.json":
            return self.list_collections()
        elif resource_path == "/business/knowledge_base.json":
            return self.search_knowledge("", limit=100)
        else:
            return {
                "success": False,
                "error": f"Unknown resource: {resource_path}"
            }
    
    # ============================================================================
    # MCP USAGE GUIDE
    # ============================================================================
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for this MCP server."""
        return {
            "server": self.name,
            "version": self.version,
            "status": self.status,
            "purpose": "Structured data storage abstraction for Smart City platform",
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "examples": [
                "database_broker.execute_query('SELECT * FROM data_objects LIMIT 10')",
                "database_broker.insert_data('business_data', {'business_type': 'customer', 'content': '{}'})",
                "database_broker.query_arangodb('business_data', 'FOR doc IN business_data RETURN doc')",
                "database_broker.search_knowledge('smart city data management')"
            ],
            "configuration": {
                "database_backends": self.database_backends,
                "default_backend": self.default_backend,
                "database_path": self.database_path
            }
        }
    
    def call_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Call a tool by name.
        
        Args:
            tool_name: Name of the tool to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            method = getattr(self, tool_name)
            return method(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to call tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
