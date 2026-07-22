#!/usr/bin/env bash
# verify_promotion_artifacts.sh — Mechanical gate for module-promotion stage.
#
# Usage: verify_promotion_artifacts.sh <stage_dir>
#
# Checks:
#   1. Every promoted module has a promotion_report.json
#   2. Every promotion_report.json has non-null cell_count
#   3. Every module has a reuse_manifest.json (F-06)
#   4. Every synthesis_log referenced in promotion reports exists on disk (F-07)
#   5. Parent cell_count >= max child cell_count (F-97)
#   6. results.xml exists for all verification testbenches (F-22)
#
# Exit 0 = all checks pass. Exit 1 = failures found.
#
# Implements improvement plan §2.5, §2.6 (IP-010 v2 postmortem F-06, F-07, F-73, F-78, F-97).

set -euo pipefail

STAGE_DIR="${1:-}"
if [ -z "$STAGE_DIR" ] || [ ! -d "$STAGE_DIR" ]; then
    echo "USAGE: verify_promotion_artifacts.sh <stage_dir>"
    echo "  stage_dir — path to 07_promote_stage/"
    exit 1
fi

FAILS=0
fail() { echo "  ⛔ $*"; FAILS=$((FAILS+1)); }
pass() { echo "  ✅ $*"; }

echo "=== verify_promotion_artifacts: $STAGE_DIR ==="
echo ""

# Source evidence-assertions if available
EVIDENCE_LIB="$HOME/.hermes/skills/asic-workflow/evidence-assertions/scripts/evidence-assertions.sh"
if [ -f "$EVIDENCE_LIB" ]; then
    source "$EVIDENCE_LIB"
fi

# ─────────────────────────────────────────────
# CHECK 1: promotion_report.json exists per module
# ─────────────────────────────────────────────
echo "--- Promotion reports ---"
REPORTS=$(find "$STAGE_DIR" -name "promotion_report.json" -type f 2>/dev/null)
# find | wc -l, not a round-trip through grep -c . on a possibly-empty variable
# (the prior form was accidentally correct on empty input but fragile).
REPORT_COUNT=$(find "$STAGE_DIR" -name "promotion_report.json" -type f 2>/dev/null | wc -l)

if [ "$REPORT_COUNT" -eq 0 ]; then
    fail "No promotion_report.json found in $STAGE_DIR"
else
    pass "$REPORT_COUNT promotion_report.json found"
fi

# ─────────────────────────────────────────────
# CHECK 2: Non-null cell_count in each report
# ─────────────────────────────────────────────
echo ""
echo "--- Cell count validation ---"
NULL_COUNT=0
while IFS= read -r report; do
    [ -z "$report" ] && continue
    CC=$(python3 -c "import json; print(json.load(open('$report')).get('cell_count', 'MISSING'))" 2>/dev/null || echo "PARSE_ERROR")
    MOD=$(python3 -c "import json; print(json.load(open('$report')).get('module', 'unknown'))" 2>/dev/null || echo "unknown")
    if [ "$CC" = "None" ] || [ "$CC" = "MISSING" ] || [ "$CC" = "PARSE_ERROR" ]; then
        fail "$MOD: cell_count is $CC (must be non-null)"
        NULL_COUNT=$((NULL_COUNT+1))
    elif [ "$CC" = "0" ]; then
        # cell_count=0 is suspicious — check if there's a synth log
        SYNTH=$(python3 -c "import json; print(json.load(open('$report')).get('synthesis_log', ''))" 2>/dev/null || echo "")
        if [ -n "$SYNTH" ] && [ -f "$SYNTH" ]; then
            # Synth log exists but cell_count is 0 — could be a blackbox
            echo "  ⚠️  $MOD: cell_count=0 with synth log — verify this is a blackbox"
        else
            fail "$MOD: cell_count=0 with no synthesis_log"
        fi
    else
        pass "$MOD: cell_count=$CC"
    fi
done <<< "$REPORTS"

# ─────────────────────────────────────────────
# CHECK 3: reuse_manifest.json per module (F-06)
# ─────────────────────────────────────────────
echo ""
echo "--- Reuse manifests ---"
REUSE_COUNT=$(find "$STAGE_DIR" -name "reuse_manifest.json" -type f 2>/dev/null | wc -l)
if [ "$REUSE_COUNT" -eq 0 ]; then
    fail "No reuse_manifest.json found (0/$REPORT_COUNT) — F-06"
elif [ "$REUSE_COUNT" -lt "$REPORT_COUNT" ]; then
    fail "Only $REUSE_COUNT/$REPORT_COUNT reuse_manifest.json — F-06"
else
    pass "$REUSE_COUNT/$REPORT_COUNT reuse_manifest.json"
fi

# ─────────────────────────────────────────────
# CHECK 4: synthesis_log exists on disk (F-07)
# ─────────────────────────────────────────────
echo ""
echo "--- Synthesis log provenance ---"
MISSING_SYNTH=0
while IFS= read -r report; do
    [ -z "$report" ] && continue
    SYNTH=$(python3 -c "import json; print(json.load(open('$report')).get('synthesis_log', ''))" 2>/dev/null || echo "")
    MOD=$(python3 -c "import json; print(json.load(open('$report')).get('module', 'unknown'))" 2>/dev/null || echo "unknown")
    if [ -z "$SYNTH" ]; then
        fail "$MOD: no synthesis_log field in promotion report — F-07"
        MISSING_SYNTH=$((MISSING_SYNTH+1))
    elif [ ! -f "$SYNTH" ]; then
        fail "$MOD: synthesis_log '$SYNTH' does not exist on disk — F-07"
        MISSING_SYNTH=$((MISSING_SYNTH+1))
    else
        pass "$MOD: synthesis_log exists"
    fi
