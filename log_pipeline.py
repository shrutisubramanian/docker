# log_pipeline.py

import docker
from datetime import datetime
import time
import json
import threading

class LogPipeline:
    """
    Multi-Container Log Collection Pipeline
    Member 2 (Shubhashri) - Log Streaming & Data Pipeline Engineer
    
    Features:
    - Real-time log streaming from multiple Docker containers
    - Structured JSON format storage
    - Container name tagging
    - Timestamp formatting
    - API for teammates to query logs
    """
    
    def __init__(self, container_names=None):
        """
        Initialize the pipeline
        
        Args:
            container_names: List of container names to monitor, or None to auto-discover all
        """
        self.client = docker.from_env()
        self.container_names = container_names or []
        self.log_storage = []  # Stores JSON strings
        self.running = False
    
    def discover_containers(self):
        """Auto-discover all running containers"""
        containers = self.client.containers.list()
        discovered = [c.name for c in containers]
        print(f"🔍 Discovered {len(discovered)} running containers")
        return discovered
    
    def _stream_from_container(self, container_name):
        """
        Stream logs from a single container (runs in separate thread)
        
        Args:
            container_name: Name of container to monitor
        """
        try:
            container = self.client.containers.get(container_name)
            
            for log_line in container.logs(stream=True, follow=True):
                if not self.running:
                    break
                
                text = log_line.decode('utf-8').strip()
                
                # Detect severity
                if 'critical' in text.lower():
                    severity = 'CRITICAL'
                    emoji = '🔴'
                elif 'error' in text.lower():
                    severity = 'ERROR'
                    emoji = '❌'
                elif 'warning' in text.lower():
                    severity = 'WARNING'
                    emoji = '⚠️'
                elif 'notice' in text.lower() or 'info' in text.lower():
                    severity = 'INFO'
                    emoji = '💙'
                else:
                    severity = 'LOG'
                    emoji = '📝'
                
                # Create structured log (JSON-compatible dictionary)
                organized_log = {
                    'timestamp': datetime.now().isoformat(),
                    'container_name': container_name,
                    'severity': severity,
                    'message': text
                }
                
                # Convert to JSON string and store
                json_log = json.dumps(organized_log)
                self.log_storage.append(json_log)
                
                # Print with emoji and container name
                print(f"{emoji} [{container_name}] {severity}: {text[:50]}...")
        
        except docker.errors.NotFound:
            print(f"❌ Container '{container_name}' not found!")
        except Exception as e:
            print(f"❌ Error with {container_name}: {e}")
    
    def start_collecting(self, duration=60):
        """
        Start collecting logs from all specified containers
        
        Args:
            duration: How long to collect logs in seconds (default: 60)
        """
        # Auto-discover containers if none specified
        if not self.container_names:
            self.container_names = self.discover_containers()
        
        if not self.container_names:
            print("❌ No containers found to monitor!")
            return
        
        print(f"\n📡 Starting Multi-Container Log Collection")
        print(f"Monitoring {len(self.container_names)} containers:")
        for name in self.container_names:
            print(f"  ✓ {name}")
        print(f"Duration: {duration} seconds")
        print("-" * 60)
        
        self.running = True
        threads = []
        
        # Start a separate thread for each container
        for container_name in self.container_names:
            thread = threading.Thread(
                target=self._stream_from_container,
                args=(container_name,),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Collect for specified duration
        try:
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n👋 Stopped by user!")
        
        # Stop collecting
        self.running = False
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join(timeout=2)
        
        print(f"\n✅ Collection complete! Collected {len(self.log_storage)} logs from {len(self.container_names)} containers\n")
    
    def stop_collecting(self):
        """Stop collecting logs"""
        self.running = False
    
    # === API FOR MEMBER 3 (SHRUTI - AI ANALYZER) ===
    
    def get_recent_logs(self, count=10):
        """
        Get the most recent N logs as JSON strings
        
        Args:
            count: Number of recent logs to return
            
        Returns:
            List of JSON strings
        """
        return self.log_storage[-count:] if self.log_storage else []
    
    def get_logs_by_container(self, container_name):
        """
        Get all logs from a specific container
        
        Args:
            container_name: Name of container
            
        Returns:
            List of JSON strings from that container
        """
        filtered = []
        for json_log in self.log_storage:
            log = json.loads(json_log)
            if log['container_name'] == container_name:
                filtered.append(json_log)
        return filtered
    
    def get_all_errors(self):
        """
        Get all ERROR and CRITICAL logs as JSON strings
        
        Returns:
            List of JSON strings containing errors
        """
        errors = []
        for json_log in self.log_storage:
            log = json.loads(json_log)
            if log['severity'] in ['ERROR', 'CRITICAL']:
                errors.append(json_log)
        return errors
    
    def get_error_count(self):
        """
        Count total errors and critical logs
        
        Returns:
            Integer count of errors
        """
        return len(self.get_all_errors())
    
    def get_logs_by_severity(self, severity):
        """
        Get all logs of a specific severity level
        
        Args:
            severity: 'CRITICAL', 'ERROR', 'WARNING', 'INFO', or 'LOG'
            
        Returns:
            List of JSON strings matching severity
        """
        filtered = []
        for json_log in self.log_storage:
            log = json.loads(json_log)
            if log['severity'] == severity:
                filtered.append(json_log)
        return filtered
    
    # === API FOR MEMBER 4 (SUBHASHINI - ACTION EXECUTOR) ===
    
    def get_stats(self):
        """
        Get summary statistics of collected logs
        
        Returns:
            Dictionary with counts by severity and container
        """
        stats = {
            'total_logs': len(self.log_storage),
            'containers_monitored': len(self.container_names),
            'critical_count': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'by_container': {}
        }
        
        # Count by severity and by container
        for json_log in self.log_storage:
            log = json.loads(json_log)
            severity = log['severity']
            container = log['container_name']
            
            # Count by severity
            if severity == 'CRITICAL':
                stats['critical_count'] += 1
            elif severity == 'ERROR':
                stats['error_count'] += 1
            elif severity == 'WARNING':
                stats['warning_count'] += 1
            elif severity == 'INFO':
                stats['info_count'] += 1
            
            # Count by container
            if container not in stats['by_container']:
                stats['by_container'][container] = 0
            stats['by_container'][container] += 1
        
        return stats
    
    def get_all_logs(self):
        """
        Get all collected logs as JSON strings
        
        Returns:
            List of all JSON strings
        """
        return self.log_storage
    
    # === DISPLAY FUNCTIONS ===
    
    def print_summary(self):
        """Print a formatted summary of collected logs"""
        stats = self.get_stats()
        
        print("="*60)
        print("📊 MULTI-CONTAINER LOG COLLECTION SUMMARY")
        print("="*60)
        print(f"Containers Monitored: {stats['containers_monitored']}")
        print(f"Total Logs Collected: {stats['total_logs']}")
        print(f"\nSeverity Breakdown:")
        print(f"  🔴 Critical: {stats['critical_count']}")
        print(f"  ❌ Errors:   {stats['error_count']}")
        print(f"  ⚠️  Warnings: {stats['warning_count']}")
        print(f"  💙 Info:     {stats['info_count']}")
        
        print(f"\n📦 Logs by Container:")
        for container, count in stats['by_container'].items():
            print(f"  - {container}: {count} logs")
        
        # Show errors if any
        errors = self.get_all_errors()
        if errors:
            print(f"\n🚨 All Critical/Error Logs ({len(errors)}):")
            for json_log in errors[:10]:  # Show max 10
                log = json.loads(json_log)
                time_str = log['timestamp'].split('T')[1][:8]
                print(f"  [{log['container_name']}] [{time_str}] {log['severity']}: {log['message'][:50]}")
        
        # Show last 5 logs from all containers
        print(f"\n📋 Last 5 Logs (across all containers):")
        for json_log in self.get_recent_logs(5):
            log = json.loads(json_log)
            time_str = log['timestamp'].split('T')[1][:8]
            print(f"  [{log['container_name']}] [{time_str}] {log['severity']}: {log['message'][:50]}")
        
        print("="*60)
        
        # Show storage format details
        print(f"\n💾 Storage Format:")
        print(f"  Format: JSON strings in memory")
        print(f"  Type: {type(self.log_storage)}")  # list
        if self.log_storage:
            print(f"  First item type: {type(self.log_storage[0])}")  # str
            print(f"\n  Example JSON log:")
            example = json.loads(self.log_storage[0])
            print(f"  {json.dumps(example, indent=4)}")
        
        print("="*60)