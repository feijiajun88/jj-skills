---
name: skill-manager
description: "Lifecycle manager for GitHub-based skills. Can batch-scan skill directories, check GitHub updates, and perform guided upgrades."
github_url: "https://github.com/feijiajun88/jj-skills"
github_hash: ae3be7b98639c062dd6a78ad4ebd1a128d57c81d
version: 1.0.0
created_at: 2026-02-25
updated_at: 2026-02-25
license: MIT
---

# Skill Manager

Lifecycle manager for GitHub-based skills. Can batch-scan skill directories, check GitHub updates, and perform guided upgrades.

## Core Functionality

1. **Audit**: Scans local skill folders, identifying those with `github_url` metadata.
2. **Check**: Queries GitHub via `git ls-remote`, comparing local commit hash with remote HEAD.
3. **Report**: Generates a status report, identifying which skills are "outdated" or "up-to-date".
4. **Update Workflow**: Provides structured workflow to guide the Agent in upgrading skill wrappers.
5. **Inventory**: Lists all local skills and supports deletion operations.

## Usage

**Trigger**:
- `/skill-manager check` or "Scan my skills for updates"
- `/skill-manager list` or "List my skills"
- `/skill-manager delete <skill-name>` or "Delete skill <skill-name>"

## Workflow

### 1. Check Updates

- Run the scanner: Execute `scripts/scan_and_check.py` to analyze all skills.
- View report: Script outputs a JSON summary, Agent presents results to user (e.g., "Found 3 outdated skills: `yt-dlp` (50 commits behind), `ffmpeg-tool` (2 commits behind)...").

### 2. Update a Skill

- Trigger: "Update [skill-name]" (requires prior check).
- Fetch new context: Agent fetches the new README from remote.
- Diff: Compare new README with old `SKILL.md`, identify new features, deprecated parameters, or usage changes.
- Refactor:
  - Rewrite `SKILL.md` to reflect new features.
  - Update `github_hash` in Frontmatter.
  - If CLI args changed, try to update `wrapper.py`.
- Verify: Run a quick verification if supported.

## Scripts

- `scripts/scan_and_check.py`: Core scanner script, parses Frontmatter, fetches remote tags, returns status.
- `scripts/update_helper.py`: (Optional) Helper tool to backup files before updating.
- `scripts/list_skills.py`: Lists all installed skills with their types and versions.
- `scripts/delete_skill.py`: Permanently removes a skill folder.

## Metadata Requirements

Depends on `github-to-skills` metadata schema:
- `github_url`: Source URL of the skill.
- `github_hash`: Current commit hash.

## Notes

This skill manager does **not automatically execute any actions**. It only provides scanning, reporting, and guided update workflows. All updates or deletions must be explicitly confirmed by the user before the Agent executes them.
