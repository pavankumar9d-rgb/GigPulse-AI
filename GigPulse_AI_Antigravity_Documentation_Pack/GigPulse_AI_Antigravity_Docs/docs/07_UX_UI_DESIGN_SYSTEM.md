# UX / UI Design System

## 1. Product design direction

**Direction:** “Mobility intelligence meets precision fintech.” The interface should look like an analytical product trusted with a worker's time and income, not a generic admin template or a neon AI landing page.

**Primary user outcome:** Understand what was earned, what may happen next, and which available work option is worth considering—with transparent assumptions.

**Design principles**
1. Clarity before decoration: every chart has a target, unit, time range and source label.
2. Trust through provenance: distinguish actual history, user-entered values, proxy labels and synthetic demo values visually and textually.
3. Actionable but non-coercive: show options, trade-offs and confidence; never automatically dispatch, accept or reject work.
4. Mobile-first responsiveness: a delivery partner may use a phone; dense model diagnostics remain desktop-friendly.
5. Accessible by default: keyboard support, visible focus, semantic controls, text alternatives, contrast and reduced motion.
6. Progressive disclosure: surface a simple summary first; keep methodology, intervals and model diagnostics one level deeper.

## 2. Information architecture

Primary navigation:
- **Overview** — earnings snapshot, forecast, alerts and top opportunities.
- **Earnings** — gross/net history, platform comparison, hourly breakdown and expenses.
- **Demand Map** — zone-by-time map/heatmap with selected demand target and data coverage.
- **Opportunity Planner** — compare platform × zone × time options under constraints.
- **Activity & Imports** — sessions, deliveries, expenses, CSV import and data quality.
- **Model Lab** — forecast evaluation, model version, feature explanations and limitations.
- **Settings & Privacy** — preferences, consent, export and deletion.

## 3. Core screen specifications

### Overview
- Header: selected date range, profile mode and visible data freshness.
- KPI strip: gross earnings, estimated net earnings, online hours, net per online hour.
- Main chart: actual history versus forecast, separated by line style and legend.
- Demand preview: selected-zone mini-map or zone list with timeframe.
- “Opportunity to review” panel: top candidate with estimate, uncertainty, travel cost and reasons.
- Data-quality banner: missing expenses, low coverage, synthetic/demo mode or stale inputs.

### Earnings
- Toggle gross/net; show formula and expense completeness.
- Time series by day/week, platform stacked comparison, hourly distribution.
- Distinguish online time from active time; never label one as the other.
- Drill down to contributing sessions, deliveries and expenses.

### Demand Map
- Hex/zone aggregation, with explicit map resolution and selected interval.
- Legend is numeric and target-specific (e.g. “observed completed deliveries / 30 min”).
- Show sample/coverage overlay so an empty zone is not mistaken for zero demand.
- Map interactions have an equivalent accessible table/list view.
- No worker live-tracking, exact route histories or precise home pin in the MVP.

### Opportunity Planner
- Inputs: time window, available platforms, maximum travel radius, minimum target net/hour, risk tolerance and personal exclusions.
- Comparison table/cards display expected net/hour, estimated demand, travel cost, interval and data quality.
- Explain score components and excluded candidates.
- CTA wording: “Review option” or “Save plan”; no “Start shift” or automatic dispatch.

### Activity & Imports
- Stepper: Upload → Map columns → Validate → Review errors → Commit.
- Preview rows and rejected samples safely; prevent formulas from being executed in exports.
- Show no data has been committed until the explicit commit action.

### Model Lab
- Model/version, target definition, training range, temporal test windows and baseline comparison.
- Metrics appropriate to target, interval calibration, residuals and segment error.
- Clearly mark `experimental`, `candidate`, `approved` or `retired`.
- Show known limitations and training-data source quality.

## 4. Suggested visual tokens (starting proposal)

These are initial tokens to validate with the installed UI/UX Pro Max and Impeccable skills—not a requirement to use every effect.

- Background: deep ink `#0B1220`; surface `#111C2E`; elevated surface `#17243A`.
- Primary accent: clear teal `#36C8B4`; secondary blue `#6B9CFF`.
- Positive: `#42B883`; warning: `#E5A84B`; negative: `#E16B76`.
- Text: high-contrast off-white `#EDF3FA`; muted text `#9AABC0`; borders `#26364D`.
- Typography: a readable system sans stack; use tabular numerals for financial KPIs. Do not depend on paid font APIs or network fonts.
- Radius: 10–14 px for cards; 8 px controls; avoid excessive pill-shaped everything.
- Spacing: 4/8 px base rhythm; maintain strong alignment and whitespace.
- Charts: use color plus line pattern/icon/label; never rely on color alone.

## 5. Interaction and motion

- Short, purposeful transitions (roughly 120–220 ms); respect `prefers-reduced-motion`.
- Avoid parallax, large shader backgrounds, video hero backgrounds or 3D scenes in analytical workflows.
- Skeletons only for loading; stable layout to prevent content shifts.
- Every asynchronous action has pending, success, empty and error states.
- Confirm destructive data deletion; allow cancel/back before CSV commit.

## 6. Responsive behavior

- Mobile: single-column KPIs, scrollable but labelled comparison table, map/list switch, sticky bottom action only when context-safe.
- Tablet: 2-column cards, compact charts.
- Desktop: persistent sidebar, multi-panel comparisons and diagnostics.
- Test narrow 360 px viewports and keyboard-only desktop operation.

## 7. Accessibility and content

- Target WCAG 2.2 AA as a design goal; verify with automated and manual testing.
- Semantic headings and landmarks; labels for inputs; chart summaries and data tables.
- Do not use color as the only status indicator.
- Explain “gross”, “net”, “online time”, “active time”, “demand proxy” and forecast intervals in plain language.
- Avoid misleading urgency, guaranteed income language, worker ranking, or punitive performance scores.

## 8. Design QA checklist

- The first screen answers “what is this number, for when, and from which data?”
- No synthetic values appear without a persistent demo-data label.
- No chart title says “demand” when it plots sample deliveries or completed orders.
- All major screens work at mobile, tablet and desktop widths.
- Focus, contrast, reduced motion, loading, empty and error states are reviewed.
- Use installed UI/UX Pro Max, Impeccable, React Bits and web-design-guidelines skills where relevant; inspect components and dependencies before adding packages.
