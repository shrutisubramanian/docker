# backend/src/recovery/docker_recovery.py
from typing import Tuple
import docker
import logging

def execute_recovery_action(container_name: str, action: str) -> Tuple[bool, str]:
    """
    Executes specialized remediation steps predicted directly by the AI model.
    Differentiates between Hot Fixes (no restart) and Cold Fixes (restart).
    Returns (success, detailed_fix_command).
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        logging.info(f"AI Model requested action: {action} for {container_name}")
        detailed_fix = "No specific command executed"

        # --- "HOT FIXES" (NO RESTART) ---
        
        if action == "RESET_NETWORK":
            # AI identified network latency: clearing tc qdisc rules
            cmd = "tc qdisc del dev eth0 root"
            container.exec_run(cmd, detach=True)
            detailed_fix = f"Hot Fix: Executed '{cmd}' to clear network latency rules."

        elif action == "PURGE_LOGS":
            # AI identified disk exhaustion: purging temporary data and logs
            cmd = "sh -c 'rm -rf /tmp/* /var/log/*.log'"
            container.exec_run(cmd, detach=True)
            detailed_fix = f"Hot Fix: Executed '{cmd}' to free disk space."

        elif action == "FIX_PERMISSIONS":
            # AI identified permission errors: resetting standard access
            cmd = "chmod -R 755 /var/lib/app"
            container.exec_run(cmd, detach=True)
            detailed_fix = f"Hot Fix: Executed '{cmd}' to restore application directory permissions."

        elif action == "APPLY_CPU_QUOTA":
            # AI identified CPU spike: applying resource quota without restart
            container.update(cpu_period=100000, cpu_quota=50000)
            detailed_fix = "Hot Fix: Dynamically applied CPU Quota (50%) to throttle runaway process."

        # --- "COLD FIXES" (RESTART REQUIRED) ---
        
        elif action == "RESTART_WITH_LIMITS":
            # AI identified memory pressure: applying 512MB limit and restarting
            container.update(mem_limit="512m")
            container.restart()
            detailed_fix = "Cold Fix: Updated Memory Limit to 512MB and performed a Hard Restart."
            
        elif action == "REBUILD_IMAGE":
            # AI identified build issues: attempting a restart/rebuild signal
            container.restart()
            detailed_fix = "Cold Fix: Triggered Container Restart to pick up new image/build state."

        elif action == "RESTART_CONTAINER":
            # Generic crash recovery
            container.restart()
            detailed_fix = "Cold Fix: Performed a Standard Container Restart to recover from crash."

        else:
            # Fallback
            container.restart()
            detailed_fix = f"Default: Restarted container as fallback for action '{action}'."
            
        return True, detailed_fix

    except Exception as e:
        err_msg = f"AI-Driven Recovery Failed for {container_name}: {e}"
        logging.error(err_msg)
        return False, err_msg