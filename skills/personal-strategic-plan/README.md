# Personal Strategic Plan — start here
Version 0.3.0 | Initial public release

Turn reflection into a clear personal direction, six annual Target Objectives, and a focused quarter. Work through one life pillar at a time: God (spiritual relationship), Fit (fitness), Fam (family and friends), Biz (work/business), $ (personal finances), and Up (personal development).

## Start with your AI
Keep this standard as a clean master. Use a separate private personal copy outside the public repository.

Load the skill folder using your AI tool's supported method, or share [SKILL.md](SKILL.md) and the [guided process](references/process.md), supplying additional referenced files as needed. Start with:

> Help me create my personal strategic plan for the year I choose. Use this skill and work in a separate private personal copy. Begin with the Current Year Wrap & Recap, one pillar at a time. Draft from my answers, ask one focused question at a time, and let me move on or go deeper. Reuse my accepted Personal Brand System Purpose, Tenets, and personal style if I provide them. Offer the HTML workspace and explain how to open it. Save and rebuild only when you have the necessary file access; otherwise give me clearly labeled updates I can save.

Confirm the planning year before drafting objectives. No Personal Brand System, account connection, polished answers, or branding exercise is required.

## Explore the interface
Open [the blank standard dashboard](assets/dashboard/strategic-plan-standard.html) in your browser after extracting the whole package. It works offline without a server or Python. It contains no personal plan or example person's answers.

The dashboard is a read-only view of saved knowledge. To update a personal view, your AI saves the source, rebuilds the HTML, and you reload the open page. Update my view provides a copyable request; it cannot send a message or save changes itself.

## What you will create
- A Current Year Wrap & Recap, distinguishing results so far from forecasts.
- Stable Purpose, Tenets, and GRIT (your long-term aspirational north star).
- An action-oriented Word of the Year with a short personal definition of its action and impact.
- One core annual Target Objective (TO) per pillar.
- Optional quarterly supporting TOs, normally 1–3 per pillar, with weights totaling 100% within each pillar/quarter.
- Clear counting definitions, dated progress, reviews, and year-to-year history.

Plan one quarter at a time, or make future quarters provisional. Lock accepted commitments and activate them when requested; activation alone does not change measurement windows or invent progress. Keep projects and task lists in your existing system.

## File-capable setup
The initializer and builder use Python 3.10 or later. From this skill folder, your AI can run:

```text
python scripts/init_plan.py <new-private-folder> --name <your-name> --initials <your-initials> --year <planning-year>
python scripts/build_dashboard.py <personal-folder>/plan.json
```

The initializer refuses an existing destination and creates a private skill copy, knowledge.md, plan.json, and outputs/strategic-plan.html. The structured plan is authoritative; HTML is derived. No Python installation is needed just to view an existing HTML file. Plain chat can guide the process and draft updates, while persistence and rebuilding require a file-capable environment.

## Personal Brand System and optional templates
Bring forward accepted Purpose and Tenets with source/version references. Personal style can supply accepted colors, local fonts, and permitted assets; the shared dashboard palette is not automatically a person's brand. Identity changes require review, and prior plans retain their snapshots. Integration is read-only unless an update is explicitly requested. See [PBS integration](references/pbs-integration.md).

Use the optional [moment](assets/templates/moment.md) and [experiment](assets/templates/experiment.md) templates for planning and reflection when useful. Native [Obsidian moment](assets/templates/obsidian-moment.md) and [Obsidian experiment](assets/templates/obsidian-experiment.md) variants are included. Configure actual vault/hub links in the private copy; the standard imposes no personal event names, quotas, or existing vault paths.

## Update safely
Download new standards into a separate folder. Keep a backup of the entire personal package and preserve its plan, knowledge, history, images, fonts, templates, and external note links.

```text
python scripts/plan_upgrade.py <new-standard-folder> <personal-folder>
```

This is a read-only preview. It flags customized files for a deliberate merge; it does not apply an upgrade. Never extract a new standard over a personal folder. See [maintenance](references/maintenance.md) and [dashboard guidance](references/dashboard.md).

## Privacy and validation
This repository and its ZIP contain the reusable standard and blank view only. Keep personal packages, backups, screenshots, source stories, financial records, and generated personal dashboards out of public repositories and issue reports. An offline view does not make your AI platform's processing local; its settings and costs still apply.

The release has passed synthetic-data build checks, browser interaction checks, offline/mobile visual review, link checks, and privacy checks. Those checks do not establish compatibility with every AI platform or replace a person's review of their plan. Test helpers are included; see [dashboard verification](references/dashboard.md).
