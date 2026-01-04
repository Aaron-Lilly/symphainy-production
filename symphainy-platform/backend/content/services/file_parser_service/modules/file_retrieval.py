#!/usr/bin/env python3
"""
File Retrieval Module - File Parser Service

Handles file/document retrieval operations.
REUSED from existing implementation - no changes needed.
"""

from typing import Dict, Any, Optional


class FileRetrieval:
    """File retrieval module for File Parser Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def retrieve_document(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve file via Data Steward SOA API (Smart City service).
        
        Business Enablement services should use Smart City APIs, not direct infrastructure access.
        Data Steward wraps Public Works file_management and exposes it as an SOA API.
        Note: Content Steward consolidated into Data Steward.
        
        Args:
            file_id: ID of file to retrieve
            
        Returns:
            File data with metadata, or None if not found
        """
        try:
            # Tier 1: Try SOA API (Data Steward - Content Steward consolidated)
            self.service.logger.info(f"🔍 FileParserService.retrieve_document({file_id})")
            
            if not self.service.data_steward:
                self.service.logger.warning(f"⚠️ Data Steward API not available (self.data_steward is None), trying Platform Gateway")
            else:
                try:
                    self.service.logger.info(f"   Calling data_steward.get_file({file_id})")
                    file_record = await self.service.data_steward.get_file(file_id)
                    if file_record:
                        # Data Steward returns file with file_content, not data
                        # Check if it's a valid file record (has uuid or file_content)
                        if file_record.get("uuid") or file_record.get("file_content") is not None:
                            self.service.logger.info(f"✅ File retrieved via Data Steward: {file_id}")
                            return file_record
                        else:
                            self.service.logger.warning(f"⚠️ Data Steward returned empty record: {file_id}, trying Platform Gateway")
                    else:
                        self.service.logger.warning(f"⚠️ File not found via Data Steward (returned None): {file_id}, trying Platform Gateway")
                except Exception as e:
                    self.service.logger.warning(f"⚠️ Data Steward failed: {e}, trying Platform Gateway")
                    import traceback
                    self.service.logger.debug(f"   Data Steward error traceback: {traceback.format_exc()}")
            
            # Tier 2: Fallback to Platform Gateway (file_management abstraction)
            try:
                file_management = self.service.get_abstraction("file_management")
                if file_management:
                    self.service.logger.info(f"   Calling file_management.get_file({file_id})")
                    file_record = await file_management.get_file(file_id)
                    if file_record:
                        self.service.logger.info(f"✅ File retrieved via Platform Gateway: {file_id}")
                        return file_record
            except Exception as e:
                self.service.logger.warning(f"⚠️ Platform Gateway failed: {e}")
            
            # Tier 3: Fail gracefully with structured error
            self.service.logger.error(f"❌ Failed to retrieve file {file_id} - tried Data Steward and Platform Gateway")
            return {
                "success": False,
                "error": "File retrieval failed",
                "error_code": "FILE_NOT_FOUND",
                "message": f"Could not retrieve file {file_id}. Tried Data Steward SOA API and Platform Gateway - both unavailable or file not found.",
                "file_id": file_id
            }
            
        except Exception as e:
            self.service.logger.error(f"❌ Failed to retrieve file {file_id}: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            # Tier 3: Fail gracefully with structured error
            return {
                "success": False,
                "error": "File retrieval exception",
                "error_code": "FILE_RETRIEVAL_EXCEPTION",
                "message": f"Exception while retrieving file {file_id}: {e}",
                "file_id": file_id
            }



