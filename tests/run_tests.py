import sys
import os
from pathlib import Path
import pytest
import io
import re
from contextlib import redirect_stdout, redirect_stderr

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

project_root = Path(__file__).parent.parent
src_path = project_root / "src"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

os.chdir(project_root)

CATEGORIES = {
    "1": {"name": "User Tests", "path": "tests/unit/test_user"},
    "2": {"name": "Messages Tests", "path": "tests/unit/test_messages"},
    "3": {"name": "Chats Tests", "path": "tests/unit/test_chats"},
    "4": {"name": "Database Tests", "path": "tests/unit/test_database"},
    "5": {"name": "Repository Tests", "path": "tests/unit/test_repository"},
    "6": {"name": "Security Tests", "path": "tests/unit/test_security"},
    "7": {"name": "Sessions Tests", "path": "tests/unit/test_sessions"},
    "8": {"name": "Calls Tests", "path": "tests/unit/test_calls"},
    "9": {"name": "ALL TESTS", "path": "tests/unit"},
}

def print_categories():
    print("\n" + "=" * 60)
    print("SELECT TEST CATEGORY")
    print("=" * 60)

    for key, value in CATEGORIES.items():
        print(f"  {key}. {value['name']}")

    print(f"  0. Exit")
    print("=" * 60)

def parse_test_results(output):
    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    patterns = {
        'passed': r'(\d+)\s+passed',
        'failed': r'(\d+)\s+failed',
        'errors': r'(\d+)\s+errors',
        'skipped': r'(\d+)\s+skipped',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            value = int(match.group(1))
            if key == 'passed':
                passed = value
            elif key == 'failed':
                failed = value
            elif key == 'errors':
                errors = value
            elif key == 'skipped':
                skipped = value

    total = passed + failed + errors + skipped

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'errors': errors,
        'skipped': skipped
    }

def run_tests(path):
    print(f"\nRunning: {path}")
    print("-" * 60)

    f = io.StringIO()
    with redirect_stdout(f), redirect_stderr(f):
        result = pytest.main(["-v", "--tb=short", path])
        output = f.getvalue()

    print(output)

    stats = parse_test_results(output)

    return result, output, stats

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in CATEGORIES:
            path = CATEGORIES[arg]["path"]
            result, output, stats = run_tests(path)
            sys.exit(result)
        else:
            print(f"Category '{arg}' not found")
            print("Available categories:")
            for key, value in CATEGORIES.items():
                print(f"  {key}. {value['name']}")
            sys.exit(1)

    while True:
        print_categories()
        choice = input("\nSelect category (number): ").strip()

        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        elif choice in CATEGORIES:
            path = CATEGORIES[choice]["path"]
            result, output, stats = run_tests(path)
            print(f"\nTests completed with exit code: {result}")
        else:
            print("Invalid choice. Please try again.")