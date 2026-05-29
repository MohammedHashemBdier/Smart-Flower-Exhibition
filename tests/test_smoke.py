import subprocess
import sys
import os


def test_smoke_run_main():
    # run main.py and ensure it prints the success banner
    cwd = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(cwd)
    proc = subprocess.run([sys.executable, os.path.join(repo_root, 'main.py')], capture_output=True, text=True, timeout=20)
    out = proc.stdout + proc.stderr
    assert 'Success: all pavilion demands were satisfied.' in out
