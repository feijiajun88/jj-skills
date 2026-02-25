---
name: skill-evolution-manager
description: "The evolution hub for the entire AI skills system. It is responsible not only for optimizing individual Skills but also for cross-Skill experience review and sedimentation."
github_url: "https://github.com/feijiajun88/jj-skills"
github_hash: ae3be7b98639c062dd6a78ad4ebd1a128d57c81d
version: 1.0.0
created_at: 2026-02-25
updated_at: 2026-02-25
license: MIT
---

# Skill Evolution Manager

This is the "evolution hub" for the entire AI skills system. It is responsible not only for optimizing individual Skills but also for cross-Skill experience review and sedimentation.

## Core Responsibilities

1.  **Session Review**: Analyze performance of all Skills invoked at the end of conversation.
2.  **Experience Extraction**: Convert unstructured user feedback into structured JSON data (`evolution.json`).
3.  **Smart Stitching**: Automatically write sedimented experiences into `SKILL.md`, ensuring persistence and preventing overwriting during version updates.

## Usage Scenarios

**Trigger**:
- `/evolve`
- "Review the previous conversation"
- "I think that tool wasn't working well, note it down"
- "Save this experience to the Skill"

## The Evolution Workflow

### 1. Review & Extract

When user triggers a review, Agent must:

1.  **Scan Context**: Identify points of dissatisfaction (errors, wrong style, parameter errors) or satisfaction (specific Prompts worked well).
2.  **Locate Skill**: Determine which Skill needs evolution (e.g., `yt-dlp` or `baoyu-comic`).
3.  **Generate JSON**: Build the following JSON structure in memory:
    ```json
    {
      "preferences": ["User prefers downloads to be muted by default"],
      "fixes": ["ffmpeg path needs escaping on Windows"],
      "custom_prompts": "Always print estimated duration before execution"
    }
    ```

### 2. Persist

Agent calls `scripts/merge_evolution.py` to incrementally write the above JSON into the target Skill's `evolution.json` file.
- Command: `python scripts/merge_evolution.py <SKILL_NAME>`

### 3. Stitch

Agent calls `scripts/smart_stitch.py` to convert `evolution.json` content into Markdown and append to the end of `SKILL.md`.
- Command: `python scripts/smart_stitch.py <SKILL_NAME>`

### 4. Align

After `skill-manager` updates a Skill, Agent should proactively run `smart_stitch.py` to "re-stitch" previously saved experiences back into the new version documentation.

## Core Scripts

- `scripts/merge_evolution.py`: **Incremental merge tool**. Reads old JSON, deduplicates and merges new Lists, saves.
- `scripts/smart_stitch.py`: **Documentation generator**. Reads JSON, generates or updates `## User-Learned Best Practices & Constraints` section at the end of `SKILL.md`.
- `scripts/align_all.py`: **Bulk alignment tool**. One-click traverses all Skill folders, re-stitching experiences from existing `evolution.json` back to corresponding `SKILL.md`. Commonly used after `skill-manager` batch updates to restore experiences.

## Best Practices

- **Don't directly modify SKILL.md body**: Unless it's an obvious typo. All experience corrections should go through the `evolution.json` channel to ensure experiences aren't lost during Skill upgrades.
- **Multi-Skill Collaboration**: If a conversation involves multiple Skills, execute the above process for each Skill in sequence.
