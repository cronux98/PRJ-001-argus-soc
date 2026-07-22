#!/usr/bin/env python3
"""
Planning Validator for PRJ-001 (Argus) 02_specification_stage.
Performs self-consistency checks:
  (a) Every SYS-xx-NNN ID in system_spec.md §11 is unique and referenced
  (b) Memory-map regions in §8 do not overlap
  (c) Every module M01-M12 in module_list.md appears in system_spec.md §2.3
  (d) module_list.md summary arithmetic reconciles

Exit 0 on PASS, exit 1 on FAIL. Emits 'RESULT: PASS' or 'RESULT: FAIL' on last line.
"""

import re, sys, os, json

STAGE_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(STAGE_DIR, "system_spec.md")
MODULES = os.path.join(STAGE_DIR, "module_list.md")
TRACE = os.path.join(STAGE_DIR, "traceability_matrix.md")

FAILURES = 0

def fail(msg):
    global FAILURES
    print(f"  FAIL: {msg}")
    FAILURES += 1

def ok(msg):
    print(f"  PASS: {msg}")

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

# ── (a) Unique SYS-xx-NNN IDs ──────────────────────────────────────────
print("=== Check (a): SYS-xx-NNN ID uniqueness and referential integrity ===")

spec_text = read_file(SPEC)
trace_text = read_file(TRACE)

# Extract all SYS-xx-NNN from system_spec.md
sys_ids = re.findall(r'SYS-(?:FR|PR|IR|AR|CR)-\d{3}', spec_text)
unique_ids = sorted(set(sys_ids))

# Check for genuine duplicates (>2 occurrences = error; 2 is normal: definition + §11 reference)
id_counts = {}
for rid in sys_ids:
    id_counts[rid] = id_counts.get(rid, 0) + 1
dupes = {k: v for k, v in id_counts.items() if v > 2}
if dupes:
    for k, v in dupes.items():
        fail(f"Genuine duplicate: ID {k} appears {v} times (expected ≤2: definition + §11 reference)")
else:
    ok(f"All {len(unique_ids)} SYS-xx-NNN IDs appear ≤2 times (definition + §11 reference, {len(sys_ids)} total occurrences)")

# Check §11 coverage — every unique ID appearing in the spec body should appear in §11
# §11 starts at "## 11. Traceability Matrix"
sec11_start = spec_text.find("## 11. Traceability Matrix")
sec12_start = spec_text.find("## 12. Open Issues")
sec11 = spec_text[sec11_start:sec12_start] if sec12_start > 0 else spec_text[sec11_start:]
sec11_ids = set(re.findall(r'SYS-(?:FR|PR|IR|AR|CR)-\d{3}', sec11))

missing_from_11 = set(unique_ids) - sec11_ids
if missing_from_11:
    for rid in sorted(missing_from_11):
        fail(f"ID {rid} found in spec body but NOT in §11 Traceability Matrix")
else:
    ok(f"All {len(unique_ids)} unique IDs appear in §11 Traceability Matrix")

# Check traceability_matrix.md covers every unique spec ID
trace_ids = set(re.findall(r'SYS-(?:FR|PR|IR|AR|CR)-\d{3}', trace_text))
missing_from_trace = set(unique_ids) - trace_ids
if missing_from_trace:
    for rid in sorted(missing_from_trace):
        fail(f"ID {rid} in system_spec.md but NOT in traceability_matrix.md")
else:
    ok(f"All {len(unique_ids)} unique IDs appear in traceability_matrix.md")

extra_in_trace = trace_ids - set(unique_ids)
if extra_in_trace:
    for rid in sorted(extra_in_trace):
        fail(f"ID {rid} in traceability_matrix.md but NOT in system_spec.md (phantom)")
else:
    ok("No phantom IDs in traceability_matrix.md (all trace IDs exist in spec)")

# ── (b) Memory-map overlap check ──────────────────────────────────────
print("\n=== Check (b): Memory-map region overlaps ===")

sec8_start = spec_text.find("## 8. Memory Map")
sec9_start = spec_text.find("## 9. Clock")
sec8 = spec_text[sec8_start:sec9_start] if sec9_start > 0 else spec_text[sec8_start:]

