import json, pathlib, unittest, re
ROOT=pathlib.Path(__file__).resolve().parents[1]

class TestAccess(unittest.TestCase):
    def test_registry(self):
        r=json.loads((ROOT/'data/model_access_registry.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(r),10)
        self.assertTrue(all(x['model_or_tool'] and x['scientific_role'] for x in r))
        self.assertTrue(all('candidate' not in x['release_status'].lower() for x in r))
    def test_packaged_registry_matches_repository_registry(self):
        a=json.loads((ROOT/'data/model_access_registry.json').read_text(encoding='utf-8'))
        b=json.loads((ROOT/'src/dp06_pyrolysis/data/model_access_registry.json').read_text(encoding='utf-8'))
        self.assertEqual(a,b)
    def test_docs(self):
        for p in ['docs/MODEL_CATALOG.md','docs/VALIDATION_CATALOG.md','docs/MANUSCRIPT_CODE_CROSSWALK.md','docs/READER_ACCESS.md']:
            self.assertTrue((ROOT/p).exists())
    def test_validation_examples(self):
        self.assertGreaterEqual(len(list((ROOT/'examples/validation').glob('*.json'))),7)
    def test_v020_metadata(self):
        py=(ROOT/'pyproject.toml').read_text(encoding='utf-8')
        self.assertRegex(py, r'version\s*=\s*"0\.2\.0"')
        self.assertIn('numpy>=1.24',py)
        c=(ROOT/'CITATION.cff').read_text(encoding='utf-8')
        self.assertIn('version: "0.2.0"',c)
        self.assertNotIn('zenodo.xxxxx',c.lower())
    def test_corrected_evidence_taxonomy(self):
        v=(ROOT/'docs/VALIDATION_CATALOG.md').read_text(encoding='utf-8')
        self.assertIn('independent cross-study trend comparison',v)
        self.assertIn('independent cross-grade transfer',v)
        self.assertNotIn('CHAR-O-RET         | Beech high-T char            | independent same-feedstock transfer',v)

if __name__=='__main__': unittest.main()