done <<< "$REPORTS"

# ─────────────────────────────────────────────
# CHECK 5: Hierarchical cell count sanity (F-97)
# ─────────────────────────────────────────────
echo ""
echo "--- Hierarchical cell count sanity ---"
# Find the SoC/top module report and check its cell_count >= children.
# The top module comes from blueprint.json's declared top, never from a substring
# match on the module name — a grep for "top"/"soc" also matches soc_bridge or
# topology_ctrl (same class of defect as §G.15: a name is not an identity).
BLUEPRINT_TOP="$(dirname "$STAGE_DIR")/03_architecture_stage/blueprint.json"
TOP_MODULE=""
if [ -f "$BLUEPRINT_TOP" ]; then
    TOP_MODULE=$(python3 -c "import json; print(json.load(open('$BLUEPRINT_TOP')).get('top_module',''))" 2>/dev/null || echo "")
fi
if [ -n "$TOP_MODULE" ]; then
    SOC_REPORT=$(find "$STAGE_DIR" -name "promotion_report.json" -type f -exec grep -l "\"module\"[[:space:]]*:[[:space:]]*\"$TOP_MODULE\"" {} \; 2>/dev/null | head -1)
else
    echo "  ⚠️  No blueprint.json top_module — falling back to substring match (unreliable)"
    SOC_REPORT=$(find "$STAGE_DIR" -name "promotion_report.json" -type f -exec grep -l '"module".*soc\|"module".*top\|"module".*_soc' {} \; 2>/dev/null | head -1)
fi
if [ -n "$SOC_REPORT" ]; then
    SOC_CC=$(python3 -c "import json; print(json.load(open('$SOC_REPORT')).get('cell_count', 0))" 2>/dev/null || echo "0")
    SOC_MOD=$(python3 -c "import json; print(json.load(open('$SOC_REPORT')).get('module', 'unknown'))" 2>/dev/null || echo "unknown")
    
    MAX_CHILD_CC=0
    MAX_CHILD_MOD=""
    while IFS= read -r report; do
        [ -z "$report" ] && continue
        [ "$report" = "$SOC_REPORT" ] && continue
        CC=$(python3 -c "import json; print(json.load(open('$report')).get('cell_count', 0))" 2>/dev/null || echo "0")
        MOD=$(python3 -c "import json; print(json.load(open('$report')).get('module', 'unknown'))" 2>/dev/null || echo "unknown")
        if [ "$CC" -gt "$MAX_CHILD_CC" ] 2>/dev/null; then
            MAX_CHILD_CC="$CC"
            MAX_CHILD_MOD="$MOD"
        fi
    done <<< "$REPORTS"
    
    if [ "$MAX_CHILD_CC" -gt 0 ] && [ "$SOC_CC" -lt "$MAX_CHILD_CC" ] 2>/dev/null; then
        fail "$SOC_MOD ($SOC_CC cells) < $MAX_CHILD_MOD ($MAX_CHILD_CC cells) — parent cannot contain fewer cells than child — F-97"
    elif [ "$MAX_CHILD_CC" -gt 0 ]; then
        pass "$SOC_MOD ($SOC_CC cells) >= $MAX_CHILD_MOD ($MAX_CHILD_CC cells)"
    fi
else
    echo "  ⚠️  No SoC/top module report found — skipping hierarchical check"
fi

# ─────────────────────────────────────────────
# CHECK 6: Verification results.xml (F-22)
# ─────────────────────────────────────────────
echo ""
echo "--- Verification results ---"
VERIFY_DIR="$(dirname "$STAGE_DIR")/06_verification_stage"
if [ -d "$VERIFY_DIR" ]; then
    # A count without a denominator is not a check. IP-010 v3 printed
    # "✅ 15 results.xml found" beside 17 promoted modules and passed.
    RESULTS_XML=$(find "$VERIFY_DIR" ( -path "*/tb_*/results.xml" -o -path "*/tb-*/results.xml" ) -type f 2>/dev/null | wc -l)
    PROMOTED=$(python3 -c "import json;print(json.load(open('$STAGE_DIR/promotion_summary.json'))['modules_promoted'])" 2>/dev/null || echo "$REPORT_COUNT")
    if [ "$RESULTS_XML" -eq 0 ]; then
        fail "No results.xml found in $VERIFY_DIR/tb_*/ — F-22"
    elif [ "$RESULTS_XML" -lt "$PROMOTED" ]; then
        fail "$RESULTS_XML results.xml for $PROMOTED promoted modules — $((PROMOTED-RESULTS_XML)) module(s) promoted with NO verification evidence"
        # Name them. A count tells you something is wrong; a set tells you what.
        comm -13 \
          <(find "$VERIFY_DIR" ( -path "*/tb_*/results.xml" -o -path "*/tb-*/results.xml" ) -printf '%h\n' | xargs -n1 basename | sed 's/^tb_//' | sort) \
          <(python3 -c "import json;[print(m) for m in json.load(open('$STAGE_DIR/promotion_summary.json'))['promoted_modules']]" 2>/dev/null | sort) \
          | sed 's/^/       UNVERIFIED: /'
    else
        pass "$RESULTS_XML/$PROMOTED results.xml — every promoted module has verification evidence"
    fi
else
    echo "  ⚠️  No verification stage directory found — skipping"
fi

# ─────────────────────────────────────────────
# Final verdict
# ─────────────────────────────────────────────
echo ""
if [ "$FAILS" -gt 0 ]; then
    echo "⛔ verify_promotion_artifacts: $FAILS FAILURE(S). Stage is BLOCKED."
    exit 1
else
    echo "✅ verify_promotion_artifacts: ALL CHECKS PASSED."
    exit 0
fi
