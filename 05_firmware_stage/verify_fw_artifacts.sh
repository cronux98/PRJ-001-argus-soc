#!/usr/bin/env bash
# verify_fw_artifacts.sh — Stage 05 firmware exit gate (§3.15)
# Enforces:
#   1. fw_build.log exists with --version output
#   2. bsp_manifest.json has per-file provenance
#   3. bootrom_report.json confirms ROM budget not exceeded
#   4. Every fw/drivers/<periph>/results.xml exists and has >= 1 <testcase>
#   5. tb-fw-bringup/results.xml exists
#
# Usage: bash verify_fw_artifacts.sh [stage_dir]
# Default: current directory

set -euo pipefail

STAGE_DIR="${1:-$(pwd)}"
FAILURES=0
CHECKS=0

pass() { echo "  PASS: $1"; CHECKS=$((CHECKS+1)); }
fail() { echo "  FAIL: $1"; FAILURES=$((FAILURES+1)); CHECKS=$((CHECKS+1)); }

echo "=== verify_fw_artifacts.sh — Stage 05 exit gate ==="
echo "Stage dir: $STAGE_DIR"
echo ""

# ── Check 1: fw_build.log ───────────────────────────────────
if [ -f "$STAGE_DIR/fw_build.log" ]; then
    if grep -q "riscv32-unknown-elf-gcc.*14\.2" "$STAGE_DIR/fw_build.log" 2>/dev/null; then
        pass "fw_build.log exists with compiler version"
    else
        fail "fw_build.log exists but missing --version output"
    fi
else
    fail "fw_build.log NOT FOUND"
fi

# ── Check 2: bsp_manifest.json ──────────────────────────────
if [ -f "$STAGE_DIR/bsp/bsp_manifest.json" ]; then
    if grep -q "GENERATED-FROM" "$STAGE_DIR/bsp/bsp_manifest.json" 2>/dev/null; then
        pass "bsp_manifest.json exists with provenance"
    else
        fail "bsp_manifest.json exists but lacks GENERATED-FROM banner"
    fi
else
    fail "bsp/bsp_manifest.json NOT FOUND"
fi

# ── Check 3: bootrom_report.json ────────────────────────────
if [ -f "$STAGE_DIR/bootrom/bootrom_report.json" ]; then
    if grep -q '"verdict".*"PASS"' "$STAGE_DIR/bootrom/bootrom_report.json" 2>/dev/null; then
        pass "bootrom_report.json exists, budget PASS"
    else
        fail "bootrom_report.json exists but budget FAIL or missing verdict"
    fi
else
    fail "bootrom/bootrom_report.json NOT FOUND"
fi

# ── Check 4: Driver results.xml ─────────────────────────────
for drv_dir in "$STAGE_DIR"/fw/drivers/*/; do
    periph=$(basename "$drv_dir")
    results="$drv_dir/results.xml"
    if [ -f "$results" ]; then
        if grep -q '<testcase' "$results" 2>/dev/null; then
            pass "results.xml for '$periph' has >= 1 testcase"
        else
            fail "results.xml for '$periph' has NO testcase entries"
        fi
    else
        fail "results.xml for '$periph' NOT FOUND"
    fi
done

# ── Check 5: Bring-up results ───────────────────────────────
if [ -f "$STAGE_DIR/tb-fw-bringup/results.xml" ]; then
    pass "tb-fw-bringup/results.xml exists"
else
    fail "tb-fw-bringup/results.xml NOT FOUND"
fi

# ── Check 6: bootrom.hex ────────────────────────────────────
if [ -f "$STAGE_DIR/bootrom/bootrom.hex" ]; then
    if grep -q '^:' "$STAGE_DIR/bootrom/bootrom.hex" 2>/dev/null; then
        pass "bootrom/bootrom.hex exists (valid Intel HEX)"
    else
        fail "bootrom/bootrom.hex exists but not valid Intel HEX"
    fi
else
    fail "bootrom/bootrom.hex NOT FOUND"
fi

# ── Verdict ─────────────────────────────────────────────────
echo ""
echo "=== Verdict ==="
echo "Checks: $CHECKS passed: $((CHECKS-FAILURES)) failed: $FAILURES"
if [ "$FAILURES" -eq 0 ]; then
    echo "RESULT: PASS"
    exit 0
else
    echo "RESULT: FAIL — $FAILURES check(s) failed"
    exit 1
fi
