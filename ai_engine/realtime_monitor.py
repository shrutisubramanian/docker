import time
import os
import sys
from datetime import datetime
from anomaly_detector import load_logs, train_model, predict_anomalies, files
from root_cause import find_root_cause

# Ensure stdout uses UTF-8 to prevent UnicodeEncodeError with emojis
if sys.stdout.encoding.lower() != 'utf-8':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("Initializing Real-Time AI Log Monitor...")
    
    all_logs, sources = load_logs()
    
    if not all_logs:
        print("No existing logs found. The model requires initial data to train.")
        return
        
    print(f"Training anomaly detection model on {len(all_logs)} existing log entries...")
    model, vectorizer = train_model(all_logs)
    print("Model training complete. Beginning real-time monitoring.\n")
    
    # Initialize file positions to the end of the file
    file_positions = {}
    for service, path in files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, 2)
                file_positions[service] = f.tell()
        else:
            file_positions[service] = 0

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("=====================================")
            print("AI Container Monitoring Cycle")
            print(f"Timestamp: {current_time}")
            print("=====================================\n")
            print("Checking logs...\n")
            
            new_logs_found = False
            
            for service, path in files.items():
                if not os.path.exists(path):
                    continue
                    
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(0, 2)
                    current_eof = f.tell()
                    
                    last_pos = file_positions.get(service, 0)
                    
                    if current_eof < last_pos:
                        # File was truncated/rotated
                        last_pos = 0
                        
                    if current_eof > last_pos:
                        f.seek(last_pos)
                        lines = f.readlines()
                        file_positions[service] = f.tell()
                        
                        new_lines = [line.strip() for line in lines if line.strip()]
                        
                        if new_lines:
                            new_logs_found = True
                            predictions = predict_anomalies(model, vectorizer, new_lines)
                            
                            for log_msg, pred in zip(new_lines, predictions):
                                if pred == -1:
                                    cause = find_root_cause(log_msg)
                                    print(f"⚠️ Anomaly detected in {service.upper()} container")
                                    print(f"Log: {log_msg}")
                                    print(f"Root Cause: {cause}\n")
                                else:
                                    print(f"Normal log ({service}): {log_msg}")
            
            print("Next scan in 30 seconds...\n")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()
