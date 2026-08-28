"""Architecture boundary tests.

Enforces that domain microservices do not import private internals
(models.py, repository.py) from other domain microservices.
"""

import ast
import unittest
from pathlib import Path

SERVICES_ROOT = Path(__file__).resolve().parents[1] / "backend" / "services"
PRIVATE_MODULE_NAMES = {"models", "repository"}


class TestArchitectureBoundaries(unittest.TestCase):
    def test_package_boundary_isolation(self):
        """Verify that no service imports private internals of another service."""
        services = [
            d.name
            for d in SERVICES_ROOT.iterdir()
            if d.is_dir() and not d.name.startswith("__")
        ]

        violations = []

        for service in services:
            service_dir = SERVICES_ROOT / service
            for py_file in service_dir.rglob("*.py"):
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                for node in ast.walk(tree):
                    # Check: from backend.services.<other_service>.<private> import ...
                    if isinstance(node, ast.ImportFrom) and node.module:
                        parts = node.module.split(".")
                        if (
                            len(parts) >= 3
                            and parts[0] == "backend"
                            and parts[1] == "services"
                        ):
                            target_service = parts[2]
                            if (
                                target_service != service
                                and target_service in services
                            ):
                                if (
                                    len(parts) >= 4
                                    and parts[3] in PRIVATE_MODULE_NAMES
                                ):
                                    violations.append(
                                        f"{py_file.relative_to(SERVICES_ROOT.parent.parent)}: "
                                        f"Illegal import of private module '{node.module}' from service '{service}'"
                                    )

                    # Check: import backend.services.<other_service>.<private>
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            parts = alias.name.split(".")
                            if (
                                len(parts) >= 4
                                and parts[0] == "backend"
                                and parts[1] == "services"
                            ):
                                target_service = parts[2]
                                if (
                                    target_service != service
                                    and target_service in services
                                ):
                                    if parts[3] in PRIVATE_MODULE_NAMES:
                                        violations.append(
                                            f"{py_file.relative_to(SERVICES_ROOT.parent.parent)}: "
                                            f"Illegal import of private module '{alias.name}' from service '{service}'"
                                        )

        self.assertEqual(
            len(violations),
            0,
            "Architecture boundary violations detected:\n"
            + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
