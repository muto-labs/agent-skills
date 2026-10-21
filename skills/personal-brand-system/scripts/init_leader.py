"""Initialize a personalized PBS package and its day-one dashboard."""
import argparse, json, re, shutil, runpy
from pathlib import Path

def initialize(source, destination, name, initials, skill_name, date):
    if destination.exists():
        raise ValueError("Destination exists; use maintenance/refresh rather than overwrite")
    if not re.fullmatch(r"[a-z0-9-]{1,63}", skill_name):
        raise ValueError("Use a lowercase hyphenated skill name under 64 characters")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", initials):
        raise ValueError("Unsafe initials/prefix")
    if destination.name != skill_name:
        raise ValueError("Destination folder must match skill name")
    if source == destination or source in destination.parents:
        raise ValueError("Destination must be separate from standard package")
    state=json.loads((source/"references/onboarding-state.json").read_text(encoding="utf-8-sig"))
    if any(i["state"] != "not started" for i in state["items"]) or state["time_events"]:
        raise ValueError("Initialize from a clean standard, not a leader package")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("dist","*-personal-brand-dashboard.html","dashboard-manifest.json","__pycache__"))
    state_path=destination/"references/onboarding-state.json"
    state.update(leader=name,output_prefix=initials,updated=date,quality="Unassessed. Evaluate selected answers with evidence and scope.",next="Explore personal success and contribution; first dashboard exists.")
    state_path.write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    kb=destination/"references/personal-brand-kb.md"
    kb.write_text(kb.read_text(encoding="utf-8-sig").replace("Leader: not initialized","Leader: "+name),encoding="utf-8")
    skill=destination/"SKILL.md"
    text=skill.read_text(encoding="utf-8-sig").replace("name: personal-brand-system","name: "+skill_name)
    text=text.replace("# Personal Brand System","# "+name+" — Personal Brand")
    text=text.replace("Identify the leader and requested mode.","Leader: "+name+". Output prefix: "+initials+". This package is initialized; resume existing progress.")
    skill.write_text(text,encoding="utf-8")
    (destination/"references/asset-index.md").write_text("# "+initials+" asset index\nNo leader assets yet. Dashboard created; index each output with ID, version, source and review status.\n",encoding="utf-8")
    (destination/"references/progress.md").write_text("# "+initials+" onboarding dashboard\nCompletion 0%: 0 resolved, 0 deferred, 30 remaining. Active time unknown.\nCurrent source: [state](onboarding-state.json).\nNext: explore objectives; day-one dashboard is available.\n",encoding="utf-8")
    runpy.run_path(str(destination/"scripts/build_dashboard.py"))["build"](destination)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--name",required=True)
    p.add_argument("--initials",required=True)
    p.add_argument("--skill-name",required=True)
    p.add_argument("--destination",type=Path,required=True)
    p.add_argument("--date",required=True,help="Leader-local date YYYY-MM-DD")
    args=p.parse_args()
    initialize(Path(__file__).resolve().parents[1],args.destination.resolve(),args.name,args.initials,args.skill_name,args.date)

