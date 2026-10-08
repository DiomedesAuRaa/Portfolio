# Portfolio workspace guidance

## Product and device scope

- This repository serves a public career portfolio plus a personal utilities/games hub through GitHub Pages. Keep the career page and its contact page completely separate from personal utilities/games and the diary. Do not add tool/diary navigation or promotional links to career pages.
- The flip-phone target is a Nokia 2780 opened in its ordinary browser. Laptop and iPhone support also matter. A 240×320 desktop render is a layout check, not proof of handset/browser compatibility.
- Keep useful content ahead of decoration. Offer a bookmarkable compact presentation, short labels, small batches, ordinary Home/Back/Previous/Next navigation and native controls. Do not force a fixed 240px width on laptops/iPhones or disable user zoom.
- Use semantic links/buttons/forms, visible focus, labelled fields and announced selected/loading/error states. Preserve browser Back and bookmarks. Scope game key capture to active gameplay; restore normal navigation in menus/dialogs and never hijack typing/select inputs. Installed KaiOS APIs/softkeys must not be assumed available in a browser.

## Preserve work and deployment behavior

- Start with `git status --short` and inspect the actual Pages configuration before changing build/hosting behavior. Existing edits to games, scores, podcast/sports configuration and feeds are user work; do not reset, overwrite, auto-stash or reformat them away.
- The cloud-synced checkout can lag the remote: compare without overwriting working-tree changes. Use a clean isolated checkout for deployment if necessary. Do not make a synced folder the sole runtime database/credential store.
- Audit-only requests are read-only. Implementation authorization permits scoped changes and verification; do not infer permission for unrelated cleanup or destructive history rewrites. Follow current user instructions rather than treating this file as an extra approval gate.
- Preserve established public URLs and links when reorganizing. Verify both career and utility entry points and all existing tool/game routes before publishing. Do not move/merge repositories solely for visual consistency.
- Read-only public data can share navigation without sharing repositories. A merge requires explicit publisher permissions, export boundaries, URL migration, rollback and ownership of every generator.

## Public/private boundary and security

- Public source code, published text, public media/preferences and public API identifiers may be intentional. Confirm intended disclosure rather than assuming all personalization is harmless or all identifiers are secrets. Locations, selected feeds, scores/progress and activity dates deserve deliberate classification.
- Never read, print, copy into reports or commit secret values from `.env`, `.envrc`, cookies, private keys, access tokens or credential stores. Report suspected embedded credentials by file/line/category with redaction. Do not dump resolved environments or configuration containing credentials.
- Runtime credentials, deployment state, operational/private notes, backups, private subscriptions/tokens and data the user wants private belong outside public source/history and public build output. `.gitignore`, hidden links, directories and separate project Pages paths are not access control. Removing a current file does not remove historical exposure.
- Project sites under the same `USERNAME.github.io` share a browser origin. Repository separation limits publisher scope but does not isolate localStorage/security origins; do not rely on it to contain script injection.
- Treat all RSS, API, Reddit, sports, Bible and podcast values as untrusted. Insert text with `textContent`; use event listeners, not interpolated inline handlers. Validate destination/audio URLs against intended HTTP(S) schemes. Regex tag stripping or escaping only apostrophes is not contextual sanitization.
- Keep public output curated by an explicit allowlist. Generator-only config, source scripts, AGENTS/reports, credentials, deployment files and backups must not enter Pages artifacts. Track public datasets/fields explicitly.
- Use least-privilege workflow/job permissions. Network fetching/dependency installation should not hold repository-write tokens. Validate artifacts before the narrowly scoped publishing job; serialize publishers and preserve unrelated main changes. Bound requests, retries and commands; redact errors.
- Public CORS proxies and contact providers are external trust/privacy dependencies. Do not classify a publicly required form/API identifier as a secret without evidence; inspect ownership, abuse controls, retention and URL/data handling separately.

## Data generation and verification

- Keep last-good data when a feed fails; label stale/error state and distinguish actual generation time from render time. Avoid rendering every item into a long keypad-navigation path when pagination is sufficient.
- Trace each page from source/config → generator/API → scheduler → credentials → published artifact. Do not invent missing producers: historical Reddit commits do not establish where its current job lives.
- Tests must use disposable output, fixture responses and local state. Do not run live publishing workflows, modify user datasets or exercise production mutations as test fixtures.
- Test keyboard-only laptop use, iPhone touch/layout, Nokia-sized reflow and actual Nokia browser navigation. Include browser chrome/keyboard space, zoom, long titles, missing/stale data and external request failures.
- Keep security/layout claims proportional to evidence. A bounded regex scan cannot prove no secrets; a screenshot cannot prove accessibility. Record current vs historical state, checks run and material limits.

- Weather defaults to Atlanta. Optional city/ZIP overrides remain device-local; never restore the previous personal default. Existing public Git history may retain old location data.
- Reddit RSS refresh is maintained in this repository; do not reactivate the disabled Pi producer with its hard reset and floating installs.

## Collective utilities interface

- All seven services, the tools hub and five games share assets/tool-ui.css and assets/tool-ui.js; games also use assets/game-ui.css. Keep navy surfaces, teal navigation/actions and amber focus indicators consistent. Preserve meaningful team, tile and game-state colors.
- Normal controls and compact controls on touch-sized screens keep 44px targets; the Nokia compact layout at widths up to 280px can use 29px controls. Verify vertical scrolling as well as horizontal overflow; legacy game styles must not trap browser navigation.
- Bible content currently comes from the World English Bible (WEB); do not label it ESV unless an actual ESV source is implemented and verified.
- Proposed future structure is career-only Portfolio at its existing URL, one pocket-tools repository for the complete utilities/games family, separate media-diary, and private/local media-stack operations. This is a recommendation, not authorization to rename/migrate repositories. Preserve old service bookmarks with explicit compatibility routes if migration is later requested.
