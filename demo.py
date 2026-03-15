# demo.py

from log_pipeline import LogPipeline

print("="*60)
print("🚀 MULTI-CONTAINER LOG PIPELINE DEMO")
print("="*60)

# Auto-discover all containers
print("\n📍 Mode: Auto-discover all containers")
pipeline = LogPipeline()

# Collect for just 10 seconds (changed from 60!)
pipeline.start_collecting(duration=10)

# Show summary
pipeline.print_summary()

# === DEMO: API usage ===

print("\n" + "="*60)
print("🧪 API USAGE DEMO FOR TEAMMATES")
print("="*60)

print("\n--- Member 3 (Shruti - AI Analyzer) Usage: ---")
print("\n1. Get recent logs for AI analysis:")
print("   recent_logs = pipeline.get_recent_logs(10)")
recent = pipeline.get_recent_logs(10)
print(f"   → Returns {len(recent)} JSON strings")
if recent:
    print(f"   → Example: {recent[0][:100]}...")

print("\n2. Get all errors across all containers:")
print("   errors = pipeline.get_all_errors()")
errors = pipeline.get_all_errors()
print(f"   → Returns {len(errors)} error/critical logs")

print("\n3. Get logs from specific container:")
if pipeline.container_names:
    print(f"   container_logs = pipeline.get_logs_by_container('{pipeline.container_names[0]}')")
    container_logs = pipeline.get_logs_by_container(pipeline.container_names[0])
    print(f"   → Returns {len(container_logs)} logs from that container")

print("\n--- Member 4 (Subhashini - Action Executor) Usage: ---")
print("\n1. Get statistics:")
print("   stats = pipeline.get_stats()")
stats = pipeline.get_stats()
print(f"   → Returns: {stats}")

print("\n2. Get error count:")
print("   error_count = pipeline.get_error_count()")
error_count = pipeline.get_error_count()
print(f"   → Returns: {error_count} errors")

print("\n" + "="*60)
print("✅ DEMO COMPLETE")
print("="*60)