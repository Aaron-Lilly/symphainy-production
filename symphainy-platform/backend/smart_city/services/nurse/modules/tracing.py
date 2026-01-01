#!/usr/bin/env python3
"""
Nurse Service - Tracing Module

Micro-module for distributed tracing using Telemetry Abstraction (OpenTelemetry + Tempo).
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TraceSpan


class Tracing:
    """Tracing module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def start_trace(self, trace_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Start a distributed trace using Tempo infrastructure."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            trace_id = str(uuid.uuid4())
            
            # Start trace via Telemetry Abstraction (which handles Tempo)
            trace_span = TraceSpan(
                name=trace_name,
                trace_id=trace_id,
                span_id=str(uuid.uuid4()),
                start_time=datetime.utcnow(),
                end_time=None,
                attributes=context or {},
                events=[]
            )
            
            success = await self.service.telemetry_abstraction.collect_trace(trace_span)
            
            if success:
                # Track active trace (backward compatibility)
                self.service.active_traces[trace_id] = {
                    "trace_id": trace_id,
                    "trace_name": trace_name,
                    "context": context or {},
                    "started_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Trace started: {trace_name} ({trace_id})")
                return trace_id
            else:
                raise Exception("Failed to start trace via Tempo")
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error starting trace: {str(e)}")
            raise e
    
    async def add_span(self, trace_id: str, span_name: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """Add a span to an existing trace using Tempo infrastructure."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            span_id = str(uuid.uuid4())
            
            # Add span via Telemetry Abstraction
            trace_span = TraceSpan(
                name=span_name,
                trace_id=trace_id,
                span_id=span_id,
                start_time=datetime.utcnow(),
                end_time=None,
                attributes=attributes or {},
                events=[]
            )
            
            success = await self.service.telemetry_abstraction.collect_trace(trace_span)
            
            if success:
                # Track span in active trace (backward compatibility)
                if trace_id in self.service.active_traces:
                    if "spans" not in self.service.active_traces[trace_id]:
                        self.service.active_traces[trace_id]["spans"] = []
                    self.service.active_traces[trace_id]["spans"].append({
                        "span_id": span_id,
                        "span_name": span_name,
                        "attributes": attributes or {},
                        "started_at": datetime.utcnow().isoformat()
                    })
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Span added: {span_name} to trace {trace_id}")
                return span_id
            else:
                raise Exception("Failed to add span via Tempo")
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error adding span: {str(e)}")
            raise e
    
    async def end_trace(self, trace_id: str, status: str = "success") -> bool:
        """End a distributed trace using Tempo infrastructure."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # End trace via Telemetry Abstraction
            if trace_id in self.service.active_traces:
                trace_data = self.service.active_traces[trace_id]
                
                # Create final span to mark trace end
                end_span = TraceSpan(
                    name="trace_end",
                    trace_id=trace_id,
                    span_id=str(uuid.uuid4()),
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow(),
                    attributes={"status": status},
                    events=[]
                )
                
                success = await self.service.telemetry_abstraction.collect_trace(end_span)
                
                if success:
                    # Update local trace status (backward compatibility)
                    self.service.active_traces[trace_id]["status"] = status
                    self.service.active_traces[trace_id]["ended_at"] = datetime.utcnow().isoformat()
                    
                    if self.service.logger:
                        self.service.logger.info(f"✅ Trace ended: {trace_id} ({status})")
                    return True
                else:
                    return False
            else:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Trace not found: {trace_id}")
                return False
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error ending trace: {str(e)}")
            return False
    
    async def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve trace data from Tempo infrastructure."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get trace from Telemetry Abstraction (traces are stored in Tempo via telemetry)
            # Note: Telemetry Abstraction handles traces, so we can query via active_traces
            # In production, this would query Tempo directly via the abstraction
            
            if trace_id in self.service.active_traces:
                trace_data = self.service.active_traces[trace_id].copy()
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Trace retrieved: {trace_id}")
                return {
                    "trace_id": trace_id,
                    "trace_data": trace_data,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "trace_id": trace_id,
                    "trace_data": None,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "not_found"
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error getting trace: {str(e)}")
            return {
                "trace_id": trace_id,
                "trace_data": None,
                "error": str(e),
                "status": "error"
            }






