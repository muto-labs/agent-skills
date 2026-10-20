# Update a personal package safely
The public standard and your private personal copy are different packages. Never extract a new standard over your personal folder. Never run init_leader.py on an existing personal package.

1. Download and extract the new standard into a separate folder. Keep the current personal package where it is.
2. Ask your AI to review the update plan, preserving your knowledge, raw stories, voice guide, accepted assets, time, progress, deferrals, approvals and customized files.
3. Where Python/file access is supported, run the NEW standard's scripts/update_leader.py --standard <new-standard> --leader <existing-personal-folder>. This previews changes only.
4. Review conflicts. --apply creates a complete sibling backup before updates. Unchanged known standard files may update; customized/unknown files are preserved and listed for manual merge. Personal files never get replaced by standard defaults. SKILL.md remains personal; one link to the current standard-method reference is added.
5. The updater rebuilds and validates the existing workspace. Reload its usual HTML file. Check your name, profile, assets, progress/time and Fuel status. Keep the backup until satisfied.

Only after conflicts are merged, rebuild and rerun checks. A partial update must not claim the entire method is current. Do not install a version older than the personal package's recorded method. A failed update leaves its backup available; restore that folder separately rather than attempting an unreviewed overwrite. Backup copies also contain private data.

Without file tools, use the same separation and backup procedure manually, apply only the relevant method/UI changes, and ask for a concrete saved-file handoff. Browser refresh alone cannot apply an upgrade. This release recognizes the shipped 0.5.1 standard hashes; older or customized files may need manual review. Not every third-party Playground supports the helper.
