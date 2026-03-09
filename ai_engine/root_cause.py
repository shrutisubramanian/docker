def find_root_cause(log):

    if "memory" in log.lower() or "137" in log:
        return "Memory exhaustion in container"

    if "connection refused" in log.lower():
        return "Database service unavailable"

    if "dependency" in log.lower():
        return "Missing dependency during build"

    if "permission" in log.lower():
        return "Permission configuration issue"

    if "timeout" in log.lower():
        return "Service response timeout"

    return "Unknown anomaly"