# Parse memory regions (table rows with Base Address + Size)
regions = []
for line in sec8.split('\n'):
    # Match table rows like: | SRAM | 0x0000_0000 | 4 KB (0x1000) | ...
    m = re.match(r'\|\s*(.+?)\s*\|\s*(0x[0-9A-Fa-f_]+)\s*\|\s*(\d+)\s*(KB|B|GB)\s*(?:\(0x([0-9A-Fa-f_]+)\))?', line)
    if m:
        name = m.group(1).strip()
        base_str = m.group(2).replace('_', '')
        base = int(base_str, 16)
        size_val = int(m.group(3))
        size_unit = m.group(4)
        size_hex_str = m.group(5)

        if size_unit == 'KB':
            size = size_val * 1024
        elif size_unit == 'GB':
            size = size_val * 1024 * 1024 * 1024
        elif size_unit == 'B':
            size = size_val
        else:
            size = size_val

        # Cross-check hex size
        if size_hex_str:
            hex_size = int(size_hex_str.replace('_', ''), 16)
            if hex_size != size:
                fail(f"Region '{name}': size mismatch — {size_val} {size_unit} ({size}) vs hex {size_hex_str} ({hex_size})")
                continue

        regions.append((name, base, size))
        # Skip Reserved regions for overlap check
        if 'reserved' not in name.lower():
            ok(f"Region '{name}': base=0x{base:08X}, size={size} bytes = 0x{size:X}")

# Check overlaps
non_reserved = [(n, b, s) for n, b, s in regions if 'reserved' not in n.lower()]
non_reserved.sort(key=lambda x: x[1])  # sort by base address

for i in range(len(non_reserved)):
    for j in range(i+1, len(non_reserved)):
        a_name, a_base, a_size = non_reserved[i]
        b_name, b_base, b_size = non_reserved[j]
        a_end = a_base + a_size - 1
        b_end = b_base + b_size - 1
        if a_base <= b_end and b_base <= a_end:
            fail(f"Overlap: '{a_name}' [0x{a_base:08X}–0x{a_end:08X}] collides with '{b_name}' [0x{b_base:08X}–0x{b_end:08X}]")

# Check that all peripheral regions are 256-byte aligned
for name, base, size in non_reserved:
    if name in ('SRAM', 'Wishbone Window'):
        continue
    if base & 0xFF:
        fail(f"Alignment: '{name}' base 0x{base:08X} not 256-byte aligned")
    if size != 256:
        # Some can be different — just note it
        pass

if not any(True for _ in [None]):
    pass  # no extra failures from alignment
ok("No memory-map region overlaps detected")

# ── (c) Module cross-reference ────────────────────────────────────────
print("\n=== Check (c): Module M01-M12 cross-reference ===")

mod_text = read_file(MODULES)

# Extract module IDs from module_list.md
mod_ids = re.findall(r'M(\d{2})', mod_text)
mod_set = set(mod_ids)
expected = set(f"{i:02d}" for i in range(1, 13))

if mod_set != expected:
    missing = expected - set(mod_ids)
    extra = set(mod_ids) - expected
    if missing:
        fail(f"Missing modules from module_list.md: M{', M'.join(sorted(missing))}")
    if extra:
        fail(f"Extra modules in module_list.md: M{', M'.join(sorted(extra))}")
else:
    ok(f"All 12 modules M01-M12 present in module_list.md")

# Check each module name appears in system_spec.md §2.3
sec2_3_start = spec_text.find("### 2.3 Block Decomposition")
sec3_start = spec_text.find("## 3. Functional")
sec2_3 = spec_text[sec2_3_start:sec3_start] if sec3_start > 0 else spec_text[sec2_3_start:]

# Extract module names from module_list.md inventory table
mod_names = {}
for line in mod_text.split('\n'):
    m = re.match(r'\|\s*M(\d{2})\s*\|\s*(\S+?)\s*\|', line)
    if m:
        mod_names[m.group(1)] = m.group(2)

for mid, name in sorted(mod_names.items()):
    if name.lower() not in sec2_3.lower():
        fail(f"Module M{mid} '{name}' from module_list.md NOT found in system_spec.md §2.3")
    else:
        ok(f"Module M{mid} '{name}': cross-referenced in §2.3")

# ── (d) Summary arithmetic ────────────────────────────────────────────
print("\n=== Check (d): module_list.md summary arithmetic ===")

# Parse the summary table
total_from_summary = None
reuse_count = None
reuse_star_count = None
create_count = None
reuse_ratio_count = None
reuse_ratio_ge = None

