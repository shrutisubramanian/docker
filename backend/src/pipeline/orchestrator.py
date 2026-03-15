import logging
from datetime import datetime
from backend.src.reasoning.models import ReasoningInput, IncidentReport
from backend.src.recovery.decision_mapper import map_issue_to_action
from backend.src.recovery.docker_recovery import execute_recovery_action
from backend.src.logging.incident_logger import log_incident

def process_reasoning_alert(alert: ReasoningInput) -> IncidentReport:
    """
    Orchestrates the dynamic recovery based on AI input.
    """
    logging.info(f"AI Alert for {alert.container}: {alert.error_type}")
    
    # 1. Map predicted label to action
    action = map_issue_to_action(alert.error_type, alert.suggested_fix)
    
    # 2. Execute Docker fix
    success = execute_recovery_action(alert.container, action)
    
    # 3. Build DYNAMIC report (No more hardcoded OOM messages)
    report = IncidentReport(
        container=alert.container,
        error_type=alert.error_type,    # Predicted by SVM
        suggested_fix=alert.suggested_fix, 
        action_taken=action,
        resolution_status="Success" if success else "Failed",
        timestamp=datetime.now().isoformat()
    )
    
    # Log to JSON for history table
    log_incident(report)
    return report