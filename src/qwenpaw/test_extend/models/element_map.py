# -*- coding: utf-8 -*-
"""Element mapping model for UI automation.

Maps semantic element names to stable selectors (data-testid, aria, CSS).
Each element map belongs to a project, defining how to locate page elements.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ElementMap(BaseModel):
    id: str = Field(default_factory=lambda: "", description="Unique element map ID")
    project_id: str = Field(default="", description="Associated project ID")
    page_name: str = Field(default="", description="Page name or route")
    mapping: dict[str, str] = Field(default_factory=dict, description="name → selector map")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
