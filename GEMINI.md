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

## Session End Ritual

When I am told to "Prepare to close the session," I will perform the following steps:

1.  **Create Session Summary:** Create a new, timestamped session summary file in the `session_summaries/` directory, documenting the work done during the current session.
2.  **Update Changelog:** Ensure the `changes.md` file is up-to-date with all modifications made during the session.
3.  **Final Git Status:** Run `git status` to provide a final overview of the repository's state.
4.  **Propose Final Commit:** If there are uncommitted changes (like the session summary or changelog), propose a final commit message to save them.