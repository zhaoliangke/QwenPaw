# -*- coding: utf-8 -*-
"""Knowledge document model for the test platform knowledge base."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str = ""
    product_line: str = ""
    doc_type: str = "general"
    tags: list[str] = Field(default_factory=list)
    iteration_id: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
