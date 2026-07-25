#!/usr/bin/env python3
"""
HumanitAI Pulse — Prevention Radar (Understand stage).

Detects crisis pathways from the composite risk series. Pure deterministic logic
(no model needed). Flags towns where risk is rising across two+ pressures, which is
the signal the 5th Space barge should prioritise for its next mooring.

Pathways modelled (illustrative, population-level only):
  rent_arrears -> eviction -> homelessness
  isolation -> mental_health_crisis
  missed_appointments -> worsening_illness
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "prediction" / "prevention_out_v3.json"


def detect(d):
    comp = d.get("composite", [])
    alerts = []
    for r in comp:
        # If a town is Critical AND its dominant pressure is isolation/mental, flag pre-crisis
        if r.get("tier") == "Critical" and r.get("pressure_dominant") in ("isolation", "mental"):
            alerts.append({
                "place": r["place"],
                "pathway": "isolation -> crisis care",
                "risk": r["risk"],
                "priority": "high",
            })
    return alerts


def main():
    if not OUT.exists():
        print("[radar] no prediction output")
        return
    d = json.loads(OUT.read_text())
    alerts = detect(d)
    (ROOT / "prediction" / "radar_alerts.json").write_text(json.dumps(alerts, indent=2))
    for a in alerts:
        print(f"[radar] {a['place']}: {a['pathway']} (risk {a['risk']})")


if __name__ == "__main__":
    main()
