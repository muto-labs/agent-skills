"""Build an offline-capable PBS dashboard from the current package. No external dependencies."""
from pathlib import Path
import argparse, json, re, shutil, runpy

def build(package):
    package = package.resolve()
    state = json.loads((package/"references/onboarding-state.json").read_text(encoding="utf-8-sig"))
    checker = runpy.run_path(str(package/"scripts/check_package.py"))
    summarize = checker["summarize"]
    config = json.loads((package/"references/dashboard-config.json").read_text(encoding="utf-8-sig"))
    docs = {}
    for directory in [package/"references", package/"assets/outputs", package/"assets/inputs", package/"assets/templates"]:
        for p in sorted(directory.rglob("*.md")):
            if "history" in p.relative_to(package).parts:
                continue
            text = p.read_text(encoding="utf-8-sig")
            title = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")), p.stem)
            docs[p.relative_to(package).as_posix()] = {"title":title,"text":text}
    skill = (package/"SKILL.md").read_text(encoding="utf-8-sig")
    docs["SKILL.md"] = {"title":"Personal Brand Skill","text":skill}
    for c in config["components"]:
        c["docs"] = [path for path in c["docs"] if path in docs]
        if not c["docs"]:
            raise ValueError(f"Component detail missing: {c['id']}")
    for amplifier in config.get("fuel",[]):
        if amplifier["doc"] not in docs: raise ValueError("Fuel detail missing: "+amplifier["id"])
    fuel_state=json.loads((package/"references/fuel-state.json").read_text(encoding="utf-8"))
    for amplifier in config.get("fuel",[]):
        amplifier["status"]=fuel_state["statuses"].get(amplifier["id"],"ready")
        if amplifier["status"] not in {"ready","active","usable","revisit"}: raise ValueError("Invalid Fuel status")
    index = (package/"references/asset-index.md").read_text(encoding="utf-8-sig")
    outputs = sorted((package/"assets/outputs").glob("*.md"))
    latest = {}
    for p in outputs:
        match = re.search(r"-v(\d+)\.(\d+)\.md$",p.name)
        stem = re.sub(r"-v\d+\.\d+\.md$","",p.name)
        version = tuple(map(int,match.groups())) if match else (0,0)
        if stem not in latest or version > latest[stem][0]:
            latest[stem] = (version,p.name)
    assets = []
    for p in outputs:
        path = p.relative_to(package).as_posix()
        stem = re.sub(r"-v\d+\.\d+\.md$","",p.name)
        row = next((l for l in index.splitlines() if l.startswith("|") and p.name in l),"")
        if latest[stem][1] != p.name or re.search(r"superseded|earlier|supersede synthesis",row,re.I):
            status,label = "history","Earlier version"
        elif "deferred" in row.lower():
            status,label = "deferred","Deferred"
        elif re.search(r"accepted profile|accepted for reuse",row,re.I):
            status,label = "accepted","Accepted"
        else:
            status,label = "review","Needs review"
        category = "Profile" if "profile" in p.name else "Bio & intro" if "bio" in p.name or "introduction" in p.name else "Story" if "story" in p.name or "origin" in p.name else "Plan & ideas"
        assets.append({"path":path,"name":p.name,"title":docs[path]["title"],"category":category,"status":status,"statusLabel":label})
    assets.sort(key=lambda a: ({"accepted":0,"review":1,"deferred":2,"history":3}[a["status"]],a["title"]))
    profile = next((a["path"] for a in assets if a["status"]=="accepted" and a["category"]=="Profile"), None)
    profile_lines = docs[profile]["text"].splitlines() if profile else []
    role = next((l.strip("*") for l in profile_lines[1:5] if l.startswith("**")), "Your role and direction will take shape here.")
    purpose = next((l.strip("*") for l in profile_lines if l.startswith("**Help ")), None)
    kb_purpose = re.search(r"(?m)^\*\*(Help .+)\*\*$", docs["references/personal-brand-kb.md"]["text"])
    purpose = purpose or (kb_purpose.group(1) if kb_purpose else "Your purpose will take shape as we explore what matters to you.")
    def complete(milestones):
        return all(i["state"] in {"resolved","not applicable"} for i in state["items"] if i["id"].split(".")[0] in milestones)
    for c in config["components"]:
        if c["metric"]=="reviewed":
            done = complete(c["milestones"])
            c["status"] = "accepted" if done else "review"
            c["statusLabel"] = "Reviewed" if done else "Needs review"
            if c["id"]=="kb": c["statusLabel"] = "Core established" if done else "Getting started"
            if c["id"]=="assets" and profile: c["statusLabel"] = "In use"
    initials = state.get("output_prefix") or "PB"
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", initials): raise ValueError("Unsafe output prefix")
    presentation = {"initials":initials,"profile":profile,"role":role,"purpose":purpose,"ready":bool(profile and complete(["M2","M3"]))}
    data = {"leader":state["leader"],"date":state["updated"],"version":state["standard_version"],"state":state,"summary":summarize(state),"components":config["components"],"fuel":config.get("fuel",[]),"assets":assets,"docs":docs,"presentation":presentation}
    destination = package/"assets/dashboard/dist"
    destination.mkdir(parents=True,exist_ok=True)
    for name in ["index.html","styles.css","app.js"]:
        shutil.copyfile(package/"assets/dashboard/src"/name,destination/name)
    (destination/"data.js").write_text("window.PBS_DATA = "+json.dumps(data,ensure_ascii=False).replace("<","\\u003c")+";\n",encoding="utf-8")
    standalone_data = dict(data, sourcePrefix="../../")
    html = (package/"assets/dashboard/src/index.html").read_text(encoding="utf-8")
    css = (package/"assets/dashboard/src/styles.css").read_text(encoding="utf-8")
    js = (package/"assets/dashboard/src/app.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+css+'</style>')
    html = html.replace('<script src="data.js" defer></script><script src="app.js" defer></script>', '')
    payload = json.dumps(standalone_data,ensure_ascii=False).replace("<","\\u003c")
    html = html.replace('</body>', '<script>window.PBS_DATA = '+payload+';</script><script>'+js+'</script></body>')
    standalone = package/"assets/dashboard"/(initials+"-personal-brand-dashboard.html")
    standalone.write_text(html,encoding="utf-8")
    (package/"references/dashboard-manifest.json").write_text(json.dumps({"standard_version":state["standard_version"],"snapshot_date":state["updated"],"standalone":standalone.relative_to(package).as_posix(),"profile":profile,"summary":data["summary"],"source_digest":checker["source_fingerprint"](package)},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"dashboard":str(destination/"index.html"),"components":len(config["components"]),"assets":len(assets),"documents":len(docs),"summary":data["summary"]},indent=2))

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("package",nargs="?",type=Path,default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().package)
