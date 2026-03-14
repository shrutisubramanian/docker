def find_root_cause(log):
    log = log.lower()

    if "memory" in log or "137" in log:
        return "Memory exhaustion in container", "Increase container memory limit (e.g. --memory=512m)"

    if "connection refused" in log:
        return "Downstream service unreachable", "Check that the target service is running and reachable"

    if "dependency" in log:
        return "Missing dependency during build", "Rebuild image and verify all dependencies in requirements.txt"

    if "permission" in log:
        return "Insufficient permissions", "Review file permissions and the user the container runs as"

    if "timeout" in log:
        return "Service response timeout", "Increase timeout threshold or investigate slow dependencies"

    return "Unknown anomaly", "Review full log output and escalate if issue persists"