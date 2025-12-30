from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClassificationRuleBase(BaseModel):
    name: str
    pattern_hostname: Optional[str] = None
    pattern_vendor: Optional[str] = None
    ports: List[int] = []
    device_type: str
    icon: str
    priority: int = 100

class ClassificationRuleCreate(ClassificationRuleBase):
    pass

class ClassificationRuleUpdate(BaseModel):
    name: Optional[str] = None
    pattern_hostname: Optional[str] = None
    pattern_vendor: Optional[str] = None
    ports: Optional[List[int]] = None
    device_type: Optional[str] = None
    icon: Optional[str] = None
    priority: Optional[int] = None

class ClassificationRule(ClassificationRuleBase):
    id: str
    is_builtin: bool
    updated_at: datetime

    class Config:
        from_attributes = True
