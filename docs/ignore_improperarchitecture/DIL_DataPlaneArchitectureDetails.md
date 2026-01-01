Deep Dive on the DIL Data Plane/Tactical Architecture

1. WHAT DATA INFRASTRUCTURE YOU NEED TO ADD (Updated)


Already in your stack (great foundation):
Redis → Upstash / MemoryStore

Arango → Oasis

Supabase

Meilisearch Cloud

HuggingFace / OpenAI / Anthropic

GCS/S3

Consul (+ eventually Consul Connect)

OPA for policy enforcement



Additions recommended for the Tactical Data Plane:


🔹 
(A) A Data Contract/Schema Registry


Not Kafka-Schema-Registry — lightweight JSON-schema or Pydantic-based.



Purposes:

Central place to store semantic model definitions

Store agent config templates

Store data pipeline contracts

Store embedding schemas + provenance schemas

Store WAL/Saga contract definitions



Implementation:

Supabase Postgres (simplest)

Wrap with: data_intel_contract_store



🔹 
(B) A Metadata/Provenance Store (lightweight AMUNDSEN-ish)


You can use Arango as a graph-based metadata store:

Node types:

FileAsset

ParseEvent

EmbeddingEvent

AgentCall

FeedbackEvent

SemanticEntity

WALStep / SagaInstance

Edges capture:

lineage

corrections

reviewers

confidence

transformations



You already have Arango — so this is just a model layer, no new infra.



🔹 
(C) Event Stream / Audit-Log fabric (optional)


OPA audit logs + your WAL/Saga events should be persisted in:

Supabase (cheap + fully managed) OR

Redis streams (if very high throughput)



But no new infra is required here.

2. WHAT ADAPTERS YOU NEED TO CREATE (Updated)


Adapters = concrete implementations of Python protocol contracts.



🔶 
Adapter Category 1 — Storage Adapters


Implement protocol contracts like:

class FileStorage(Protocol):
    def put(self, path: str, bytes: bytes) -> str: ...
    def get(self, path: str) -> bytes: ...
    def exists(self, path: str) -> bool: ...
You provide adapters:

GcsFileStorageAdapter

S3FileStorageAdapter

SupabaseFileStorageAdapter (if needed)

🔶 
Adapter Category 2 — Database Adapters


For Arango:

class VectorStore(Protocol):
    def upsert_embedding(self, id: str, vector: list[float], meta: dict): ...
    def query(self, vector: list[float], top_k: int): ...
Adapters you implement:

ArangoVectorStoreAdapter

ArangoMetadataAdapter (lineage, reviews, agent logs)

🔶 
Adapter Category 3 — LLM/Embedding Adapters
class EmbeddingProvider(Proto):
    def embed_text(self, text: str) -> EmbeddingResult: ...
    def embed_table(self, table: list[dict]) -> EmbeddingResult: ...
    def embed_document(self, bytes: bytes) -> EmbeddingResult: ...
Adapters:

HuggingFaceStatelessAdapter

OpenAIEmbeddingAdapter

AnthropicEmbeddingAdapter

🔶 
Adapter Category 4 — OPA Policy Adapter


OPA becomes a pluggable governance service:

class PolicyEvaluator(Protocol):
    def evaluate(self, input: dict) -> PolicyDecision: ...
Adapter:

OPAHTTPAdapter (HTTP POST → /v1/data/...)

🔶 
Adapter Category 5 — Consul/Service Registry Adapters


You don’t need heavy abstractions here — just:

ServiceDiscoveryAdapter

KVConfigAdapter

3. WHAT CONTACTS / COMPOSITION SERVICES ARE REQUIRED (Updated)


Contacts = stable, typed, domain-facing API surfaces inside the platform.

Composition services = orchestrate adapters + contracts into capabilities.



Here’s the updated taxonomy:

🟧 
Contact: FileParseContact
Input: file reference

Output: ParsedText, ParsedTable, HybridParse



Uses adapters:

FileStorage

PolicyEvaluator

MetadataAdapter

🟧 
Contact: EmbeddingContact
Input: parsed components

Route to the correct embedding pipeline via LLM adapters

Log results to Arango

Emit traceability & confidence

🟧 
Contact: SemanticEntityContact
Input: embedding outputs

Reference the semantic model schema from the Contract Store

Convert raw embeddings → typed semantic entities

Persist in Arango + Meilisearch

🟧 
Contact: AgentExecutionContact


Captures:

agent ID

input prompt

output

trace/context window

corrections/feedback

confidence

tools called



Uses the contract store to resolve:

agent JSON config template

MCP tool definitions

Prompt scaffolding

🟧 
Contact: WAL/SagaContact
 (NOW PART OF DIL Foundation)


Provides:

Begin WAL transaction

Append WAL event

Begin Saga

Log saga step

Compensate

Finalize



Backed by:

Supabase

Or Redis streams

4. WHAT ABSTRACTIONS YOU NEED TO CREATE (Updated + Clean Split)


Abstraction Layer 1 — Contract Abstractions (Python Protocols)


These define shape + semantics without binding to infra.

FileStorage

VectorStore

MetadataRepository

SemanticModelRepository

EmbeddingProvider

AgentExecutor

PolicyEvaluator

WorkflowOrchestrator (for sagas)

WALTransaction



These are all pure Python protocols (PEP 544).

Abstraction Layer 2 — Domain Abstractions (Tactical DIL)


Domain-level logical constructs:

ParsedFile

EmbeddingEvent

SemanticEntity

AgentEvent

FeedbackAnnotation

WALRecord

SagaInstance

Abstraction Layer 3 — Capability Abstractions (exposed to Realms)
Parse → Embed → Align → Persist (PEAP pipeline)

Semantic search

Data mash combinators

Agent interaction + learning store

Robust lineage queries

Event Replay

Governance guardrails (OPA)



These live inside the DIL Foundation.

5. WHERE THEY ARE EXPOSED (Updated)


🟦 (A) Exposed to Foundations


Data Intelligence SDK (recommended)
YES — you should expose an SDK.

Why?

Your agent configs, semantic models, workflows, and embeddings are composable, developer-facing concepts.

Teams will build new realm services and agents; they need shared primitives.

Industry direction (Palantir, Snowflake Polaris, Promethium) all provide SDKs for:

querying semantic models

publishing metadata

running transformations

storing pipeline lineage

emitting audit events



What the DIL SDK should include


Lightweight Python API:

from dil import embed, parse, track, semantic, wal, saga
Capabilities:

parse_file(file_ref)

embed_text(text)

emit_agent_event(agent_id, prompt, output, meta)

record_feedback(entity_id, correction)

wal.begin(), wal.append(), wal.commit()

saga.begin(), saga.step(), saga.compensate()

🟧 (B) Exposed to Smart City Foundation


Use cases:

Governance

Security/tenancy

SOA API exposure

MCP tool registration

Tracing/telemetry at the platform level



Smart City exposes:

Semantic entity retrieval

Embedding review endpoints

Lineage inspection

Feedback submission

Agent-call browse endpoints

🟩 (C) Exposed to Realm Services


Realm teams consume:

DIL SDK

SOA APIs

MCP Tools



The realms DO NOT directly access infrastructure.

They consume only contract-bound capabilities.



This ensures portability whether deployed on-prem, locally, or SaaS.

⭐ FINAL RECOMMENDATION (Short Version)


YES, Data Intelligence absolutely should expose an SDK


It becomes:

the semantic layer entry point

the metadata and lineage API

the agent event + feedback ingestion pipeline

the WAL/Saga orchestration primitive

the runtime contract resolver



This is exactly what Palantir Foundry, Promethium, and Snowflake are doing