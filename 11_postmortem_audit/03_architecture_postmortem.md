# Stage 03: Architecture — Postmortem

**Date:** 2026-07-21
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/03_architecture_stage
**Verdict:** PASS (8/8) — audit retry 0, cost $0.28

## What Went Well
- **Complete, self-consistent blueprint.** 12 modules in `blueprint.json` map 1:1 to M01–M12 in the 1,183-line `ARCHITECTURE.md`; no phantom or missing modules.
- **Full golden alignment.** `arch_comparison.json` = 19/19 IDENTICAL against golden (seed 42) covering every functional path (bus, SRAM, all peripherals, IRQ, sleep/wake) — §2.8 coverage gap of the IP-005 v6 kind was avoided.
- **Honest empty analog manifest.** `analog_manifest.json` declares `blocks: []` explicitly with a WONT-001 rationale rather than omitting the file — the exact §2.9 "empty is recorded, not assumed" behavior.
- **Schema-valid contracts.** `memory_map.json` (8 KB) carries `{core, regions, peripherals}`; downstream firmware later consumed it cleanly (addresses matched at Stage 05).

## What Went Wrong
- **Block diagram is HTML, not PNG/mermaid.** `block_diagrams/top_level.html` satisfies the rubric but is less portable/diff-able than a committed PNG or in-markdown mermaid block.
- **Single in-document diagram reference.** Only 1 diagram callout inside ARCHITECTURE.md; the visual lives entirely in the sidecar HTML.

## Root Causes
- The HTML diagram is a tooling-default choice (interactive top-level view) rather than a defect; no rubric threshold was missed.

## Fixes Applied
- None required — stage passed on the first audit with no rework.

## Iterations
- 0 reworks. Retry 0, PASS 10/10 (stage self-audit) corroborated by this independent 8/8 re-verification.

## Framework Improvements Recommended
- Add a rubric note that block diagrams delivered as HTML should also emit a static PNG snapshot for archival/diff, or embed a mermaid source block in ARCHITECTURE.md.
- Consider auto-checking that every `blueprint.json` module count equals the `arch_comparison.json` module coverage denominator (here 12), to keep §2.8 mechanical.

## Metrics
- Duration: within stage window (2026-07-20 03:54–04:01) · Cost: $0.28 · Rework: 0 · Violations: 0
- Artifacts: ARCHITECTURE.md (1,183 lines), blueprint.json (12 modules), memory_map.json, analog_manifest.json (empty), arch_comparison.json (19/19), top.sdc, cdc_plan.md
