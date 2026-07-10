from typing import Dict

def map_issue_to_action(error_type: str, suggested_fix: str) -> str:
    """
    Maps the predicted AI error type to a concrete backend recovery action.
    Upgraded to support new SVM labels: build, dependency, permission, timeout.
    """
    label = error_type.lower()
    
    # 1. Resource & Logic Attacks
    if "fork" in label:
        return "RESTART_CONTAINER"
        
    if "memory" in label:
        return "RESTART_WITH_LIMITS"
        
    if "cpu" in label:
        return "APPLY_CPU_QUOTA"

    # 2. Network & Connectivity
    if "dependency" in label or "refused" in label:
        return "RESTART_CONTAINER"
        
    if "timeout" in label or "latency" in label or "delay" in label:
        return "RESET_NETWORK"

    # 3. Security & Access
    if "permission" in label or "access" in label:
        return "FIX_PERMISSIONS"

    # 4. Lifecycle & Build
    if "build" in label or "compile" in label:
        return "REBUILD_IMAGE"

    # 5. Generic Crash
    if "crash" in label or "stopped" in label or "segfault" in label:
        return "RESTART_CONTAINER"
        
    # Default fallback
    return "RESTART_CONTAINER"