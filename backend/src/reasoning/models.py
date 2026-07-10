from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReasoningInput(BaseModel):
    """
    Input model for the AI reasoning pipeline.
    Captures the direct action predicted by the SVM.
    """
    container: str = Field(description="Name of the affected container")
    error_type: str = Field(description="The detected error type or AI diagnosis label")
    severity: str = Field(description="Severity (e.g. ERROR, CRITICAL)")
    suggested_fix: str = Field(description="The specific Action string predicted by the AI model")
    confidence: float = Field(description="Confidence score of the AI prediction")
    
    # NEW: Added to support dynamic, non-hardcoded reporting
    root_cause: Optional[str] = Field(None, description="Detailed root cause explanation")
    original_log: Optional[str] = Field(None, description="The raw log text that was analyzed")

class IncidentReport(BaseModel):
    """
    Final report model for the Frontend and Incident History.
    """
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    container: str
    error_type: str
    suggested_fix: str
    action_taken: str
    resolution_status: str
    
    # NEW: Added to ensure the dashboard timeline shows unique AI data
    root_cause: Optional[str] = None
    confidence: Optional[str] = None
    
    # NEW: Specific command or action taken for "Hot Fixes"
    detailed_fix: Optional[str] = None