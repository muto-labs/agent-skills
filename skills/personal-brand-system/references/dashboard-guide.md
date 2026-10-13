# Personal Brand dashboard lifecycle
Standard 0.3.0 | 2026-10-11 | Same minimal Muto-palette design used in Customer Zero.
## Create at the beginning
Initialize a leader package with scripts/init_leader.py (see SKILL.md), then create its dashboard before the first interview. Name/initials are enough. Missing profile, role, purpose, voice examples and assets produce honest empty states; do not invent facts or copy another leader's data.
Outputs: assets/dashboard/<initials>-personal-brand-dashboard.html (self-contained browser file), assets/dashboard/dist/ (server version), and references/dashboard-manifest.json. Viewing needs no Python/server.
## Keep current during the process
After any meaningful saved KB, progress, time, asset, acceptance, deferral or configuration change:
1. Update the authoritative KB/state/asset index, and readable progress snapshot as needed.
2. Run python scripts/build_dashboard.py from the package (or pass its path).
3. Run python scripts/check_package.py <package> and check dashboard-manifest.json against state.
4. Present the same dashboard path; after rebuilding an open browser tab must reload.
Do this before ending the turn. No new permission is needed for the authorized local refresh. It is refresh-on-save workflow, not a live MAGE connection or background watcher.
If a platform cannot execute/write files, return proposed source/data/dashboard updates and state exactly that the local snapshot has not been refreshed. Never claim an update succeeded when unavailable.
## Design and personalization
Maintain the shared layout/styles and Muto palette: #FC7935, #104F72, #006799, #25AAE1, #303D49, #00C8E5. Orange accent. All 10 core components and the separate Fuel cards stay visible; distinguish built infrastructure from reviewed leader work.
Name and prefix come from onboarding-state.json. Purpose and role derive from the current accepted profile (purpose may fall back to current KB). Component progress/status derives from checklist. Current assets and acceptance derive from asset-index.md; earlier versions remain available. Do not hardcode personal values in the shared template.
## Privacy
The dashboard embeds private KB/source details. Keep local unless a separate public-safe export is reviewed. Public publishing is not implied by dashboard creation. Scripts are optional for viewing; the generated file is portable.


## First welcome and visual tour
Offer the dashboard early. Follow [opening and usage instructions](kickoff-guide.md#open-and-explore-your-dashboard), supply the actual file, explain the initial empty state and keep the visual tour optional. Distinguish exploring saved details from editing through the AI conversation.
