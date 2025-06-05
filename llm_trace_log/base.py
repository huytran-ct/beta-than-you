import datetime
from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class LangFuseGenerationDataModel(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    completion_start_time: Optional[datetime.datetime] = None
    model: Optional[str] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    level: Optional[str] = None
    status_message: Optional[str] = None
    version: Optional[str] = None
    tag: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class LangFuseSpanDataModel(BaseModel):
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[str] = None
    level: Optional[str] = None
    status_message: Optional[str] = None
    version: Optional[str] = None
    tag: Optional[List[str]] = None
