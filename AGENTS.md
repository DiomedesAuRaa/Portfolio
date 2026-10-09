# Career repository guidance

- Preserve the career homepage and contact page byte for byte during the tools migration. Keep career styling and navigation separate from the personal utilities hub.
- `scripts/build_career.py` is the Pages artifact boundary. Extend its explicit file list only for career content or named legacy compatibility routes; never recursively publish source files.
- Keep the established career URL and keep utility/game legacy routes as HTML stubs pointing to the matching route under `https://diomedesauraa.github.io/media-diary/tools/`.
- Each stub must preserve the original query string and fragment in both its automatic redirect and visible fallback link.
- Podcast, Reddit, news, game and other personal tool data/workflows are owned by the combined `media-diary` repository. Do not add their scheduled producers here.
- Before cutover, transfer the latest validated feed snapshots, finish active old feed runs, and disable/remove the former Portfolio podcast and Reddit workflows. Keep this repository's career Pages workflow active.
- Any later news publisher belongs in the combined repository and must share its `combined-pages-publish` workflow concurrency group and complete-artifact build.
- Verify the explicit career artifact, the original home/contact files, and all legacy route destinations without deploying from this staging tree.
