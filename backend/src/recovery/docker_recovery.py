# backend/src/recovery/docker_recovery.py
import docker
import logging

def execute_recovery_action(container_name: str, action: str) -> bool:
    """
    Executes specialized remediation steps predicted directly by the AI model.
    Preserves original resource-limiting logic while adding new autonomous fixes.
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        logging.info(f"AI Model requested action: {action} for {container_name}")

        # --- AI-Driven Specialized Actions ---
        
        if action == "RESTART_WITH_LIMITS":
            # AI identified memory pressure: applying 512MB limit and restarting
            container.update(mem_limit="512m")
            container.restart()
            
        elif action == "RESET_NETWORK":
            # AI identified network latency: clearing tc qdisc rules
            # Requires iproute2/tc to be installed in the container
            container.exec_run("tc qdisc del dev eth0 root", detach=True)
            
        elif action == "PURGE_LOGS":
            # AI identified disk exhaustion: purging temporary data and logs
            container.exec_run("sh -c 'rm -rf /tmp/* /var/log/*.log'", detach=True)
            
        elif action == "FIX_PERMISSIONS":
            # AI identified permission errors: resetting standard access
            container.exec_run("chmod -R 755 /var/lib/app", detach=True)

        # --- Preserved Original Logic ---

        elif action == "LIMIT_RESOURCES":
            # Dynamically throttle a runaway CPU container
            container.update(cpu_period=100000, cpu_quota=50000) 
            container.restart()

        elif action == "CLEAR_CACHE_AND_RESTART":
            # Signal the app to clear internal cache via reboot
            container.restart()

        elif action == "REBUILD_AND_START":
            # For containers that are stopped or need a clean start
            container.start()

        elif action in ["REBUILD_IMAGE", "INCREASE_TIMEOUT"]:
            # Standard recovery for build or timeout issues
            container.restart()

        else:
            # Default fallback for RESTART_CONTAINER or unrecognized AI labels
            container.restart()
            
        return True
    except Exception as e:
        logging.error(f"AI-Driven Recovery Failed for {container_name}: {e}")
        return False