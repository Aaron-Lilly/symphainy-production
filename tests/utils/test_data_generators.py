"""
Test data generators for creating test data.

Provides utilities for generating realistic test data for all test categories.
"""

from faker import Faker
from typing import Dict, List, Any, Optional
import random
from datetime import datetime, timedelta

fake = Faker()


def generate_user_context(tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a realistic user context for testing.
    
    Args:
        tenant_id: Optional tenant ID (default: generated)
    
    Returns:
        User context dictionary
    """
    return {
        "user_id": fake.uuid4(),
        "tenant_id": tenant_id or fake.uuid4(),
        "email": fake.email(),
        "name": fake.name(),
        "permissions": ["read", "write", "execute"],
        "roles": ["user"],
    }


def generate_file_metadata(
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate file metadata for testing.
    
    Args:
        filename: Optional filename (default: generated)
        content_type: Optional content type (default: Excel)
        size: Optional file size in bytes (default: random)
    
    Returns:
        File metadata dictionary
    """
    return {
        "filename": filename or f"{fake.word()}.xlsx",
        "content_type": content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size": size or random.randint(1024, 10240),
        "uploaded_at": datetime.utcnow().isoformat(),
    }


def generate_structured_data(rows: int = 10, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate structured data for testing.
    
    Args:
        rows: Number of rows to generate
        columns: Optional column names (default: id, name, value, date)
    
    Returns:
        Structured data dictionary
    """
    if columns is None:
        columns = ["id", "name", "value", "date"]
    
    data_rows = []
    for i in range(rows):
        row = {
            "id": i + 1,
            "name": fake.word().title(),
            "value": random.randint(1, 1000),
            "date": fake.date().isoformat(),
        }
        data_rows.append(row)
    
    return {
        "columns": columns,
        "rows": data_rows,
        "row_count": rows,
    }


def generate_unstructured_data(length: int = 500) -> Dict[str, Any]:
    """
    Generate unstructured text data for testing.
    
    Args:
        length: Approximate text length in characters
    
    Returns:
        Unstructured data dictionary
    """
    return {
        "text": fake.text(max_nb_chars=length),
        "metadata": {
            "title": fake.sentence(nb_words=5),
            "author": fake.name(),
            "date": fake.date().isoformat(),
            "source": fake.url(),
        },
    }


def generate_saga_operation(
    operation_name: str,
    status: str = "pending",
    milestones: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a Saga operation for testing.
    
    Args:
        operation_name: Name of the operation
        status: Operation status
        milestones: Optional list of milestones
    
    Returns:
        Saga operation dictionary
    """
    if milestones is None:
        milestones = ["start", "process", "complete"]
    
    return {
        "saga_id": fake.uuid4(),
        "operation_name": operation_name,
        "status": status,
        "milestones": milestones,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def generate_workflow_steps(count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate workflow steps for testing.
    
    Args:
        count: Number of steps to generate
    
    Returns:
        List of workflow step dictionaries
    """
    steps = []
    for i in range(count):
        steps.append({
            "step_id": i + 1,
            "name": fake.sentence(nb_words=3),
            "description": fake.sentence(nb_words=10),
            "action": random.choice(["process", "validate", "transform", "store"]),
            "dependencies": [j + 1 for j in range(i) if random.random() > 0.7],
        })
    return steps


def generate_sop_sections(count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate SOP sections for testing.
    
    Args:
        count: Number of sections to generate
    
    Returns:
        List of SOP section dictionaries
    """
    sections = []
    section_types = ["overview", "procedure", "requirements", "validation", "troubleshooting"]
    
    for i in range(count):
        sections.append({
            "section_id": i + 1,
            "title": fake.sentence(nb_words=4),
            "type": section_types[i % len(section_types)],
            "content": fake.paragraph(nb_sentences=5),
            "order": i + 1,
        })
    return sections




