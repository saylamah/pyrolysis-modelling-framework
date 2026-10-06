from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
required=[
    'README.md','CHANGELOG.md','CITATION.cff','RELEASE_STATUS.md','RELEASE_NOTES_v0.2.0.md','THIRD_PARTY_NOTICES.md','pyproject.toml',
    'data/model_access_registry.json','src/dp06_pyrolysis/data/model_access_registry.json',
    'docs/MODEL_CATALOG.md','docs/VALIDATION_CATALOG.md','docs/MANUSCRIPT_CODE_CROSSWALK.md','docs/READER_ACCESS.md','docs/QUICKSTART_EXTENSIONS.md',
    'src/dp06_pyrolysis/extensions/empirical.py','src/dp06_pyrolysis/extensions/daem_isoconversional.py','src/dp06_pyrolysis/extensions/validation_metrics.py',
    'tests/test_access_registry.py','tests/test_extensions.py'
]
missing=[p for p in required if not (ROOT/p).exists()]
if missing:
    raise SystemExit('Missing required v0.2.0 files: '+', '.join(missing))
py=(ROOT/'pyproject.toml').read_text(encoding='utf-8')
if not re.search(r'version\s*=\s*"0\.2\.0"',py):
    raise SystemExit('pyproject.toml is not version 0.2.0')
forbidden=['0.2.0rc','v0.2.0 candidate','release candidate','zenodo.xxxxx','10.5281/zenodo.xxxxx','not yet published','not yet archived','doi reserved / not yet','reserved v0.2.0 doi','extension — —','extension — p1-b','extension — p2-fw1','extension — s4','common daem / isoconversional comparison instrument v0.1','unified frozen-adapter comparison harness v1.0','common validation and uncertainty metrics v1.0','sewage-sludge source/reference adapter v1.0','food-waste source/reference adapter v1.0']
scan=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.md','.json','.toml','.cff','.py'}:
        continue
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith('tests/') or rel == 'tools/verify_v020_release.py':
        continue
    scan.append(p)
for p in scan:
    text=p.read_text(encoding='utf-8',errors='replace').lower()
    for token in forbidden:
        if token.lower() in text:
            raise SystemExit(f'Forbidden pre-release token {token!r} in {p.relative_to(ROOT)}')
val=(ROOT/'docs/VALIDATION_CATALOG.md').read_text(encoding='utf-8')
if 'independent cross-study trend comparison' not in val:
    raise SystemExit('CHAR-O-RET evidence topology not corrected')
if 'independent cross-grade transfer' not in val:
    raise SystemExit('LDPE evidence topology not corrected')
if 'same-study/null diagnostic' in val:
    raise SystemExit('Obsolete EMP-MIX1 topology remains')
if 'quantitative FAIL / causal diagnostic PASS; no refit' not in val:
    raise SystemExit('CRECK explicit quantitative/diagnostic status missing')
if '| Bio-CPD/CRECK/SFOR | Extracted biomass components | cross-model literature comparison |' not in val:
    raise SystemExit('Cross-model literature comparison topology missing')
if 'source-model reproduction; independent raw experimental validation limited/not established' not in val:
    raise SystemExit('BIO-PF1 source-reproduction boundary missing')
if 'full dynamic/time-history execution HOLD' not in val:
    raise SystemExit('PVC full-dynamic HOLD boundary missing')
if '[59,60]' in val or re.search(r'\[(61|62|63|64|66)\]', val):
    raise SystemExit('Stale pre-renumbering manuscript citation remains in VALIDATION_CATALOG.md')
reg=json.loads((ROOT/'data/model_access_registry.json').read_text(encoding='utf-8'))
if any('candidate' in x.get('release_status','').lower() for x in reg):
    raise SystemExit('Candidate status remains in model_access_registry')
if json.loads((ROOT/'src/dp06_pyrolysis/data/model_access_registry.json').read_text(encoding='utf-8')) != reg:
    raise SystemExit('Packaged and repository model-access registries differ')
print('v0.2.0 release-integrity metadata checks: PASS')
