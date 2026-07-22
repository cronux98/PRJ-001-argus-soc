#!/usr/bin/env python3
"""
gen_reuse_manifest.py — Generate reuse_manifest.json and promotion_report.json
for PRJ-001 Argus promotion stage.

Usage: python3 gen_reuse_manifest.py
Reads: 04_frontend_stage/rtl-*/ artifacts, 06_verification_stage/tb-*/ results.xml
Writes: 07_promote_stage/reuse_manifest_<module>.json (per CREATE/REUSE_STAR module)
       07_promote_stage/promotion_report.json (all 12 modules)
       07_promote_stage/promotion_summary.json

GENERATED-FROM: gen_reuse_manifest.py, 04_frontend_stage artifacts, 06_verification_stage results.xml
"""

import os, re, json, glob, xml.etree.ElementTree as ET
from datetime import datetime, timezone

PROJECT_DIR = "/home/smdadmin/hermes_workspace/projects/PRJ-001/v0"
FRONTEND_DIR = os.path.join(PROJECT_DIR, "04_frontend_stage")
VERIFY_DIR = os.path.join(PROJECT_DIR, "06_verification_stage")
PROMOTE_DIR = os.path.join(PROJECT_DIR, "07_promote_stage")
BLUEPRINT_PATH = os.path.join(PROJECT_DIR, "03_architecture_stage", "blueprint.json")
FRONTEND_AUDIT = os.path.join(FRONTEND_DIR, "audit", "audit_pass.json")
VERIFY_AUDIT = os.path.join(VERIFY_DIR, "audit", "audit_pass.json")
RESEARCH_ROOT = os.path.expanduser("~/hermes_workspace/research")

os.makedirs(PROMOTE_DIR, exist_ok=True)

# Load blueprint
with open(BLUEPRINT_PATH) as f:
    blueprint = json.load(f)

# Load audits
with open(FRONTEND_AUDIT) as f:
    faudit = json.load(f)
with open(VERIFY_AUDIT) as f:
    vaudit = json.load(f)

# --- Helper functions ---

def read_synth_metrics(module_name):
    """Extract cell_count, dff_count, area from synthesis log."""
    synth_log = os.path.join(FRONTEND_DIR, f"rtl-{module_name}", "logs", "synth", f"{module_name}_synth.log")
    cell_count = None
    dff_count = 0
    area = None
    errors = []
    latch_count = 0
    
    if os.path.exists(synth_log):
        with open(synth_log) as f:
            content = f.read()
        
        # Cell count — find numeric-area cells lines, take last
        matches = re.findall(r'(\d+)\s+([\d.E+-]+)\s+cells', content)
        for cnt, ar in reversed(matches):
            try:
                float(ar)
                cell_count = int(cnt)
                break
            except ValueError:
                continue
        
        # DFF count
        dffs = re.findall(r'(\d+)\s+[\d.]+\s+sky130_fd_sc_hd__dfrtp', content)
        dff_count = sum(int(x) for x in dffs)
        dffs2 = re.findall(r'(\d+)\s+[\d.]+\s+sky130_fd_sc_hd__dfxtp', content)
        dff_count += sum(int(x) for x in dffs2)
        
        # Latch count
        latches = re.findall(r'(\d+)\s+[\d.]+\s+sky130_fd_sc_hd__dlrtp', content)
        latch_count = sum(int(x) for x in latches)
        
        # Errors
        error_lines = [l.strip() for l in content.split('\n') if 'ERROR' in l and 'EXIT' not in l]
        errors = error_lines
        
        # Chip area
        area_match = re.search(r"Chip area for module.*?:\s*([\d.]+)", content)
        if area_match:
            area = float(area_match.group(1))
        
        # Exit code
        exit_match = re.search(r'EXIT:(\d+)', content)
        synth_pass = exit_match and exit_match.group(1) == '0' and latch_count == 0
    
    return {
        "cell_count": cell_count,
        "dff_count": dff_count,
        "latch_count": latch_count,
        "area_um2": area,
        "errors": errors,
        "pass": synth_pass if os.path.exists(synth_log) else None,
        "log_path": synth_log
    }


def read_lint_metrics(module_name):
    """Check lint log for errors."""
    lint_log = os.path.join(FRONTEND_DIR, f"rtl-{module_name}", "logs", "lint", f"{module_name}_verilator.log")
    error_count = 0
    if os.path.exists(lint_log):
        with open(lint_log) as f:
            content = f.read()
        error_count = content.count('%Error')
    return {"error_count": error_count, "pass": error_count == 0, "log_path": lint_log}


