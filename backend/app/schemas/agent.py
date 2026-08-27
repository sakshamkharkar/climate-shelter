from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ToolCallLog(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Dict[str, Any]
    timestamp: str

class AgentRunRequest(BaseModel):
    user_prompt: str = "Design a thermally efficient shelter for Leh, Ladakh."
    location_name: Optional[str] = "Leh, Ladakh"
    latitude: Optional[float] = 34.1526
    longitude: Optional[float] = 77.5771

class AgentRunResponse(BaseModel):
    response: str
    tool_calls: List[ToolCallLog] = Field(default_factory=list)
    recommended_design: Optional[Dict[str, Any]] = None
    environmental_summary: Optional[Dict[str, Any]] = None
    validation_summary: Optional[Dict[str, Any]] = None
