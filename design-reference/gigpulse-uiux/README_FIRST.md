# GigPulse AI — UI/UX Reference Pack

## Contents
- `reference_screenshots/01_target_visual_reference.png` — the target visual style supplied by you.
- `reference_screenshots/02_current_gigpulse_dashboard.png` — the current dashboard to improve.
- `ANTIGRAVITY_PROMPT.md` — the full ready-to-paste redesign task.
- `UI_DIRECTION.md` — palette, layout, and component principles.
- `online_image_references/IMAGE_SOURCES.md` — three curated Unsplash sources and attribution details.
- `online_image_references/preview_online_references.html` — browser preview using remote images.
- `scripts/download_online_references.ps1` — tries to download the images into the pack on Windows.

## Important note about image downloads
The build environment used to prepare this ZIP could not resolve external image hosts, so it could not store the actual Unsplash image binaries locally. The ZIP includes the two screenshots you supplied, the verified Unsplash source pages and image URLs, a preview page, and a PowerShell downloader for Antigravity/your PC. The pack does not pretend that remote photos are already embedded.

## How to use
1. Extract the ZIP.
2. Open the GigPulse AI workspace in Antigravity.
3. Copy `ANTIGRAVITY_PROMPT.md` into a new Antigravity conversation.
4. Attach or copy the extracted reference pack folder into the project workspace (for example `design-reference/gigpulse-uiux/`).
5. Tell Antigravity to read that folder before editing `apps/web`.

Do not ask Antigravity to rebuild the backend or machine-learning code unless it finds an actual regression. This task is specifically a UI/UX redesign with regression protection.
