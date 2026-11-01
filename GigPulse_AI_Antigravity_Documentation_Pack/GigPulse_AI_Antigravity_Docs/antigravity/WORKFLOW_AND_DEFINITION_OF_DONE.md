# Agent Workflow and Definition of Done

## Task workflow

For every task create or update a small implementation-plan entry:

```markdown
## Task: <observable outcome>
- Scope:
- Relevant docs/contracts:
- Files expected to change:
- Risks/assumptions:
- Acceptance criteria:
- Tests/verification commands:
- Out of scope:
```

Then execute:
1. Inspect current implementation and test conventions.
2. Read the exact relevant skill and source documentation.
3. Add/update a failing focused test where practical.
4. Implement the smallest correct vertical slice.
5. Run focused tests and type/lint checks.
6. Run relevant regressions.
7. Perform browser inspection for UI changes.
8. Update docs, data/API schema and ADRs.
9. Record evidence and unresolved limitations.

## Definition of Done

### Functional
- Acceptance criteria pass.
- Empty/loading/error/permission states handled.
- No dead control or fake action appears functional.

### Data and ML
- Target, unit, interval, data source and quality visible.
- No target substitution or time leakage.
- Baseline compared with any candidate model on the same temporal holdout.
- Metrics and intervals are measured, not invented.

### Security/privacy
- User input validated; SQL parameterized.
- Ownership and access checks covered by positive and negative tests.
- No secret, credential or raw sensitive record leaks into browser/logs/errors.
- Import/commit/export/delete rules verified.

### UI/accessibility
- Responsive at mobile and desktop.
- Keyboard and focus behavior checked.
- Status is not conveyed by color alone.
- Charts have labels, units and an accessible alternative.
- Demo/synthetic labels remain visible.

### Maintainability
- Minimal dependency additions; no speculative abstraction.
- Tests, type checks and lint pass or failures are explicitly listed.
- Documentation and decisions reflect actual behavior.

### Evidence and reporting
- Report exact commands run and actual results.
- Include paths changed.
- Distinguish implemented, demonstrated, evaluated and proposed.
- State what has not been tested.
- No claim of deployment, security or model accuracy without evidence.

## Stop conditions

Stop before destructive actions, paid resource creation, account connection, external platform access, data publication, real-user data ingestion or a schema operation that could destroy user data. Explain the exact reason and ask for explicit approval where required.
