# Stage 07: Promotion & SoC Integration — Postmortem

**Date:** 2026-07-21
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/07_promote_stage
**Verdict:** PASS (11/11 stage self-audit) with a §G.16 independence note — audit retry 0.

## What Went Well
- **Clean promotion ledger.** 12 modules resolved: 5 promoted, 6 reuse, 1 conditional (caravel_wrapper), 0 blocked — internally consistent across `promotion_summary.json`, `promotion_report.json`, and per-module reports.
- **Provenance intact.** Each promoted/created module cites a real `synthesis_log`; the SoC log path (`04_frontend_stage/.../argus_soc_synth.log`) resolves to a 1.69 MB file (§5.11).
- **Reuse manifests complete.** 6 `reuse_manifest.json` (5 promoted + argus_soc), each with qualification (lint/synth/formal/equiv/verify) and license — §5.3/§5.15 satisfied.
- **Upstream gates cited.** Both frontend and verification `audit_pass.json` referenced with verdict PASS before promotion (§5.9/§5.10).
- **Correct deferral of the wrapper.** `caravel_wrapper` marked CONDITIONAL with an explicit "Stage 9 artifact" reason rather than force-promoted with null fields.

## What Went Wrong
- **The gate was self-audited (§G.16).** `audit_pass.json` field `audit_engine: "manual (verification-agent)"`, note "Claude Opus 4.8 unavailable — OAuth session expired." An independent auditor did not adjudicate this gate.
- **Filename convention drift (§5.1).** `promotion_summary.json` where the rubric names `promotion_summary.md` — a still-open v1 item.
- **Suspicious SoC FF count.** `argus_soc/promotion_report.json` shows `dff_count: 0` with 154,291 cells — implausible for a design containing Ibex; a synth-view artifact, but it was promoted without a sanity note.

## Root Causes
- **5 Whys (self-audit):** gate lacked an independent auditor → Opus OAuth session expired on the headless server → no fallback independent-auditor credential was provisioned → the stage agent filled the gap manually → the framework has no hard interlock forbidding self-adjudication when the auditor is unavailable. Root cause: no provisioned independent-auditor fallback + no §G.16 hard stop.
- **dff_count 0:** the promotion report copied a flattened/blackboxed synth metric without cross-checking against the eventual P&R sequential-cell count (3,498 in backend).

## Fixes Applied
- None (retry 0 PASS). No BLOCKED modules, so no recursive-reentry/rework was dispatched (§5.5 vacuously satisfied).

## Iterations
- 0 reworks.

## Framework Improvements Recommended
- **Hard §G.16 interlock:** if the independent auditor is unavailable, the gate must BLOCK and escalate to Vera, not fall back to stage-agent self-audit. Provision a standby independent-auditor credential for headless runs.
- **Cross-check promotion metrics against downstream reality:** flag `dff_count: 0` on any SoC that instantiates a CPU; reconcile against backend sequential-cell count.
- **Resolve the `promotion_summary.md`/`.json` filename mismatch** once, project-wide, to close the recurring §5.1 finding.

## Metrics
- Duration: 2026-07-20 ~14:07–14:15 · Rework: 0 · Modules: 5 promoted / 6 reuse / 1 conditional / 0 blocked
- SoC synth: 154,291 cells / 2,091,171 µm² · Reuse manifests: 6 · Failing tests in promoted set: 0
