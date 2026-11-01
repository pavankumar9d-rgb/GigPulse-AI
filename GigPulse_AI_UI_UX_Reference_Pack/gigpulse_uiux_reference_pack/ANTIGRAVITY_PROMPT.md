# ANTIGRAVITY TASK: GIGPULSE AI — PREMIUM UI/UX REDESIGN

You are the lead product designer and senior frontend engineer. Your task is to redesign the existing GigPulse AI web application so that its visual quality and information hierarchy closely follow the supplied target reference, while preserving all working research, machine-learning, API, and database functionality.

## 0. Read these references first

Open and inspect every file in this reference pack:
- `reference_screenshots/01_target_visual_reference.png` — the visual direction to follow.
- `reference_screenshots/02_current_gigpulse_dashboard.png` — the current implementation that must be improved.
- `UI_DIRECTION.md` — design system and layout requirements.
- `online_image_references/IMAGE_SOURCES.md` — curated image sources and licensing notes.

If the `online_image_references` folder does not yet contain downloaded image files, run `scripts/download_online_references.ps1` from PowerShell. If an image download fails, record the failure and continue; do not waste time retrying indefinitely. Treat downloaded photos as optional contextual assets, not mandatory dashboard decoration.

## 1. Understand the existing app before editing

Inspect the complete current frontend in `apps/web`, including all routes, components, styles, chart libraries, fonts, API client, and state management. Also inspect the backend API contracts and the README/VERIFICATION documents so you understand the exact real data available.

The existing application reportedly has 11 functional areas: Overview, Earnings Analytics, Earnings Predictor, Deliveries, Zone Demand, Platforms, Opportunity Planner, Expenses, Data Imports, Model Lab, and Settings & Privacy. Verify the actual implementation and preserve all working sections and interactions.

Do not replace the application with a static mockup, a Figma-like screenshot, an unrelated starter template, or hardcoded sample cards.

## 2. Visual objective

The target is a premium, understated mobility-operations cockpit: near-black graphite surfaces, restrained acid-lime highlights, precise typography, strong negative space, elegant compact charts, and a clear dashboard grid.

The current blue/navy admin-template appearance must be removed. In particular:
- Remove the dominant blue background and blue gradients.
- Remove the bright teal/blue/amber mixture as the primary visual language.
- Remove repeated thick bordered cards and excessive pill badges.
- Remove generic dashboard-template styling and unnecessary decorative icons.
- Avoid oversized headings, excessive explanatory copy, and cramped data density.
- Do not fill the interface with random stock photography.

The target screenshot is a style reference, not a requirement to copy irrelevant taxi, passenger, battery, or speed metrics. Adapt its visual language to GigPulse's real gig-worker analytics.

## 3. Design system

Use `UI_DIRECTION.md` as the design source of truth. Starting palette:
- App background: #080907 or #0B0C0A.
- Main surfaces: #11130F and #171914.
- Raised/hover surfaces: #1D2019.
- Hairline separators: #292D24.
- Primary accent: acid lime around #D7F52F / #D9FF36.
- Text: #F2F3EC.
- Secondary text: #A0A397.
- Muted text: #717568.
- Semantic red/amber only for actual warning/error states, used sparingly.

Use one consistent type family already available in the repo or a reliable system fallback. Use tabular numerals for KPI values. Establish clear type sizes for page title, section title, data label, helper text, and metadata.

Surfaces should feel quiet and tactile: subtle tonal separation, fine low-contrast dividers, modest radii, and restrained shadows. Do not use glassmorphism, neon glows everywhere, excessive gradients, or animated backgrounds.

## 4. Application shell and information architecture

Build a cohesive shell across all 11 sections:
- Slim top header with GigPulse identity, current worker selector, small synthetic-data/research indicator, and compact settings/profile actions.
- Narrow left icon rail or compact sidebar inspired by the target reference. Use clear active-state lime treatment. On small screens, convert it to a usable drawer or bottom navigation without losing navigation access.
- Main content area on a disciplined responsive grid with consistent gutters and vertical rhythm.
- No giant warning banner consuming the first screen. Keep the synthetic-data advisory as a thin, legible strip or small status label that remains visible without dominating the UI.
- Use consistent page headers, contextual filters, and section layouts.

The 1440×900 desktop viewport should feel composed and balanced, with the most important information visible without excessive scrolling. Do not force every section into identical cards; use varied, purposeful layouts.

## 5. Redesign the Overview first, then propagate the system

The overview should borrow the target screenshot's composition and rhythm while showing GigPulse data:

A. Top overview row:
- A compact “Next shift / opportunity outlook” or strongest existing recommendation module using actual API data.
- One clear primary earnings figure or forecast with its time basis and uncertainty range where available.
- Compact supporting KPIs for gross earnings, expenses, net earnings, and online duration. Avoid five huge cards with identical styling.

B. Main visual row:
- Earnings over time: clean custom chart with readable axes, subtle grid, lime emphasis, hover tooltip, and real date filtering.
- Zone demand: use a real zone-intensity visualization, ranked zone list, or heat matrix based on actual records. Do not invent map coordinates or show a fake map if the backend does not provide geospatial coordinates.
- Shift composition: active versus waiting duration using a restrained ring or segmented bar, sourced from real backend values.

C. Supporting row:
- Recent delivery/session activity, compact and scannable.
- Platform earnings share using real platform totals.
- Top opportunity/recommendation with net hourly rate, platform, zone, suggested time, and a concise explanation from the optimizer.

