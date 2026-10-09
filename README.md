# Career site and legacy routes

This repository owns the career portfolio at `https://diomedesauraa.github.io/Portfolio/`. Its Pages workflow publishes only the explicitly listed career files and compatibility stubs.

The old utility URLs remain available as small HTML pages. They forward to `https://diomedesauraa.github.io/media-diary/tools/` and preserve each URL's query string and fragment. Their visible links also work with JavaScript disabled. Utility navigation and data publishing belong to the combined `media-diary` repository; this career repository must not publish podcast, Reddit, or other tool feeds.

At cutover, disable or remove the former Portfolio podcast and Reddit scheduled workflows after any active runs finish and the latest validated snapshots have been transferred. Keep the career Pages workflow enabled. Do not run old and combined feed publishers at the same time.

Any later scheduled news publisher belongs in the combined repository, must use the shared `combined-pages-publish` concurrency group, and must deploy the full curated Pages artifact.

Legacy podcast-manifest.json, reddit-digest.json and sports-config.json are frozen compatibility snapshots from 2026-10-09. Live data and apps are in media-diary/tools/. Keep these snapshots for existing clients during transition; they no longer refresh here.
