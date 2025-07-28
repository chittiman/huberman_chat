# Gemini Project Instructions: huberman_chat

## Onboarding Instructions for New Sessions

To quickly understand the project state without re-analyzing the entire codebase, follow these steps:

1.  **Read the Codebase Analysis:** This provides a complete overview of the project structure and data pipeline.
    -   `CODEBASE_ANALYSIS.md`

2.  **Review the Latest Changes:** This file logs all recent modifications.
    -   `changes.md`

3.  **Consult the Most Recent Session Summary:** To get the latest conversational context, review the most recent summary file.
    -   Check the `session_summaries/` directory.

By reading these key documents first, I can immediately get up to speed on the project's status, our recent work, and your goals.

## Core Development Workflow

1.  **Plan Before Implementing:** For any significant new feature, we must first discuss and agree on a plan.
2.  **Document the Plan:** Before writing implementation code, the final plan must be saved to a new markdown file in the `.gemini/planning/` directory.
3.  **Use Test-Driven Development (TDD):** Default to a TDD workflow. Create a test file and write failing tests *before* implementing the corresponding code.
4.  **Manage Dependencies Correctly:** Always use `uv add <package>` to add new Python dependencies. This ensures `pyproject.toml` is updated automatically.

## Session End Ritual

When I am told to "Prepare to close the session," I will perform the following steps:

1.  **Create Session Summary:** Create a new, timestamped session summary file in the `session_summaries/` directory, documenting the work done during the current session.
2.  **Update Changelog:** Ensure the `changes.md` file is up-to-date with all modifications made during the session.
3.  **Review Project Documentation:** Proactively review all files in the `.gemini/` directory (especially `CODEBASE_ANALYSIS.md`) and propose updates to ensure they accurately reflect the project's current state.
4.  **Final Git Status:** Run `git status` to provide a final overview of the repository's state.
5.  **Propose Final Commit:** If there are uncommitted changes, propose a final commit message to save them.
