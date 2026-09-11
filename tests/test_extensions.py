import unittest
from dp06_pyrolysis.extensions import empirical
from dp06_pyrolysis.extensions import daem_isoconversional as daem
from dp06_pyrolysis.extensions import comparison_harness as cmp
from dp06_pyrolysis.extensions import sewage_sludge_reference as ss
from dp06_pyrolysis.extensions import food_waste_reference as fw
from dp06_pyrolysis.extensions import validation_metrics as vm
from dp06_pyrolysis.extensions import model_selection as ms
from dp06_pyrolysis.extensions import optimization as opt
from dp06_pyrolysis.extensions import chemistry_fidelity as cf

class TestExtensions(unittest.TestCase):
    def test_emp_bio_holdout(self):
        r=empirical.emp_bio1_outer_anchor_holdout_600(); self.assertAlmostEqual(r['mae_pp'],2.1777777778,6); self.assertAlmostEqual(r['rmse_pp'],2.4883431941,6)
    def test_emp_bio_bounds(self):
        with self.assertRaises(ValueError): empirical.emp_bio1(450)
    def test_emp_man_values(self): self.assertAlmostEqual(empirical.emp_man1(700)['gas_phase_N_pct_initial_N'],38.3333333333,6)
    def test_emp_man_loo(self):
        r=empirical.emp_man1_leave_one_interior_out(); self.assertAlmostEqual(r['mae_pp'],6.7222222,5); self.assertAlmostEqual(r['rmse_pp'],6.9997795,5); self.assertAlmostEqual(r['max_abs_pp'],10,5)
    def test_emp_pl_midpoint(self): self.assertAlmostEqual(empirical.emp_pl1(5.0),455.5,6)
    def test_emp_pl_bounds(self):
        with self.assertRaises(ValueError): empirical.emp_pl1(20)
    def test_emp_mix_null(self): self.assertAlmostEqual(empirical.emp_mix1_char_null(.25,20,0),5.0)
    def test_emp_mix_fraction_guard(self):
        with self.assertRaises(ValueError): empirical.emp_mix1_char_null(1.1,20,0)
    def test_validation_metrics(self):
        r=vm.errors([1,2,4],[1,3,3]); self.assertAlmostEqual(r['mae'],2/3); self.assertAlmostEqual(r['bias'],0)
    def test_relative_zero_guard(self):
        with self.assertRaises(ValueError): vm.relative_error_percent(1,0)
    def test_nrmse_guard(self):
        with self.assertRaises(ValueError): vm.nrmse([1,1],[1,1],normalization='range')
    def test_selection_empirical(self):
        r=ms.select_framework(ms.StudyRequest(targets=frozenset({'source_bounded_yield'}))); self.assertEqual(r['core_level'],1)
    def test_selection_daem_data_gate(self):
        r=ms.select_framework(ms.StudyRequest(targets=frozenset({'E_alpha'}),heating_rates_available=2)); self.assertTrue(r['holds'])
    def test_selection_detailed_gate(self):
        r=ms.select_framework(ms.StudyRequest(targets=frozenset({'detailed_reaction_network'}),heating_rates_available=3,structural_feedstock_data_available=True)); self.assertTrue(r['holds'])
    def test_selection_pressure_hold(self):
        r=ms.select_framework(ms.StudyRequest(targets=frozenset({'bulk_TG_DTG'}),pressure_dependent_question=True)); self.assertTrue(r['holds'])
    def test_optimization_pareto(self): self.assertEqual(set(opt.pareto_front([[1,1],[2,0],[0,2],[.5,.5]],['max','max'])),{0,1,2})
    def test_optimization_pressure_hold(self):
        with self.assertRaises(ValueError): opt.inside_domain({'P':2},opt.OptimizationDomain({'P':(1,10)},pressure_enabled=False))
    def test_optimization_universal_prohibited(self):
        with self.assertRaises(RuntimeError): opt.universal_optimum()
    def test_chemistry_hold(self): self.assertEqual(cf.chemistry_level_for_question('detailed_reaction_network',cf.ChemistryEvidence())['level'],'HOLD')
    def test_chemistry_L7_exploration(self):
        e=cf.ChemistryEvidence(detailed_mechanism=True,provenance_rights_clear=True,feedstock_mapping_defined=True,numerical_integrity_verified=True)
        self.assertEqual(cf.chemistry_level_for_question('detailed_reaction_network',e)['level'],'L7')
    def test_universal_mechanism_prohibited(self):
        with self.assertRaises(RuntimeError): cf.universal_detailed_mechanism()
    def test_sludge_closure(self):
        r=ss.product_mass_closure(ss.ProductYieldPoint(58.7,22.4,18.9)); self.assertAlmostEqual(r['total_wt_pct'],100.0)
    def test_sludge_r2_ambiguity(self):
        c=[ss.CoatsRedfernCandidate('first',27.52,205.31,.984),ss.CoatsRedfernCandidate('surface',30,100,.982)]
        r=ss.top_model_r2_gap(c); self.assertAlmostEqual(r['delta_r2'],.002,6)
    def test_food_stage(self): self.assertEqual(fw.yasir_stage_order(.5),9.6)
    def test_food_domain_guard(self):
        with self.assertRaises(ValueError): fw.yasir_n_of_alpha(1.0)
    def test_daem_module_import(self): self.assertTrue(hasattr(daem,'kas'))
    def test_daem_and_kas_are_distinct_interfaces(self):
        self.assertTrue(hasattr(daem,'kas')); self.assertTrue(hasattr(daem,'daem_integral_source2021'))
        self.assertNotEqual(daem.kas.__name__, daem.daem_integral_source2021.__name__)
    def test_comparison_no_universal_score(self): self.assertFalse(hasattr(cmp,'universal_score'))

if __name__=='__main__': unittest.main(verbosity=2)
