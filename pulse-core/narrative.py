#!/usr/bin/env python3
"""
HumanitAI Pulse — free-model narrative layer.

Reads prediction/out.json (deterministic scores) and produces the *language* layer:
- "what changed this week"
- per-town risk narrative
- intervention recommendation note

Uses the FREE model tencent/hy3:free via the Nous Portal OpenAI-compatible endpoint.
No paid API. If the model is unreachable, the system degrades gracefully to a
"synthesis pending" placeholder — the numbers still stand on their own.

Env: NOUS_API_KEY (free key from portal.nousresearch.com). Optional.
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "prediction" / "prevention_out_v3.json"

MODEL = "tencent/hy3:free"
BASE = os.environ.get("NOUS_BASE_URL", "https://api.nousresearch.com/v1")


def load():
    if not OUT.exists():
        return None
    return json.loads(OUT.read_text())


def build_prompt(d):
    comp = d.get("composite", [])[:8]
    lines = "\n".join(f"- {r['place']} (risk {r['risk']}, {r['tier']})" for r in comp)
    return (
        "You are the narrative layer for HumanitAI Pulse, a UK community-forecast system. "
        "Write a 3-sentence plain-language briefing on where social pressure is building. "
        "No statistics you cannot source. Calm, no charity voice, no blame. Internal enemy only.\n\n"
        f"Top towns by composite risk:\n{lines}\n\nBriefing:"
    )


def run_free(prompt):
    key = os.environ.get("NOUS_API_KEY")
    if not key:
        return "[synthesis pending — set NOUS_API_KEY to enable free-model narrative]"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, base_url=BASE)
        r = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=220,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"[synthesis pending — model unreachable: {e}]"


def main():
    d = load()
    if not d:
        print("[narrative] no prediction output found")
        return
    prompt = build_prompt(d)
    out = run_free(prompt)
    (ROOT / "prediction" / "narrative.md").write_text(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
