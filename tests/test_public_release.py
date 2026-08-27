import json
import tempfile
import unittest
from pathlib import Path

from dp06_pyrolysis.preflight import preflight_config
from dp06_pyrolysis.unified import run_unified_config
from dp06_pyrolysis.reporting import load_result, build_user_report
from dp06_pyrolysis.example_suite import verify_example_suite
from dp06_pyrolysis.adapters import adapter_for, AdapterNotImplementedError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/"examples"/"suite_manifest.json"

class PublicReleaseTests(unittest.TestCase):
    def test_manifest_has_four_examples(self):
        m=json.loads(MANIFEST.read_text())
        self.assertEqual(len(m["examples"]),4)

    def test_all_examples_preflight(self):
        m=json.loads(MANIFEST.read_text())
        for e in m["examples"]:
            p=preflight_config(ROOT/"examples"/e["run_file"])
            self.assertEqual(p.status,"PASS",e["example_id"])
            self.assertEqual(p.selected_model,"SFOR_RWTH")

    def test_all_examples_match_baseline_scientific_outputs(self):
        m=json.loads(MANIFEST.read_text())
        for e in m["examples"]:
            out=Path(run_unified_config(ROOT/"examples"/e["run_file"]))
            r=json.loads(out.read_text())
            self.assertAlmostEqual(
                r["outputs"]["total_volatile_yield_fraction"],
                e["baseline_expected_total_volatile_yield_fraction"],
                places=12
            )
            self.assertAlmostEqual(
                r["outputs"]["remaining_solid_fraction"],
                e["baseline_expected_remaining_solid_fraction"],
                places=12
            )

    def test_mass_closure(self):
        m=json.loads(MANIFEST.read_text())
        for e in m["examples"]:
            r=json.loads(Path(run_unified_config(ROOT/"examples"/e["run_file"])).read_text())
            self.assertAlmostEqual(r["mass_ledger"]["closure_residual"],0.0,places=12)

    def test_evidence_not_promoted(self):
        m=json.loads(MANIFEST.read_text())
        for e in m["examples"]:
            r=json.loads(Path(run_unified_config(ROOT/"examples"/e["run_file"])).read_text())
            self.assertEqual(r["evidence_passport"]["evidence"]["result_status"],"calibrated")

    def test_user_report_exposes_warnings_and_rights(self):
        e=json.loads(MANIFEST.read_text())["examples"][0]
        r=build_user_report(load_result(run_unified_config(ROOT/"examples"/e["run_file"])))
        self.assertEqual(r["overall_status"],"PASS_WITH_WARNINGS")
        self.assertEqual(r["evidence"]["result_status"],"calibrated")
        self.assertIn("boundary",r["rights_provenance"])

    def test_unintegrated_model_fails_explicitly(self):
        with self.assertRaises(AdapterNotImplementedError):
            adapter_for("CRECK_BIOMASS")

    def test_validated_sfor_request_is_blocked(self):
        m=json.loads(MANIFEST.read_text())
        e=m["examples"][0]
        cfg=json.loads((ROOT/"examples"/e["run_file"]).read_text())
        cfg["request"]["evidence_requirement"]="validated"
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            cfg["case_file"]=str((ROOT/"examples"/e["case_file"]).resolve())
            cfg["profiles_file"]=str((ROOT/"data"/"model_passport_profiles.json").resolve())
            cfg["output_file"]=str(td/"result.json")
            p=td/"run.json"
            p.write_text(json.dumps(cfg))
            pre=preflight_config(p)
            self.assertEqual(pre.status,"FAIL")
            self.assertTrue(any(x["code"]=="SELECTOR_BLOCKED" for x in pre.issues))
            self.assertFalse((td/"result.json").exists())

    def test_example_suite_exact_rerun(self):
        report=verify_example_suite(MANIFEST,reruns=2)
        self.assertTrue(report["all_pass"])
        self.assertEqual(report["example_count"],4)

    def test_public_schema_names(self):
        r=json.loads(Path(run_unified_config(ROOT/"examples"/"cellulose_tga_run.json")).read_text())
        self.assertEqual(r["schema"],"PyrolysisFramework_RunResult_v1")
        self.assertEqual(r["evidence_passport"]["schema"],"PyrolysisFramework_EvidencePassport_v2")

if __name__=="__main__":
    unittest.main()
