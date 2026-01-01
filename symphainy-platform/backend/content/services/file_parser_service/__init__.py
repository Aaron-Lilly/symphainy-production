"""
File Parser Service Package

WHAT: Parses files into structured formats across multiple file types
HOW: Provides unified file parsing APIs via micro-modules with parsing type determination
"""

from .file_parser_service import FileParserService

__all__ = ["FileParserService"]



