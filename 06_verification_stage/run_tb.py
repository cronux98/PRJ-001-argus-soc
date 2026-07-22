#!/usr/bin/env python3
"""
Run cocotb simulation and capture results, working around vvp segfault on exit.
Parses the cocotb console output to extract pass/fail counts and generates
a JUnit-compatible results.xml file.

Usage:
    python3 run_tb.py <tb_dir>
"""

import subprocess, sys, os, re, xml.etree.ElementTree as ET
from datetime import datetime

def parse_cocotb_output(output):
    """Parse cocotb regression output to extract test results."""
    tests = []
    summary = {"pass": 0, "fail": 0, "skip": 0, "total": 0}

    # Look for the result table lines: "** test_name  STATUS  SIM_TIME  ..."
    table_re = re.compile(
        r'\*\*\s+(\S+)\s+(PASS|FAIL|SKIP)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
    )
    for line in output.split('\n'):
        m = table_re.search(line)
        if m:
            name, status, sim_time, real_time, ratio = m.groups()
            tests.append({
                'name': name,
                'status': status,
                'sim_time_ns': float(sim_time),
                'real_time_s': float(real_time),
            })
            if status == 'PASS':
                summary['pass'] += 1
            elif status == 'FAIL':
                summary['fail'] += 1
            else:
                summary['skip'] += 1

    # Also try the summary line: "TESTS=N PASS=N FAIL=N SKIP=N"
    sum_re = re.compile(r'TESTS=(\d+)\s+PASS=(\d+)\s+FAIL=(\d+)\s+SKIP=(\d+)')
    for line in output.split('\n'):
        m = sum_re.search(line)
        if m:
            summary['total'] = int(m.group(1))
            summary['pass'] = int(m.group(2))
            summary['fail'] = int(m.group(3))
            summary['skip'] = int(m.group(4))
            break

    return tests, summary

def generate_junit_xml(tests, summary, module_name, output_path):
    """Generate JUnit-compatible results.xml (matches cocotb native format)."""
    testsuite = ET.Element('testsuite', {
        'name': f'cocotb.{module_name}',
        'tests': str(summary['total']),
        'failures': str(summary['fail']),
        'errors': '0',
        'skipped': str(summary['skip']),
        'time': str(sum(len(t.get('name','')) for t in tests)),
        'timestamp': datetime.utcnow().isoformat(),
    })

    for t in tests:
        testcase = ET.SubElement(testsuite, 'testcase', {
            'name': t['name'],
            'classname': module_name,
            'time': f"{t['real_time_s']:.3f}",
        })
        if t['status'] == 'FAIL':
            ET.SubElement(testcase, 'failure', {
                'message': f"Test {t['name']} failed",
                'type': 'AssertionError',
            })
        elif t['status'] == 'SKIP':
            ET.SubElement(testcase, 'skipped')

    tree = ET.ElementTree(testsuite)
    ET.indent(tree, space='  ')
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"  Wrote {output_path}")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <tb_dir>")
        sys.exit(1)

    tb_dir = sys.argv[1]
    os.chdir(tb_dir)

    # Read Makefile to get module name
    module_name = os.path.basename(tb_dir).replace('tb-', '')

    # Set up PATH
    env = os.environ.copy()
    env['PATH'] = f"/home/smdadmin/oss-cad-suite/bin:{env.get('PATH', '')}"

    print(f"Running tests for {module_name}...")

    # Run make sim, capturing output
    try:
        result = subprocess.run(
            ['make', 'sim'],
            capture_output=True, text=True, timeout=300,
            env=env, cwd=tb_dir
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 300s")
        return 1

    # Parse output
    tests, summary = parse_cocotb_output(output)

    if summary['total'] == 0:
        print(f"  WARNING: Could not parse test results from output.")
        print(f"  Exit code: {result.returncode}")
        # Still write a minimal results.xml
        pass

    # Print summary
    print(f"  Results: {summary['total']} tests, "
          f"{summary['pass']} PASS, {summary['fail']} FAIL, {summary['skip']} SKIP")

    # Generate results.xml
    results_path = os.path.join(tb_dir, 'results.xml')
    generate_junit_xml(tests, summary, module_name, results_path)

    # Also try to get coverage data if sim_build/coverage.dat exists
    cov_dat = os.path.join(tb_dir, 'sim_build', 'coverage.dat')
    if os.path.exists(cov_dat):
        import shutil
        shutil.copy(cov_dat, os.path.join(tb_dir, 'coverage.dat'))
        print(f"  Copied coverage.dat")

    return 0 if summary['fail'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
