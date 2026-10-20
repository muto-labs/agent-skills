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

## Open, update and refresh — user handoff
On first creation, provide the actual clickable HTML file or downloadable package, its saved location and instructions to reopen it. Extract a ZIP before opening assets/dashboard/<initials>-personal-brand-dashboard.html in a browser. Keep the source package too, so future updates and exports are possible. Do not substitute a temporary preview for a delivered file. If a hosted preview is used, explain whether it expires and provide a supported download/export route.

Explain the three separate actions: the AI saves knowledge/assets; the AI rebuilds the workspace; the user reloads the open browser page. Reloading alone does not rebuild anything. The page is a static saved snapshot, not an auto-syncing app or an editor. Buttons open saved details; edits happen through the AI conversation or source files.

After successful save, rebuild and validation, say: “Your files and workspace are updated. Reload your open page to see the changes.” Supply the same stable file link. If only knowledge was saved, explicitly say the workspace is not yet rebuilt. Never claim an unsupported operation succeeded.

Check platform capability early. If file writing or execution is unavailable, explain the limit and return proposed updates plus concrete manual save/build instructions. If the platform uses a Playground, artifact or preview, verify its supported export/open route rather than assuming its code appears in file listings. A missing delivery route remains an open item, not a completed handoff. Ask the leader to confirm they can reopen the file when that cannot be tested directly.

Keep local/private, temporary preview and public website states distinct. The workspace embeds personal knowledge. Public publishing requires a separately reviewed public-safe version and explicit authorization. Do not call the workspace the source of truth: it renders the authoritative KB, state and asset files.

## AI-assisted Update my view
The compact Update my view button beside See what's next opens help, a copyable AI request and a reload action. The page cannot send that request to AI by itself. When a leader asks to update or refresh their view, use available tools to save approved changes, rebuild, validate and return the same file link. Do the work rather than sending the user command-line instructions when you can perform it. If files are unavailable, ask only for the current package/location needed to act; if execution is unavailable, give the smallest concrete fallback. Distinguish a normal data refresh from a standard-method upgrade; use the safe updater only when a newer standard is supplied/requested. Never overwrite personal data or silently merge customized conflicts. After success say “Your workspace is updated. Reload your open page,” and provide the real link. The reload button does not rebuild.

## Visual asset previews
For a visual asset, put a Markdown image preview near the top of its output document, plus named links to the export, editable source and companion text. The builder embeds linked local PNG/JPEG/GIF/WebP previews in the saved dashboard and indexes existing package-local file links. Rebuild after image changes. Check the actual detail preview and file links, not just file existence. The source package is still needed for editing and opening original files; no external media is fetched or embedded.

## Channel shortcuts
Use dashboard-config.json channel_links for a compact links row below the leader identity. Each entry records label, url, personal/business scope and source. Include personal LinkedIn, organization LinkedIn, YouTube and website only when relevant and sourced; use clear organization labels and do not imply ownership from a public listing. Reuse known URLs, confirm ambiguous matches and never invent missing ones. The clean standard has an empty list; hide the row until links exist. Ask only for missing links in the chosen scope, without adding required channels. Links open in a new tab; only HTTP(S) URLs render. Preserve this leader-specific configuration during upgrades.

Channel shortcuts use Font Awesome Free 6.7.2: LinkedIn and YouTube brand icons, plus the solid globe for other websites. Keep visible labels, mark decorative SVGs aria-hidden and non-focusable, inherit UI color and embed icons in app.js for offline standalone and dist views. Original SVGs and license/attribution remain in assets/dashboard/icons. No remote kit, CDN, icon font or runtime request is needed. Verify icons with networking disabled.
