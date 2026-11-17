# Contributing to AURIS build documentation

- This is an **engineering concept baseline**, not a production-release repository.
- A change to a component, electrical requirement, scope or product claim needs an ADR update in `docs/14-DECISION-REGISTER.md`.
- Do not promote `CANDIDATE`, `PROPOSED` or `OPEN` items to `SELECTED` or `VERIFIED` without evidence (datasheet rev, circuit calculation, measured test, dated reviewer).
- Treat files in `references/` as read-only historical originals.
- Attach raw benchmark data and reproducible test scripts to validation changes.
- Avoid commit of any API credentials, SIM identifiers, real deployment coordinates, private recordings, or customer information.
- Match firmware/backend schema revisions and support migrations; `specs/*.example.json` is illustrative only.
- Use issues with requirement IDs from `docs/16-REQUIREMENTS-TRACEABILITY.md` and link the verification evidence.