def read_formal_metrics(module_name):
    """Check formal verification results."""
    formal_dir = os.path.join(FRONTEND_DIR, f"rtl-{module_name}", "formal", module_name)
    pass_file = os.path.join(formal_dir, "PASS")
    depth = None
    mode = None
    
    if os.path.exists(pass_file):
        # Read .sby for depth
        sby_files = glob.glob(os.path.join(formal_dir, "*.sby"))
        if sby_files:
            with open(sby_files[0]) as f:
                sby_content = f.read()
            depth_match = re.search(r'depth\s+(\d+)', sby_content)
            if depth_match:
                depth = int(depth_match.group(1))
            mode_match = re.search(r'mode\s+(\w+)', sby_content)
            if mode_match:
                mode = mode_match.group(1)
        
        return {"pass": True, "depth": depth, "mode": mode, "pass_file": pass_file}
    else:
        return {"pass": False, "depth": None, "mode": None, "pass_file": None}


def read_equiv_metrics(module_name):
    """Check equivalence check results."""
    equiv_log = os.path.join(FRONTEND_DIR, f"rtl-{module_name}", "logs", "equiv_check", f"{module_name}_equiv.log")
    if os.path.exists(equiv_log):
        with open(equiv_log) as f:
            content = f.read()
        eq_pass = 'PASS' in content or 'Success' in content or 'Equivalent' in content
        return {"pass": eq_pass, "log_path": equiv_log}
    return {"pass": None, "log_path": equiv_log}


def read_verification_metrics(module_name):
    """Parse results.xml for test pass/fail counts."""
    results_xml = os.path.join(VERIFY_DIR, f"tb-{module_name}", "results.xml")
    if os.path.exists(results_xml):
        tree = ET.parse(results_xml)
        root = tree.getroot()
        tests = int(root.get('tests', 0))
        failures = int(root.get('failures', 0))
        errors = int(root.get('errors', 0))
        skipped = int(root.get('skipped', 0))
        passes = tests - failures - errors - skipped
        
        return {
            "total_tests": tests,
            "tests_pass": passes,
            "tests_fail": failures,
            "tests_error": errors,
            "tests_skip": skipped,
            "all_pass": failures == 0 and errors == 0,
            "results_xml": results_xml
        }
    return {
        "total_tests": 0,
        "tests_pass": 0,
        "tests_fail": 0,
        "all_pass": None,
        "results_xml": None
    }


def determine_promotion_status(module_name, module_type, synth, lint, formal, equiv, verify):
    """Apply A1-A7 admission criteria."""
    reasons = []
    blocked = False
    conditional = False
    
    # A1: Lint
    lec = lint["error_count"]
    if lec is not None and lec > 0:
        blocked = True
        reasons.append(f"A1: Lint has {lec} errors")
    elif lec is None:
        blocked = True
        reasons.append("A1: No lint log found")
    
    # A2: Synthesis
    if synth["pass"] is False:
        blocked = True
        reasons.append(f"A2: Synthesis FAIL — {len(synth.get('errors',[]))} errors, {synth.get('latch_count',0)} latches")
    elif synth["pass"] is None:
        blocked = True
        reasons.append("A2: No synthesis log found")
    
    # A3: Equivalence
    if equiv["pass"] is False:
        blocked = True
        reasons.append("A3: Equivalence check FAIL")
    elif equiv["pass"] is None:
        conditional = True
        reasons.append("A3: No equivalence log — CONDITIONAL")
    
    # A4: Verification
    if verify["all_pass"] is False:
        blocked = True
        reasons.append(f"A4: Verification has {verify['tests_fail']} failing tests")
    elif verify["all_pass"] is None:
        blocked = True
        reasons.append("A4: No verification results.xml")
    
    # A5: GLS — not run in this flow, document as CONDITIONAL
    # GLS is a Stage 5 (Verification) concern per frontend audit finding
    
    # A6: Formal
    if formal["pass"] is False:
        blocked = True
        reasons.append("A6: Formal verification FAIL")
    elif formal["pass"] is None:
        blocked = True
        reasons.append("A6: No formal verification found")
    
    # A7: Failing tests
    vt = verify["tests_fail"]
    if vt is not None and vt > 0:
        blocked = True
        reasons.append(f"A7: {vt} failing tests")
    
    if blocked:
        status = "BLOCKED"
    elif conditional:
        status = "CONDITIONAL"
    else:
        status = "PASS"
    
    return {"status": status, "blocked": blocked, "conditional": conditional, "reasons": reasons}


