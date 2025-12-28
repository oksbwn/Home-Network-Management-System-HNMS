from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceRead(BaseModel):
    id: str
    ip: str
    mac: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    device_type: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    vendor: Optional[str] = None
    icon: Optional[str] = None
    status: Optional[str] = "unknown"
    open_ports: Optional[list] = []
    attributes: Optional[dict] = {}

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    device_type: Optional[str] = None
    vendor: Optional[str] = None
    icon: Optional[str] = None
    attributes: Optional[str] = None
