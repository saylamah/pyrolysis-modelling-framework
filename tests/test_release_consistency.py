import json
import unittest
from pathlib import Path

from dp06_pyrolysis.adapters import adapter_for

ROOT = Path(__file__).resolve().parents[1]


class ReleaseConsistencyTests(unittest.TestCase):
    def test_sfor_fidelity_matches_v020_L1_L9_hierarchy(self):
        self.assertEqual(adapter_for("SFOR_RWTH").manifest.fidelity_level, "L2")
        profiles = json.loads((ROOT / "data" / "model_passport_profiles.json").read_text())
        self.assertEqual(profiles["SFOR_RWTH"]["level"], "L2")


if __name__ == "__main__":
    unittest.main()
