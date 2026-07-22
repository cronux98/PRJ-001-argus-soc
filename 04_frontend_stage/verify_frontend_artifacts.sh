#!/usr/bin/env bash
# verify_frontend_artifacts.sh — Frontend artifact gate
# Run from 04_frontend_stage/ directory
# Sources evidence-assertions.sh for assert_files, assert_clean, assert_exists
#
# Generated for PRJ-001 v0 audit fix (check 3.9/3.16)
# GENERATED-FROM: hermes rtl-flow-agent verify_frontend_artifacts.sh $(date -Iseconds)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE_LIB="/home/smdadmin/.hermes/skills/asic-workflow/evidence-assertions/scripts/evidence-assertions.sh"

if [ ! -f "$EVIDENCE_LIB" ]; then
    echo "FATAL: evidence-assertions.sh not found at $EVIDENCE_LIB"
    exit 1
fi
source "$EVIDENCE_LIB"

STAGE_DIR="${1:-$SCRIPT_DIR}"
cd "$STAGE_DIR" || { echo "FATAL: cannot cd to $STAGE_DIR"; exit 1; }

PASS_COUNT=0
FAIL_COUNT=0
MODULES=(uart spi_master i2c_master gpio pwm sys_ctrl interrupt_ctrl apb_interconnect wb_bridge ibex_core sram argus_soc)

echo "=== verify_frontend_artifacts.sh ==="
echo "Stage dir: $STAGE_DIR"
echo "Timestamp: $(date -Iseconds)"
echo ""

# ── CHECK 1: Lint logs (12 modules, 0 fatal errors) ──
echo "── Check 1: Lint logs (12 modules) ──"
LINT_FAILS=0
for m in "${MODULES[@]}"; do
    LOG="rtl-${m}/logs/lint/${m}_verilator.log"
    if ! assert_exists "$LOG" "lint-log-${m}"; then
        ((LINT_FAILS++))
        continue
    fi
    # Count %Error- lines (excluding "Exiting due to")
    err_count=$(grep -c '%Error-' "$LOG" 2>/dev/null || true)
    exit_line=$(grep -c '%Error: Exiting due to' "$LOG" 2>/dev/null || true)
    fatal_count=$((err_count - exit_line))
    if [ "$fatal_count" -gt 0 ]; then
        echo "FAIL lint-clean-${m}: $fatal_count fatal errors in $LOG"
        ((LINT_FAILS++))
    else
        echo "PASS lint-clean-${m}: 0 fatal errors"
    fi
done
if [ "$LINT_FAILS" -eq 0 ]; then
    echo "PASS check-1: all 12 lint logs present and clean"
    ((PASS_COUNT++))
else
    echo "FAIL check-1: $LINT_FAILS lint failures"
    ((FAIL_COUNT++))
fi
echo ""

# ── CHECK 2: Formal results (12 modules, results.xml) ──
echo "── Check 2: Formal results (12 modules) ──"
FORMAL_FAILS=0
for m in "${MODULES[@]}"; do
    XML="rtl-${m}/logs/formal/results.xml"
    LOG="rtl-${m}/logs/formal/${m}_sby.log"
    if [ -f "$XML" ]; then
        echo "PASS formal-xml-${m}: results.xml exists"
    elif [ -f "$LOG" ] && grep -q "DONE (PASS" "$LOG" 2>/dev/null; then
        echo "PASS formal-${m}: sby log shows PASS (no xml, but log ok)"
    elif [ -f "$LOG" ]; then
        echo "FAIL formal-${m}: sby log exists but no PASS"
        ((FORMAL_FAILS++))
    else
        echo "FAIL formal-${m}: no results.xml, no sby log"
        ((FORMAL_FAILS++))
    fi
done
if [ "$FORMAL_FAILS" -eq 0 ]; then
    echo "PASS check-2: all 12 formal results present"
    ((PASS_COUNT++))
else
    echo "FAIL check-2: $FORMAL_FAILS formal failures"
    ((FAIL_COUNT++))
fi
echo ""

