"""
DEV-ONLY helper: loads student_validator.py and import_service.py directly by
file path (bypassing app/__init__.py, which imports Flask-SQLAlchemy) so their
pure logic can be exercised in environments without Flask installed yet.
This is NOT part of the delivered test suite - the real suite is
tests/unit/test_validators.py and tests/unit/test_import_service.py, run
normally with `pytest` after `pip install -r requirements.txt`.
"""
import importlib.util
import os
import sys
import types

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sv = _load("student_validator", "app/validators/student_validator.py")
isvc = _load("import_service", "app/services/import_service.py")

# Fake the package tree so `from app.validators.student_validator import ...`
# and `from app.services.import_service import ...` resolve to the modules we
# just loaded directly, without running app/__init__.py.
app_pkg = types.ModuleType("app")
validators_pkg = types.ModuleType("app.validators")
services_pkg = types.ModuleType("app.services")
sys.modules["app"] = app_pkg
sys.modules["app.validators"] = validators_pkg
sys.modules["app.validators.student_validator"] = sv
sys.modules["app.services"] = services_pkg
sys.modules["app.services.import_service"] = isvc


def run_module(path):
    spec = importlib.util.spec_from_file_location("test_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tests = [v for k, v in vars(mod).items() if k.startswith("test_") and callable(v)]
    passed, failed = 0, []
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
        except Exception as e:
            failed.append((t.__name__, f"{type(e).__name__}: {e}"))
    return passed, failed, len(tests)


if __name__ == "__main__":
    total_passed, total_failed = 0, 0
    for f in ["test_validators.py", "test_import_service.py"]:
        p = os.path.join(os.path.dirname(__file__), f)
        passed, failed, total = run_module(p)
        print(f"\n=== {f} ===")
        for name, err in failed:
            print(f"FAIL  {name}: {err}")
        print(f"{passed}/{total} passed")
        total_passed += passed
        total_failed += len(failed)
    print(f"\nTOTAL: {total_passed} passed, {total_failed} failed")
    sys.exit(1 if total_failed else 0)
