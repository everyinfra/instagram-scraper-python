"""Minimal EveryInfra client: one POST per call, polls async jobs, exits on errors.

Docs: https://everyinfra.com/en/docs
"""
import csv
import json
import os
import sys
import time

import requests

API = "https://api.everyinfra.com"
DONE = {"succeeded", "failed"}


def _key():
    key = os.environ.get("EVERYINFRA_API_KEY")
    if not key:
        sys.exit("Set EVERYINFRA_API_KEY first. Get a key at https://everyinfra.com/en/docs#quickstart")
    return key


def call(platform, action, params, timeout=180):
    """POST /api/v1/social. Returns the response body; waits for async jobs."""
    headers = {"Authorization": f"Bearer {_key()}"}
    body = {"platform": platform, "action": action, "params": params}
    r = requests.post(f"{API}/api/v1/social", json=body, headers=headers, timeout=timeout)
    data = r.json()
    if r.status_code >= 400:
        err = data.get("error", {})
        charged = data.get("billing", {}).get("charged", False)
        sys.exit(f"HTTP {r.status_code} {err.get('code')}: {err.get('message')} (charged: {charged})")
    if data.get("job_id") and data.get("status") not in DONE:
        data = wait(data["job_id"], headers)
    return data


def wait(job_id, headers, every=5, limit=600):
    """Poll GET /api/v1/jobs/{job_id} (free) until the job succeeds or fails."""
    start = time.time()
    while True:
        data = requests.get(f"{API}/api/v1/jobs/{job_id}", headers=headers, timeout=60).json()
        if data.get("status") in DONE:
            break
        if time.time() - start > limit:
            sys.exit(f"Job {job_id} still {data.get('status')} after {limit}s; poll it again later.")
        time.sleep(every)
    if data["status"] == "failed":
        sys.exit(f"Job {job_id} failed: {json.dumps(data.get('error', data))}")
    return data


def save(rows, path):
    """Write rows to .json or .csv (lists are joined with ';')."""
    if path.endswith(".json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        return
    keys = []
    for row in rows:
        keys += [k for k in row if k not in keys and not isinstance(row[k], dict)]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: ";".join(map(str, v)) if isinstance(v, list) else v for k, v in row.items()})


def report(data, out):
    rows = data.get("results") or []
    charged = data.get("billing", {}).get("charged_usd")
    cost = f", charged ${charged}" if charged is not None else f", billing {data.get('billing_state')}"
    print(f"{len(rows)} rows{cost}", file=sys.stderr)
    if out:
        save(rows, out)
        print(f"saved to {out}", file=sys.stderr)
    else:
        print(json.dumps(rows[:3], ensure_ascii=False, indent=2))
    return rows
