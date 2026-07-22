# Postmortem Report — [STAGE_NAME]

**Project:** [PROJECT_ID]  
**Stage:** [01_business_stage — 10_document_stage]  
**Auditor:** Claude Code Opus 4.8 (Final: Claude Code Fable 5)  
**Date:** [YYYY-MM-DD]  
**Status:** [DRAFT | FINAL]

---

## 1. Executive Summary

*One paragraph. What was this stage, what were the key results, and what is the single most important takeaway for the next project iteration?*

> [2-4 sentences]

---

## 2. Stage Context

| Field | Value |
|-------|-------|
| Stage name | |
| Input artifact(s) | |
| Output artifact(s) | |
| Agent(s) involved | |
| Skills dispatched | |
| Wall-clock duration | |
| API cost (USD) | |
| Iterations / retries | |
| Final verdict | PASS / FAIL |

---

## 3. Timeline of Key Events

*Chronological list of significant events — successes, failures, decisions, agent restarts, scope changes. ISO 8601 timestamps.*

| Timestamp (UTC) | Event | Impact |
|-----------------|-------|--------|
| | | |
| | | |
| | | |

---

## 4. What Went Well

*Actions, decisions, tooling, or patterns that WORKED. These should be preserved and replicated in future projects.*

### 4.1 [Category — e.g. Agent Workflow]

- **Finding:** [What worked, with evidence]
- **Why it mattered:** [Quantified impact]
- **Preserve:** [How to replicate this in future iterations]

### 4.2 [Category]

...

---

## 5. What Went Wrong

*Failures, blockers, errors, or suboptimal outcomes. Be specific — reference exact files, line numbers, error messages, tool exit codes.*

### 5.1 [Issue Title]

| Field | Value |
|-------|-------|
| Severity | CRITICAL / HIGH / MEDIUM / LOW |
| First observed | [timestamp] |
| Duration | [time to resolve] |
| Impact | [what was blocked or degraded] |

- **Symptom:** [What was observed — error messages, wrong outputs, hung processes]
- **Root Cause (5 Whys):**
  1. Why? → [immediate cause]
  2. Why? → [underlying cause]
  3. Why? → [process gap]
  4. Why? → [systemic gap]
  5. Why? → [root cause]
- **Fix Applied:** [What was done to resolve it]
- **Was this fix propagated?** [To skill? To script? To template? To memory?]

### 5.2 [Next Issue]

...

---

## 6. Where We Got Lucky

*Things that COULD have gone wrong but didn't — narrow escapes, unverified assumptions that happened to hold, tooling that almost failed. This section prevents survivor bias.*

- **Near-miss:** [Description]
  - **Why it didn't escalate:** [Reason]
  - **What would have happened if it did:** [Worst-case impact]
  - **Preventive action:** [What to change so luck isn't needed next time]

---

## 7. Metrics & Data

*Quantitative evidence. Every number must be traceable to a source file.*

| Metric | This Stage | Previous Iteration | Delta | Source |
|--------|-----------|-------------------|-------|--------|
| Duration (min) | | | | |
| API calls | | | | |
| Token cost (USD) | | | | |
| Errors encountered | | | | |
| Fix iterations | | | | |
| Scope changes | | | | |
| Skills updated | | | | |
| Scripts modified | | | | |

---

## 8. Agent Performance Review

*Per-agent assessment. Only include agents that participated in this stage.*

| Agent | Role | Autonomy Score (1-5) | Hallucinations | Escalations | Notes |
|-------|------|---------------------|----------------|-------------|-------|
| | | | | | |

**Autonomy Scale:**
- 1 = Required human intervention for every step
- 2 = Needed frequent correction or re-prompting
- 3 = Completed with minor nudges
- 4 = Fully autonomous, one or two clarifications
- 5 = Fully autonomous, zero intervention, proactive quality checks

---

## 9. Hallucination Incidents

*If applicable. Tag using Liu et al. (2026, IEEE TSE) taxonomy from SOUL.md §Anti-Hallucination Guardrail Taxonomy.*

| Incident | Agent | Category | Sub-Category | Diagnostic Code | Resolution |
|----------|-------|----------|--------------|-----------------|------------|
| | | | | | |

---

## 10. Lessons Learned

*Actionable, forward-facing takeaways. Each lesson must be specific enough that a future agent (or future you) can act on it without additional context.*

| # | Lesson | Category | Applies To | Priority |
|---|--------|----------|------------|----------|
| 1 | | SKILL / SCRIPT / TEMPLATE / FLOW / TOOL | [which stages] | P0-P3 |

---

## 11. Action Items

*Concrete, assigned, trackable. Every action item must have an owner and a verification criterion.*

| # | Action | Owner | Deadline | Verification | Status |
|---|--------|-------|----------|--------------|--------|
| 1 | | | | | OPEN |

---

## 12. Preventive Measures

*Systemic changes that prevent this class of failure from recurring — across ALL future projects, not just this one.*

| # | Measure | Type | Affected Skill/Script | Implementation Scope |
|---|---------|------|----------------------|---------------------|
| 1 | | SKILL_UPDATE / SCRIPT_UPDATE / NEW_TEMPLATE / FLOW_CHANGE / MEMORY | | |

---

## 13. Flow Improvement Proposals

*If this stage revealed something that should change the overall Vera framework workflow pipeline itself.*

| Proposal | Current Behavior | Proposed Behavior | Rationale | Risk |
|----------|-----------------|-------------------|-----------|------|
| | | | | |

---

## 14. Sign-off

| Role | Name / Agent | Date | Signature |
|------|-------------|------|-----------|
| Auditor | Claude Code Opus 4.8 | | |
| Reviewed by | Vera (Orchestrator) | | |
| Accepted by | [User] | | |

---

*Template version: 2.0 | Created: 2026-07-16 | Updated: 2026-07-16 — v6a path conventions (underscores, 00_ validation, 11_ postmortem) | For Vera ASIC Workflow Framework*