# ── CHECK 3: Synth logs (12 modules, 0 errors) ──
echo "── Check 3: Synth logs (12 modules) ──"
SYNTH_FAILS=0
for m in "${MODULES[@]}"; do
    LOG="rtl-${m}/logs/synth/${m}_synth.log"
    if ! assert_exists "$LOG" "synth-log-${m}"; then
        ((SYNTH_FAILS++))
        continue
    fi
    # Check for ABC errors
    if grep -qE 'ABC: ERROR|ERROR: ABC' "$LOG" 2>/dev/null; then
        echo "FAIL synth-${m}: ABC errors in $LOG"
        ((SYNTH_FAILS++))
    else
        echo "PASS synth-${m}: synth log present, no ABC errors"
    fi
done
if [ "$SYNTH_FAILS" -eq 0 ]; then
    echo "PASS check-3: all 12 synth logs present and clean"
    ((PASS_COUNT++))
else
    echo "FAIL check-3: $SYNTH_FAILS synth failures"
    ((FAIL_COUNT++))
fi
echo ""

# ── CHECK 4: Netlists (12 modules) ──
echo "── Check 4: Netlists (12 modules) ──"
NETLIST_FAILS=0
for m in "${MODULES[@]}"; do
    NL="rtl-${m}/synth/${m}_netlist.v"
    if assert_exists "$NL" "netlist-${m}"; then
        echo "PASS netlist-${m}: netlist exists"
    else
        ((NETLIST_FAILS++))
    fi
done
if [ "$NETLIST_FAILS" -eq 0 ]; then
    echo "PASS check-4: all 12 netlists present"
    ((PASS_COUNT++))
else
    echo "FAIL check-4: $NETLIST_FAILS netlist missing"
    ((FAIL_COUNT++))
fi
echo ""

# ── CHECK 5: Equiv logs (12 modules) ──
echo "── Check 5: Equiv logs (12 modules) ──"
EQUIV_FAILS=0
for m in "${MODULES[@]}"; do
    LOG="rtl-${m}/logs/equiv_check/${m}_equiv.log"
    if [ -f "$LOG" ] && grep -q "Equivalence successfully proven" "$LOG" 2>/dev/null; then
        echo "PASS equiv-${m}: equivalence proven"
    elif [ -f "$LOG" ]; then
        echo "FAIL equiv-${m}: log exists but equivalence not proven"
        ((EQUIV_FAILS++))
    else
        echo "PENDING equiv-${m}: equiv not yet run"
        ((EQUIV_FAILS++))
    fi
done
if [ "$EQUIV_FAILS" -eq 0 ]; then
    echo "PASS check-5: all 12 equiv proven"
    ((PASS_COUNT++))
else
    echo "FAIL check-5: $EQUIV_FAILS equiv pending/failed"
    ((FAIL_COUNT++))
fi
echo ""

# ── CHECK 6: GENERATED-FROM banners ──
echo "── Check 6: GENERATED-FROM banners ──"
BANNER_FAILS=0
for m in "${MODULES[@]}"; do
    LOG="rtl-${m}/logs/lint/${m}_verilator.log"
    if [ -f "$LOG" ]; then
        if head -1 "$LOG" | grep -q "GENERATED-FROM:"; then
            echo "PASS banner-lint-${m}: banner present"
        else
            echo "FAIL banner-lint-${m}: no GENERATED-FROM banner"
            ((BANNER_FAILS++))
        fi
    fi
done
if [ "$BANNER_FAILS" -eq 0 ]; then
    echo "PASS check-6: all lint logs have GENERATED-FROM banners"
    ((PASS_COUNT++))
else
    echo "FAIL check-6: $BANNER_FAILS logs missing banners"
    ((FAIL_COUNT++))
fi
echo ""

# ── SUMMARY ──
echo "========================================="
echo "VERDICT: $PASS_COUNT checks PASS, $FAIL_COUNT checks FAIL"
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "GATE: PASS — all frontend artifacts verified"
    exit 0
else
    echo "GATE: FAIL — $FAIL_COUNT check(s) failed"
    exit 1
fi
