#!/bin/bash
# run_determinism.sh — Run golden model N times with different seeds
# and verify deterministic output (excluding metadata fields).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
N=${1:-3}
SEEDS=(42 123 999 7777 54321)

echo "=== PRJ-001 Argus Golden Model Determinism Check (N=$N) ==="
echo ""

declare -a HASHES
declare -a FILES

for i in $(seq 0 $((N - 1))); do
    seed="${SEEDS[$i]}"
    out="golden_out_seed${seed}.json"
    FILES+=("$out")
    echo "[$((i+1))/$N] Running with --seed $seed ..."
    python3 "$SCRIPT_DIR/golden_model.py" --seed "$seed" --out "$SCRIPT_DIR/$out" > /dev/null 2>&1
    # Extract MD5 of tests array only (strip _metadata)
    h=$(python3 -c "
import json
with open('$SCRIPT_DIR/$out') as f:
    data = json.load(f)
# Compute MD5 of tests array only, excluding _metadata
import hashlib
tests_json = json.dumps(data['tests'], sort_keys=True)
print(hashlib.md5(tests_json.encode()).hexdigest())
")
    HASHES+=("$h")
    echo "       Tests MD5: $h  ($out)"
done

echo ""
echo "--- Hash Comparison ---"
FIRST="${HASHES[0]}"
IDENTICAL=true
for i in $(seq 0 $((N - 1))); do
    seed="${SEEDS[$i]}"
    h="${HASHES[$i]}"
    if [ "$h" != "$FIRST" ]; then
        echo "  MISMATCH: seed $seed hash $h != $FIRST"
        IDENTICAL=false
    fi
done

if $IDENTICAL; then
    echo "  ALL IDENTICAL: $N/$N runs produce same tests MD5 ($FIRST)"
else
    echo "  FAIL: hashes differ between runs"
fi

# Write determinism.json
python3 -c "
import json, hashlib, os
hashes = $(python3 -c "import json; print(json.dumps(${HASHES[@]@Q}))" 2>/dev/null || echo '[]')
runs = []
seeds_list = [${SEEDS[0]}, ${SEEDS[1]}, ${SEEDS[2]}, ${SEEDS[3]}, ${SEEDS[4]}]
for i in range($N):
    runs.append({'seed': seeds_list[i], 'file': '${FILES[$i]}', 'tests_md5': hashes[i] if i < len(hashes) else 'unknown'})

result = {
    'project': 'PRJ-001',
    'codename': 'Argus',
    'identical': $IDENTICAL,
    'first_hash': '$FIRST',
    'n_runs': $N,
    'runs': runs,
    'method': 'MD5 of sorted tests JSON array (excluding _metadata)',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}
with open('$SCRIPT_DIR/determinism.json', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"

echo ""
echo "Wrote determinism.json"
exit 0