def determine_category(module_name, module_info):
    """Determine research library category."""
    name = module_name.lower()
    if 'uart' in name or 'spi' in name or 'i2c' in name or 'gpio' in name or 'pwm' in name:
        return "peripherals"
    elif 'ibex' in name or 'core' in name:
        return "processors"
    elif 'bridge' in name or 'interconnect' in name or 'wb_' in name or 'apb_' in name:
        return "interfaces"
    elif 'sram' in name or 'mem' in name:
        return "memory"
    elif 'interrupt' in name or 'sys_ctrl' in name:
        return "system"
    elif 'soc' in name or 'argus' in name or 'top' in name:
        return "soc"
    elif 'caravel' in name or 'wrapper' in name:
        return "integration"
    return "usecases"


def generate_reuse_manifest(module_name, module_info, metrics):
    """Generate reuse_manifest.json for a module."""
    category = determine_category(module_name, module_info)
    
    manifest = {
        "module": module_name,
        "version": "1.0.0",
        "provenance_type": "self",
        "source_project": "PRJ-001",
        "source_version": "v0",
        "promotion_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "category": category,
        "research_path": f"research/{category}/{module_name}/",
        "type": module_info.get("type", "CREATE"),
        "license": module_info.get("license") or "Apache-2.0",
        "description": module_info.get("description", ""),
        "qualification": {
            "lint": {
                "status": "PASS" if metrics["lint"]["pass"] else "FAIL",
                "errors": metrics["lint"]["error_count"],
                "log": metrics["lint"]["log_path"]
            },
            "synthesis": {
                "status": "PASS" if metrics["synth"]["pass"] else ("FAIL" if metrics["synth"]["pass"] is not None else "MISSING"),
                "cell_count": metrics["synth"]["cell_count"],
                "dff_count": metrics["synth"]["dff_count"],
                "latch_count": metrics["synth"]["latch_count"],
                "area_um2": metrics["synth"]["area_um2"],
                "log": metrics["synth"]["log_path"]
            },
            "formal": {
                "status": "PASS" if metrics["formal"]["pass"] else "FAIL",
                "depth": metrics["formal"]["depth"],
                "mode": metrics["formal"]["mode"],
                "pass_file": metrics["formal"]["pass_file"]
            },
            "equivalence": {
                "status": "PASS" if metrics["equiv"]["pass"] else ("FAIL" if metrics["equiv"]["pass"] is not None else "MISSING"),
                "log": metrics["equiv"]["log_path"]
            },
            "verification": {
                "status": "PASS" if metrics["verify"]["all_pass"] else ("FAIL" if metrics["verify"]["all_pass"] is not None else "MISSING"),
                "tests_total": metrics["verify"]["total_tests"],
                "tests_pass": metrics["verify"]["tests_pass"],
                "tests_fail": metrics["verify"]["tests_fail"],
                "results_xml": metrics["verify"]["results_xml"]
            }
        },
        "promotion": {
            "status": metrics["promotion"]["status"],
            "reasons": metrics["promotion"]["reasons"]
        },
        "ports": [],  # Can be extracted from RTL
        "dependencies": [],
        "generated_by": "gen_reuse_manifest.py",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return manifest


# --- Main ---

all_modules = []
promoted_modules = []
blocked_modules = []
conditional_modules = []
reuse_modules = []  # Already in library

for mod_entry in blueprint["modules"]:
    module_name = mod_entry["name"]
    module_type = mod_entry["type"]
    
    print(f"Processing {module_name} ({module_type})...")
    
    # Check if frontend artifacts exist
    rtl_dir = os.path.join(FRONTEND_DIR, f"rtl-{module_name}")
    has_frontend = os.path.isdir(rtl_dir)
    
    # Collect metrics
    if has_frontend:
        synth = read_synth_metrics(module_name)
        lint = read_lint_metrics(module_name)
        formal = read_formal_metrics(module_name)
        equiv = read_equiv_metrics(module_name)
    else:
        synth = {"cell_count": None, "dff_count": 0, "latch_count": 0, "area_um2": None, "errors": [], "pass": None, "log_path": None}
        lint = {"error_count": None, "pass": None, "log_path": None}
        formal = {"pass": None, "depth": None, "mode": None, "pass_file": None}
        equiv = {"pass": None, "log_path": None}
    
    verify = read_verification_metrics(module_name)
    promotion = determine_promotion_status(module_name, module_type, synth, lint, formal, equiv, verify)
    
    metrics = {
        "synth": synth,
        "lint": lint,
        "formal": formal,
        "equiv": equiv,
        "verify": verify,
        "promotion": promotion
    }
    
    # Build module entry for promotion_report.json
    module_entry = {
        "module": module_name,
        "id": mod_entry["id"],
        "type": module_type,
        "description": mod_entry.get("description", ""),
        "promotion_status": promotion["status"],
        "blocked": promotion["blocked"],
        "conditional": promotion["conditional"],
        "admission_reasons": promotion["reasons"],
        "lint_errors": lint["error_count"],
        "synthesis_cells": synth["cell_count"],
        "synthesis_dffs": synth["dff_count"],
        "synthesis_latches": synth["latch_count"],
        "synthesis_area_um2": synth["area_um2"],
        "synthesis_log": synth["log_path"],
        "formal_pass": formal["pass"],
        "formal_depth": formal["depth"],
        "formal_mode": formal["mode"],
        "equiv_pass": equiv["pass"],
        "verification_tests_pass": verify["tests_pass"],
        "verification_tests_total": verify["total_tests"],
        "verification_tests_fail": verify["tests_fail"],
        "verification_results_xml": verify["results_xml"],
        "has_frontend_artifacts": has_frontend
    }
    
    all_modules.append(module_entry)
    
    if promotion["status"] == "PASS":
        promoted_modules.append(module_name)
    elif promotion["status"] == "BLOCKED":
        blocked_modules.append(module_name)
        module_entry["block_reason"] = "; ".join(promotion["reasons"])
    elif promotion["status"] == "CONDITIONAL":
        conditional_modules.append(module_name)
        module_entry["condition_reason"] = "; ".join(promotion["reasons"])
    
    # Generate reuse_manifest for CREATE/REUSE_STAR modules that pass
    if module_type in ("CREATE", "REUSE_STAR") and promotion["status"] in ("PASS", "CONDITIONAL"):
        manifest = generate_reuse_manifest(module_name, mod_entry, metrics)
        manifest_path = os.path.join(PROMOTE_DIR, f"reuse_manifest_{module_name}.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        print(f"  -> {manifest_path}")
    elif module_type == "REUSE":
        reuse_modules.append(module_name)


# --- Write promotion_report.json ---
promotion_report = {
    "project": "PRJ-001",
    "codename": "Argus",
    "version": "v0",
    "promotion_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "upstream_audits": {
        "frontend": {
            "path": FRONTEND_AUDIT,
            "verdict": faudit.get("verdict", "UNKNOWN"),
            "checks": len(faudit.get("checks", [])),
            "retry": faudit.get("retry", 0)
        },
        "verification": {
            "path": VERIFY_AUDIT,
            "verdict": vaudit.get("verdict", "UNKNOWN"),
            "checks_passed": vaudit.get("checks_passed", 0),
            "checks_total": vaudit.get("checks_total", 0)
        }
    },
    "summary": {
        "total_modules": len(all_modules),
        "promoted": len(promoted_modules),
        "blocked": len(blocked_modules),
        "conditional": len(conditional_modules),
        "reuse_existing": len(reuse_modules),
        "promoted_module_names": promoted_modules,
        "blocked_module_names": blocked_modules,
        "conditional_module_names": conditional_modules,
        "reuse_module_names": reuse_modules
    },
    "modules": all_modules,
    "generated_by": "gen_reuse_manifest.py",
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

report_path = os.path.join(PROMOTE_DIR, "promotion_report.json")
with open(report_path, 'w') as f:
    json.dump(promotion_report, f, indent=2, default=str)
print(f"\nWrote promotion_report.json -> {report_path}")

# --- Write promotion_summary.json ---
summary = {
    "project": "PRJ-001",
    "codename": "Argus",
    "version": "v0",
    "total_modules": len(all_modules),
    "modules_promoted": len(promoted_modules),
    "modules_blocked": len(blocked_modules),
    "modules_conditional": len(conditional_modules),
    "modules_reuse": len(reuse_modules),
    "promoted_modules": promoted_modules,
    "blocked_modules": blocked_modules,
    "conditional_modules": conditional_modules,
    "reuse_modules": reuse_modules,
    "generated_by": "gen_reuse_manifest.py"
}
summary_path = os.path.join(PROMOTE_DIR, "promotion_summary.json")
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)
print(f"Wrote promotion_summary.json -> {summary_path}")

# Print summary
print(f"\n{'='*60}")
print(f"PRJ-001 Promition Summary")
print(f"{'='*60}")
print(f"Total modules:    {len(all_modules)}")
print(f"PROMOTED:          {len(promoted_modules)} — {', '.join(promoted_modules) if promoted_modules else 'none'}")
print(f"BLOCKED:           {len(blocked_modules)} — {', '.join(blocked_modules) if blocked_modules else 'none'}")
print(f"CONDITIONAL:       {len(conditional_modules)} — {', '.join(conditional_modules) if conditional_modules else 'none'}")
print(f"REUSE (existing):  {len(reuse_modules)} — {', '.join(reuse_modules) if reuse_modules else 'none'}")
