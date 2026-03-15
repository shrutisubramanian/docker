from typing import Dict

def map_issue_to_action(error_type: str, suggested_fix: str) -> str:
    """
    Maps the predicted AI error type to a concrete backend recovery action.
    Corresponds to Member 4's Execution Layer.
    """
    label = error_type.lower()
    
    # 1. Process/Logic Attacks
    if "fork" in label:
        return "RESTART_CONTAINER" # Cleanest way to kill a fork bomb
        
    # 2. Network Attacks
    if "network" in label or "latency" in label or "delay" in label:
        return "RESET_NETWORK"
        
    # 3. Disk/Storage Attacks
    if "disk" in label or "space" in label:
        return "PURGE_LOGS"
        
    # 4. Standard Resource Spikes
    if "cpu" in label:
        return "APPLY_CPU_QUOTA"
        
    if "memory" in label:
        return "RESTART_WITH_LIMITS"
        
    # 5. Generic Crash
    if "crash" in label or "stopped" in label:
        return "RESTART_CONTAINER"
        
    # Default fallback
    return "RESTART_CONTAINER"