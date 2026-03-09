import subprocess

print("\n==============================")
print(" Autonomous Log Monitoring System ")
print("==============================\n")

print("Step 1: Detecting anomalies...\n")
subprocess.run(["python", "ai_engine/anomaly_detector.py"])

print("\nStep 2: Running AI log analyzer...\n")
subprocess.run(["python", "ai_engine/analyzer.py"])

print("\nSystem analysis complete.")