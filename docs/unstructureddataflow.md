unstructured data is conceptually a sibling to your structured semantic pipeline, but it requires different extraction and normalization techniques. The core principles — semantic inference, HITL validation, universal exposure layer, multi-tenant governance — still apply. Let’s break this down carefully in your context.

I. Treat Unstructured Data as Its Own Journey/Flow


Yes — you’re correct: it’s a different solution/journey, because the input type and extraction method are fundamentally different.

Structured Flow: Columns → metadata → semantic ID → contract → pipeline

Unstructured Flow: Documents/claims → NLP extraction → normalized entities & relationships → semantic graph → contract → downstream AI or operator workflows



But the semantic layer philosophy remains identical: everything maps to a shared semantic ontology, enabling cross-client reasoning, matchmaking, and interoperability.

II. Layer 1 — Canonical Models (Metadata Layer)


Think of this as structured abstraction of unstructured inputs:

Input Sources:

Policy PDFs, scanned legacy documents

Claim files (structured + unstructured)

Vendor requirements, regional regulations

Extraction / Normalization Pipeline:

Step

Component

Output

Text Extraction

OCR + PDF parsers + text cleaners

Raw text

Entity Extraction

LLMs, NER models, regex heuristics

Entities: policies, rules, amounts, locations

Relation Extraction

LLM or knowledge graph inference

Relationships: Vendor → Experiment, Exercise → Location

Canonical Mapping

Semantic inference / embedding → Global semantic IDs

Normalized semantic graph nodes & edges

Metadata Enrichment

Contextual metadata, confidence scores, provenance

Augmented entity nodes

Output:

Shared Semantic Graph: Nodes = normalized entities; edges = relationships

Confidence/Explanation Metadata per node/edge

Semantic graph can now feed the Matchmaking/Coexistence layer



Key Principle:

This mirrors your structured pipeline: everything maps to universal meaning, but the nodes are entities extracted from text instead of columns.

III. Layer 2 — The Matchmaking Engine (Coexistence Layer)


Once the semantic graph exists:

Scorecards & Dashboards:

Evaluate alignment: requirements vs. capabilities

Highlight matches, gaps, or conflicts

AI-Enabled Constraint Monitoring:

Rules engine / predictive agent monitors semantic graph nodes

Sends alerts when constraints are violated (e.g., policy overlap, location conflict)

Operator Interaction:

HITL agents for override, adjustment, or approval

Feedback feeds semantic graph confidence scores → improves automated matching

Ongoing Learning:

Multi-tenant: models learn relationships, extraction patterns, normalization heuristics

Cross-client learning strengthens entity recognition and relationship inference



Key Principle:

The same over-the-top design applies: multi-tenant semantic graph + agent-driven orchestration + HITL validation. Only the input modality differs.

IV. Hybrid Use Case — Canonical Metadata + Matchmaking


Your example fits neatly into this abstraction:

Layer

Core Output

Agents / Orchestrators

Notes

Layer 1 — Canonical Models

Normalized semantic graph of Vendor Test Requirements, Experiment Opportunities, Exercise Opportunities, Location Parameters

Profiling Agent, NLP Extraction Agent, Semantic Mapping Agent

Map every entity to universal semantic IDs; attach confidence scores; optional de-identification

Layer 2 — Matchmaking Engine

AI-enabled scoring, alerts, dashboards, schedules

Matchmaking Agent, Constraint Monitoring Agent, Experience/UI Agents

Operators interact via Experience Foundation; HITL feedback updates confidence; orchestration ensures multi-client safety

Observation:

This design allows you to reuse existing platform abstractions:

Agents are stateless or use MCP tools

Semantic IDs from structured flow and unstructured flow live in the same universal semantic graph

Cross-domain reasoning is enabled (e.g., structured policy + extracted unstructured requirements → match client capabilities)

V. Implementation Notes (High-Level, Deferred)
Text-to-Semantic Graph:

LLMs + embedding + entity extraction

Confidence scores attached to every node/edge

Graph stored in Arango / Neo4j or hybrid solution

Normalization / HITL Review:

Experience Foundation UI presents entities + inferred semantic mapping

Human approves/rejects/edits → stored in semantic_mapping_history

Updates flow to universal semantic graph

Matchmaking & Monitoring:

Agents evaluate semantic graph for rules, gaps, conflicts

Scorecards, dashboards, alerting based on confidence and constraints

Operators intervene via Experience Foundation

Cross-Tenant Learning:

Extract patterns from multiple clients

Update global models (NLP extractors, semantic clustering, relation inference)

No client data leaves tenant context; only model weights and embedding patterns are shared

VI. Summary of Principles That Carry Over from Structured Flow
Principle

Structured Flow

Unstructured Flow

Semantic IDs

Columns → semantic ID

Entities → semantic ID

HITL validation

Approve column → semantic mapping

Approve entity → semantic mapping

Contracts

Column → semantic contract

Entity → semantic contract

Learning

Cross-client mapping patterns

Cross-client extraction & relationship patterns

Multi-Tenant Safety

Smart City governance, agents, adapters

Same governance + stateless NLP agents

Coexistence / Migration

Legacy → SEL → Target

Extracted semantic graph → operational flows → dashboards/alerts

Bottom line: Unstructured flow is another journey, but the same platform abstractions and governance patterns apply. Semantic IDs become your common currency, enabling multi-tenant reasoning, matchmaking, and ongoing improvement.