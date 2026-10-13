"""Validate PBS state/package and report progress. Python 3 standard library only."""
import argparse, hashlib, json, re
from pathlib import Path

STATES = {"not started", "in progress", "resolved", "deferred", "not applicable"}

def source_fingerprint(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or path.suffix not in {".md",".json",".py",".html",".css",".js"}:
            continue
        if "history" in relative.parts or "dist" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.name == "dashboard-manifest.json" or path.name.endswith("-personal-brand-dashboard.html"):
            continue
        digest.update(relative.as_posix().encode()+b"\0"+path.read_bytes())
    return digest.hexdigest()

def summarize(state):
    items = state["items"]
    expected = {f"M{m}.{i}" for m in range(1, 11) for i in range(1, 4)}
    ids = [i["id"] for i in items]
    if set(ids) != expected or len(ids) != 30:
        raise ValueError("Checklist must contain each of 30 IDs once")
    for item in items:
        if item["state"] not in STATES:
            raise ValueError("Unknown item state")
        if item["state"] == "resolved" and not item["evidence"]:
            raise ValueError("Resolved item needs review/source evidence")
        if item["state"] == "not applicable" and not item.get("reason"):
            raise ValueError("N/A needs reason")
    fractions = []
    for m in range(1, 11):
        group = [i for i in items if i["id"].startswith(f"M{m}.")]
        applicable = [i for i in group if i["state"] != "not applicable"]
        if applicable:
            fractions.append(sum(i["state"] == "resolved" for i in applicable) / len(applicable))
    total = None
    seen = set()
    for event in state["time_events"]:
        if event["source"] in seen:
            raise ValueError("Duplicate time source")
        seen.add(event["source"])
        minutes = event["minutes"]
        if not isinstance(minutes, (int, float)) or isinstance(minutes, bool) or minutes < 0:
            raise ValueError("Invalid minutes")
        if event["mode"] == "cumulative":
            if total is not None and minutes < total:
                raise ValueError("Cumulative report reduces time; explicit correction required")
            total = minutes
        elif event["mode"] == "incremental":
            total = (total or 0) + minutes
        else:
            raise ValueError("Unknown time report mode")
    return {
        "completion_percent": round(100 * sum(fractions) / len(fractions), 1) if fractions else None,
        "resolved": sum(i["state"] == "resolved" for i in items),
        "deferred": sum(i["state"] == "deferred" for i in items),
        "remaining": sum(i["state"] not in {"resolved", "deferred", "not applicable"} for i in items),
        "active_minutes": total
    }

def check_links(root):
    broken = []
    for path in root.rglob("*.md"):
        # History snapshots are immutable and may contain paths relative to their original location.
        if "history" in path.relative_to(root).parts:
            continue
        content = path.read_text(encoding="utf-8-sig")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            dest = path.parent / target.split("#", 1)[0]
            if not dest.exists():
                broken.append(f"{path.relative_to(root)}: {target}")
    return broken

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    root = args.package.resolve()
    state = json.loads((root / "references/onboarding-state.json").read_text(encoding="utf-8-sig"))
    result = summarize(state)
    links = check_links(root)
    result["broken_links"] = links
    dashboard = (root / "references/progress.md").read_text(encoding="utf-8-sig")
    match = re.search(r"(?m)(?:^Completion\s+|^\*\*)(\d+(?:\.\d+)?)%", dashboard)
    result["dashboard_mismatch"] = not match or float(match.group(1)) != result["completion_percent"]
    result["unnamed_output_files"] = []
    manifest_path = root/"references/dashboard-manifest.json"
    result["dashboard_snapshot_stale"] = manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8-sig")).get("source_digest") != source_fingerprint(root)
    prefix = state.get("output_prefix", "")
    if prefix:
        result["unnamed_output_files"] = [p.name for p in (root / "assets/outputs").glob("*.md") if not p.name.startswith(prefix + "-")]
    print(json.dumps(result, indent=2))
    if links or result["unnamed_output_files"] or result["dashboard_mismatch"] or result["dashboard_snapshot_stale"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
