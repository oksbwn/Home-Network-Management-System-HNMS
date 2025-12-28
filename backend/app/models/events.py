from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceEvent(BaseModel):
    id: str
    device_id: str
    status: str
    changed_at: datetime
    # Joined fields
    ip: Optional[str] = None
    display_name: Optional[str] = None
    icon: Optional[str] = None
    device_type: Optional[str] = None

class EventStats(BaseModel):
    timestamp: datetime
    online_count: int
    offline_count: int
