#!/bin/bash
# verify_test_artifacts.sh — Verification Stage exit gate for PRJ-001
# Checks that all required verification artifacts exist.
# Exit 0 = PASS, Exit 1 = FAIL

set -euo pipefail

STAGE_DIR="$(cd "$(dirname "$0")" && pwd)"
FAILS=0

echo "=== PRJ-001 Verification Stage: verify_test_artifacts.sh ==="
echo "Stage dir: $STAGE_DIR"
echo ""

MODULES=(sys_ctrl interrupt_ctrl uart gpio spi_master i2c_master pwm sram wb_bridge apb_interconnect ibex_core argus_soc)

# Check 1: results.xml for every module
echo "--- Check 1: results.xml per module ---"
for mod in "${MODULES[@]}"; do
    if [ -f "$STAGE_DIR/tb-$mod/results.xml" ]; then
        tests=$(grep -o 'tests="[0-9]*"' "$STAGE_DIR/tb-$mod/results.xml" | head -1 | grep -o '[0-9]*' || echo "0")
        fails=$(grep -o 'failures="[0-9]*"' "$STAGE_DIR/tb-$mod/results.xml" | head -1 | grep -o '[0-9]*' || echo "0")
        echo "  [PASS] $mod: results.xml ($tests tests, $fails failures)"
    else
        echo "  [FAIL] $mod: results.xml NOT FOUND"
        FAILS=$((FAILS + 1))
    fi
done

# Check 2: tier_assignment.json
echo ""
echo "--- Check 2: tier_assignment.json ---"
if [ -f "$STAGE_DIR/coverage/tier_assignment.json" ]; then
    echo "  [PASS] coverage/tier_assignment.json exists"
else
    echo "  [FAIL] coverage/tier_assignment.json NOT FOUND"
    FAILS=$((FAILS + 1))
fi

# Check 3: verification_summary.json
echo ""
echo "--- Check 3: verification_summary.json ---"
if [ -f "$STAGE_DIR/results/verification_summary.json" ]; then
    echo "  [PASS] results/verification_summary.json exists"
    # Verify it has GENERATED-FROM provenance
    if grep -q "GENERATED-FROM" "$STAGE_DIR/results/verification_summary.json"; then
        echo "  [PASS] verification_summary.json has GENERATED-FROM banner"
    else
        echo "  [FAIL] verification_summary.json missing GENERATED-FROM provenance"
        FAILS=$((FAILS + 1))
    fi
else
    echo "  [FAIL] results/verification_summary.json NOT FOUND"
    FAILS=$((FAILS + 1))
fi

# Check 4: failure_clusters.txt
echo ""
echo "--- Check 4: failure_clusters.txt ---"
if [ -f "$STAGE_DIR/failure_clusters.txt" ]; then
    echo "  [PASS] failure_clusters.txt exists"
    if grep -q "SIGNATURE TABLE" "$STAGE_DIR/failure_clusters.txt"; then
        echo "  [PASS] failure_clusters.txt has SIGNATURE TABLE"
    else
        echo "  [FAIL] failure_clusters.txt missing SIGNATURE TABLE"
        FAILS=$((FAILS + 1))
    fi
else
    echo "  [FAIL] failure_clusters.txt NOT FOUND"
    FAILS=$((FAILS + 1))
fi

# Check 5: All 12 modules have results.xml
echo ""
echo "--- Check 5: Module count ---"
MOD_COUNT=$(ls -1 "$STAGE_DIR"/tb-*/results.xml 2>/dev/null | wc -l)
if [ "$MOD_COUNT" -eq 12 ]; then
    echo "  [PASS] 12/12 modules have results.xml"
else
    echo "  [FAIL] Only $MOD_COUNT/12 modules have results.xml"
    FAILS=$((FAILS + 1))
fi

# Summary
echo ""
echo "========================================"
if [ "$FAILS" -eq 0 ]; then
    echo "VERDICT: PASS — All verification artifacts present"
    exit 0
else
    echo "VERDICT: FAIL — $FAILS check(s) failed"
    exit 1
fi