Keep the page visually close to the target's balance and spacing, not necessarily the same widget names.

## 6. Redesign every remaining view

Maintain the same design language and interaction quality across all 11 views:

1. **Earnings Analytics:** actual gross/net trends, platform breakdown, date filters, clear summary hierarchy, and readable records.
2. **Earnings Predictor:** focused input form, concise prediction result, Q10/Q50/Q90 visualization, prediction assumptions, and advisory wording.
3. **Deliveries:** high-quality table/list with date, platform, zone, payout, tip/incentive, duration, and pagination/filtering where available.
4. **Zone Demand:** multi-step 30-minute forecast, zone selector, actual vs predicted data, confidence band, demand-tier legend, and target-type clarity.
5. **Platforms:** meaningful comparison, earnings mix, completed counts, average payout, and tip metrics from the API.
6. **Opportunity Planner:** candidate ranking, risk profile, constraints, expected gross/expenses/net rate, and transparent explanation. Make controls usable and results easy to compare.
7. **Expenses:** clear category breakdown, actual expenses over time, operating expense ratio, and source records.
8. **Data Imports:** a calm, explicit upload → validation → review → commit flow. Show row counts, errors, duplicate/idempotency information, and never commit silently.
9. **Model Lab:** compact evaluation tables, selected model, baselines, MAE/RMSE/WAPE, uncertainty coverage, train/retrain state, and honest synthetic-data disclaimer.
10. **Settings & Privacy:** worker profile, export, destructive purge confirmation, and data/privacy explanation. Destructive actions must require a clear confirmation step.
11. **Overview:** implement as described above.

## 7. Data integrity — absolute requirement

- All displayed values must come from the existing API and actual SQLite-backed dataset.
- Do not hardcode or fabricate KPIs, prediction values, zone demand, maps, activity, performance percentages, avatars, or activity events.
- Do not create buttons or controls that do nothing.
- Preserve the existing ML models, inference APIs, database, schema, and business logic.
- Keep money consistent with the backend's integer-paise convention. Inspect each response field's units before formatting. Never double-convert paise to rupees or vice versa.
- Use Indian number formatting and ₹ currency display where appropriate.
- Distinguish gross earnings, expenses, and net earnings clearly.
- Keep synthetic-data and advisory-estimate disclaimers visible but unobtrusive.
- Do not label synthetic values as real-time/live market data.

## 8. Images and visual assets

The target reference is primarily a UI composition, not a photography-led design. Use downloaded online photos only where they add genuine product context, such as a restrained empty state or one optional contextual image panel. Do not place large stock photos in every card.

Do not use stock-person photos as the worker's identity/avatar. Use real profile data if present; otherwise use initials or a neutral generated avatar treatment.

Use local assets after download; do not depend on hotlinked image URLs at runtime. Record attribution and source URL in the project. Do not use watermarked, paywalled, or ambiguously licensed images.

Prefer native CSS/SVG/chart components and the icon library already installed. Do not install large UI kits or replace the whole component stack merely for appearance.

## 9. Interaction, accessibility, and responsive behavior

- Every button, select, tab, filter, table action, and navigation item must work.
- Add loading, empty, error, and success states.
- Use keyboard navigation, visible focus states, semantic labels, and accessible contrast.
- Respect reduced-motion preferences.
- Use short 120–200ms transitions only where they improve feedback.
- Check at 1440×900, 1280×800, 768px tablet, and 390px mobile widths.
- Prevent horizontal overflow and clipped dialogs/tables.

## 10. Iterative visual QA — do not stop after the first pass

Perform at least three real review passes:

**Pass 1 — Structure:** implement the design tokens, shell, navigation, and Overview layout. Run the frontend and compare a screenshot to `01_target_visual_reference.png`.

**Pass 2 — Consistency:** redesign all remaining sections and verify charts, tables, forms, controls, and empty/error states. Compare screenshots across sections.

**Pass 3 — Polish:** correct spacing, typography, visual density, card treatment, alignment, chart legibility, mobile layout, focus states, and any visual mismatch. Remove remaining generic-template styling.

Use the browser/Playwright screenshot tooling already available in the project or environment. Do not claim visual review if no screenshot was actually captured. If browser automation is unavailable, run the app and state exactly what visual checks could and could not be performed.

## 11. Regression and build verification

After changes:
- Run `npm run build` in `apps/web`.
- Run the complete Python test suite from the repository root.
- Verify every dashboard section loads real API data.
- Test prediction, demand forecast, recommendations, filters, data import validation/commit flow, model lab, export, and destructive-action confirmation where applicable.
- Inspect browser console and network errors.
- Fix regressions before declaring completion.
- Do not alter backend or ML functionality merely to make the redesign easier.
- Do not commit, push, reset, or force-push Git history.

## 12. Final report

Provide:
1. Files changed and why.
2. Sections redesigned.
3. Screenshots captured and viewport sizes reviewed.
4. Actual commands and their results.
5. Frontend build result.
6. Full Python test result.
7. Verified API integration and interaction flows.
8. Remaining visual or functional issues.
9. Git status summary.

Do not declare the work complete unless the redesigned UI is genuinely implemented, all 11 sections remain functional, the backend data is real, the build passes, and the existing tests pass.

Start now. Inspect first, redesign the actual project, review it visually in multiple passes, fix flaws, and finish the implementation. Do not stop to ask for routine approval between these steps.