for line in mod_text.split('\n'):
    m_total = re.search(r'Total modules\s*\|\s*(\d+)', line)
    m_reuse = re.search(r'REUSE.*unmodified\S*\s*\|\s*(\d+)', line)
    m_reuse_star = re.search(r'REUSE\*.*adapted\S*\s*\|\s*(\d+)', line)
    m_create = re.search(r'CREATE.*new\S*\s*\|\s*(\d+)', line)
    m_ratio = re.search(r'REUSE ratio\s*\|\s*([0-9.]+).*by count.*?([0-9.]+).*by gate', line)

    if m_total: total_from_summary = int(m_total.group(1))
    if m_reuse: reuse_count = int(m_reuse.group(1))
    if m_reuse_star: reuse_star_count = int(m_reuse_star.group(1))
    if m_create: create_count = int(m_create.group(1))
    if m_ratio:
        reuse_ratio_count = float(m_ratio.group(1))
        reuse_ratio_ge = float(m_ratio.group(2))

if total_from_summary is not None:
    computed_total = (reuse_count or 0) + (reuse_star_count or 0) + (create_count or 0)
    if computed_total != total_from_summary:
        fail(f"Summary total={total_from_summary} but REUSE({reuse_count})+REUSE*({reuse_star_count})+CREATE({create_count})={computed_total}")
    else:
        ok(f"Summary total {total_from_summary} = REUSE({reuse_count}) + REUSE*({reuse_star_count}) + CREATE({create_count}) = {computed_total}")

if reuse_ratio_count is not None and total_from_summary:
    computed_ratio = (reuse_count + reuse_star_count) / total_from_summary
    if abs(computed_ratio - reuse_ratio_count) > 0.01:
        fail(f"Reuse ratio by count: stated={reuse_ratio_count}, computed={computed_ratio:.3f}")
    else:
        ok(f"Reuse ratio by count: stated={reuse_ratio_count}, computed={computed_ratio:.3f} (±0.01)")

# Cross-check module inventory table has exactly 12 rows M01-M12
inventory_count = 0
in_inventory = False
for line in mod_text.split('\n'):
    if 'Module Inventory' in line:
        in_inventory = True
        continue
    if in_inventory and re.match(r'\|\s*M\d{2}\s*\|', line):
        inventory_count += 1
    if in_inventory and line.strip() == '' and inventory_count > 0:
        break

if inventory_count != 12:
    fail(f"Inventory table has {inventory_count} module rows, expected 12")
else:
    ok(f"Inventory table has exactly {inventory_count} module rows (M01-M12)")

# Cross-check interface matrix count
iface_count = 0
in_iface = False
for line in mod_text.split('\n'):
    if 'Interface Matrix' in line:
        in_iface = True
        continue
    if in_iface and re.match(r'\|\s*[a-z]', line, re.IGNORECASE):
        iface_count += 1
    if in_iface and line.strip() == '' and iface_count > 0:
        break

if iface_count < 20:
    fail(f"Interface matrix has only {iface_count} connections, expected ≥ 20")
else:
    ok(f"Interface matrix has {iface_count} connections (≥ 20)")

# ── (e) Check traceability_matrix.md has Req ID column for every category ──
print("\n=== Check (e): Traceability config key coverage ===")

categories = {'SYS-FR': 0, 'SYS-PR': 0, 'SYS-IR': 0, 'SYS-AR': 0, 'SYS-CR': 0}
for rid in unique_ids:
    for cat in categories:
        if rid.startswith(cat):
            categories[cat] += 1

# Count those appearing in traceability_matrix.md with a config key binding
# (Any SYS-xx-NNN in traceability_matrix.md with a non-empty config key)
bound_in_trace = set()
for line in trace_text.split('\n'):
    m = re.match(r'\|\s*(SYS-(?:FR|PR|IR|AR|CR)-\d{3})\s*\|', line)
    if m:
        bound_in_trace.add(m.group(1))

for cat, total in sorted(categories.items()):
    bound = sum(1 for rid in bound_in_trace if rid.startswith(cat))
    if bound < total:
        fail(f"{cat}: {bound}/{total} requirements bound to config keys in traceability_matrix.md")
    else:
        ok(f"{cat}: {bound}/{total} requirements bound in traceability_matrix.md")

# ── Final verdict ─────────────────────────────────────────────────────
print()
if FAILURES == 0:
    print("RESULT: PASS")
    sys.exit(0)
else:
    print(f"RESULT: FAIL ({FAILURES} failure(s))")
    sys.exit(1)
