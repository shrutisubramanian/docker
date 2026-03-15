"""
generate_report.py — saves anomaly detection results to a report file
Run after anomaly_detector.py or call generate_report(results) directly
"""

import os
import json
from datetime import datetime
from collections import Counter

REPORTS_DIR = "reports"


def generate_report(results: list, container_stats: dict = None):
    """
    Generate and save a report from anomaly detection results.

    Args:
        results: list of anomaly dicts from anomaly_detector
        container_stats: optional dict with total/normal log counts
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_txt  = os.path.join(REPORTS_DIR, f"report_{timestamp}.txt")
    report_json = os.path.join(REPORTS_DIR, f"report_{timestamp}.json")

    if not results:
        print("[WARN] No anomalies to report.")
        return

    type_counts = Counter(r["error_type"] for r in results)
    avg_conf = sum(r["confidence"] for r in results) / len(results)

    # ── Plain text report ─────────────────────────────────────────────────────
    with open(report_txt, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  AI CONTAINER MONITORING REPORT\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        if container_stats:
            f.write(f"Total logs scanned : {container_stats.get('total', 'N/A')}\n")
            f.write(f"Normal logs        : {container_stats.get('normal', 'N/A')}\n")

        f.write(f"Anomalies detected : {len(results)}\n")
        f.write(f"Avg SVM confidence : {avg_conf:.1f}%\n\n")

        f.write("Error breakdown:\n")
        for etype, count in type_counts.most_common():
            f.write(f"  {etype}: {count}\n")

        f.write("\n" + "-" * 60 + "\n")
        f.write("DETAILED FINDINGS\n")
        f.write("-" * 60 + "\n\n")

        for i, r in enumerate(results, 1):
            f.write(f"[{i}] Container : {r['container']}\n")
            f.write(f"    Log       : {r['original_log']}\n")
            f.write(f"    Error     : {r['error_type']} (confidence: {r['confidence']}%)\n")
            f.write(f"    Cause     : {r['root_cause']}\n")
            f.write(f"    Fix       : {r['fix']}\n\n")

        f.write("=" * 60 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 60 + "\n")

    # ── JSON report ───────────────────────────────────────────────────────────
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_anomalies": len(results),
            "avg_confidence": round(avg_conf, 1),
            "error_breakdown": dict(type_counts),
        },
        "anomalies": results,
    }
    if container_stats:
        json_data["summary"].update(container_stats)

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

    print(f"\nReport saved:")
    print(f"  Text : {report_txt}")
    print(f"  JSON : {report_json}")

    return report_txt, report_json