import math
import random
import unittest
from pathlib import Path

from dp06_pyrolysis.core import (
    CompositionBlock, FeedstockPassport, ThermalProgram, RegimePassport,
    ModelRequest, StudyCase
)
from dp06_pyrolysis.types import (
    Basis, QualityStatus, FeedstockFamily, AtmosphereClass, EvidenceIntent
)
from dp06_pyrolysis.integrity import validate_composition_block, validate_study_case, IntegrityError
from dp06_pyrolysis.kinetics import (
    ArrheniusReaction, first_order_isothermal_conversion, first_order_linear_ramp,
    independent_parallel_conversion, R_J_PER_MOL_K
)
from dp06_pyrolysis.products import ProductState
from dp06_pyrolysis.balances import MassLedger, ElementLedger
from dp06_pyrolysis.adapters import adapter_for, AdapterDomainError, stable_sfor_linear_ramp
from dp06_pyrolysis.models.rwth2021 import sfor_linear_ramp
from dp06_pyrolysis.minimal_models import FirstOrderScreeningModel

ROOT = Path(__file__).resolve().parents[1]


def simpson_reference(A, E, T0, T1, beta, n=20000):
    if n % 2:
        n += 1
    h = (T1-T0)/n
    def f(T):
        return A*math.exp(-E/(R_J_PER_MOL_K*T))/beta
    total = f(T0) + f(T1)
    for i in range(1, n):
        total += (4 if i % 2 else 2)*f(T0+i*h)
    integral = total*h/3.0
    return 1.0-math.exp(-integral)


def simple_case(atmosphere=AtmosphereClass.INERT):
    prox = CompositionBlock(
        Basis.DRY, QualityStatus.ASSUMED,
        {"volatile_matter":0.80, "fixed_carbon":0.18, "ash":0.02}, True
    )
    feed = FeedstockPassport(
        "F1", FeedstockFamily.LIGNOCELLULOSIC_BIOMASS, "synthetic",
        "synthetic_architecture_test", "prov-1", prox
    )
    fractions = {"N2":1.0} if atmosphere == AtmosphereClass.INERT else {"CO2":1.0}
    reg = RegimePassport(
        ThermalProgram("isothermal", T_K=700.0, hold_time_s=1.0),
        101325.0, atmosphere, fractions
    )
    return StudyCase(
        "C1", "integrity test", EvidenceIntent.SCREENING, feed, reg,
        ModelRequest("L1", "explicit", None), ["conversion"]
    )


class ScientificIntegrityTests(unittest.TestCase):
    def test_isothermal_first_order_identity(self):
        r = ArrheniusReaction(A_per_s=2.0, E_J_per_mol=0.0)
        expected = 1.0-math.exp(-1.0)
        self.assertAlmostEqual(first_order_isothermal_conversion(r,500.0,0.5),expected,places=14)

    def test_linear_ramp_against_high_accuracy_reference(self):
        cases = [
            (1e3,70e3,300.0,850.0,10.0),
            (1e4,80e3,300.0,900.0,20.0),
            (1e5,100e3,350.0,1000.0,50.0),
        ]
        for A,E,T0,T1,beta in cases:
            ref=simpson_reference(A,E,T0,T1,beta)
            pred=first_order_linear_ramp(ArrheniusReaction(A,E),T0,T1,beta,dt_s=0.02)[-1][2]
            self.assertLess(abs(pred-ref),2e-8)

    def test_rk4_convergence_is_consistent_with_fourth_order(self):
        r=ArrheniusReaction(1e4,80e3)
        ref=simpson_reference(1e4,80e3,300.0,900.0,20.0,n=50000)
        e1=abs(first_order_linear_ramp(r,300,900,20,1.0)[-1][2]-ref)
        e2=abs(first_order_linear_ramp(r,300,900,20,0.5)[-1][2]-ref)
        e3=abs(first_order_linear_ramp(r,300,900,20,0.25)[-1][2]-ref)
        self.assertGreater(e1/e2,8.0)
        self.assertGreater(e2/e3,8.0)

    def test_parallel_model_matches_weighted_reference(self):
        reactions=[
            ArrheniusReaction(1e3,60e3,0.2),
            ArrheniusReaction(1e4,80e3,0.5),
            ArrheniusReaction(1e5,100e3,0.3),
        ]
        pred=independent_parallel_conversion(reactions,300,900,20,dt_s=0.02)[-1][2]
        ref=sum(r.weight*simpson_reference(r.A_per_s,r.E_J_per_mol,300,900,20) for r in reactions)
        self.assertLess(abs(pred-ref),2e-8)

    def test_stable_sfor_matches_inherited_equation_where_rk4_is_stable(self):
        for Tend in [600.0,650.0,700.0]:
            stable=stable_sfor_linear_ramp(303.0,Tend,5.0/60.0,"cellulose","tga",dT_K=0.02)[-1][2]
            inherited=sfor_linear_ramp(303.0,Tend,5.0/60.0,"cellulose","tga",dt_s=0.02)[-1][2]
            self.assertLess(abs(stable-inherited),5e-6)

    def test_stable_sfor_full_tga_converges(self):
        vals=[]
        for dT in [0.2,0.1,0.05,0.02]:
            y=stable_sfor_linear_ramp(303.0,1173.0,5.0/60.0,"cellulose","tga",dT_K=dT)[-1][2]
            self.assertTrue(0.0<y<1.0)
            vals.append(y)
        self.assertLess(abs(vals[-1]-vals[-2]),2e-7)

    def test_complete_dry_composition_closure_is_enforced(self):
        block=CompositionBlock(
            Basis.DRY,QualityStatus.ASSUMED,
            {"volatile_matter":0.70,"fixed_carbon":0.20,"ash":0.05},True
        )
        with self.assertRaises(IntegrityError):
            validate_composition_block(block,"proximate_analysis")

    def test_dry_basis_nonzero_moisture_is_rejected(self):
        block=CompositionBlock(
            Basis.DRY,QualityStatus.ASSUMED,
            {"volatile_matter":0.70,"fixed_carbon":0.20,"ash":0.05,"moisture":0.05},True
        )
        with self.assertRaises(IntegrityError):
            validate_composition_block(block,"proximate_analysis")

    def test_atmosphere_closure_is_enforced(self):
        case=simple_case()
        bad=RegimePassport(case.regime.thermal_program,101325.0,AtmosphereClass.INERT,{"N2":0.9})
        bad_case=StudyCase(case.case_id,case.purpose,case.evidence_intent,case.feedstock,bad,case.model_request,case.outputs_requested)
        with self.assertRaises(IntegrityError):
            validate_study_case(bad_case)

    def test_sfor_rejects_non_inert_execution(self):
        case=simple_case(AtmosphereClass.CO2_CONTAINING)
        with self.assertRaises(AdapterDomainError):
            adapter_for("SFOR_RWTH").run(case,{"component":"cellulose","regime":"tga"})

    def test_randomized_mass_and_element_ledgers_close(self):
        rng=random.Random(20260827)
        for _ in range(100):
            vals=[rng.random() for _ in range(8)]
            total=sum(vals)
            vals=[v/total for v in vals]
            p=ProductState(
                organic_char_kg=vals[0],inorganic_residue_kg=vals[1],unresolved_solid_kg=vals[2],
                organic_condensables_kg=vals[3],water_kg=vals[4],heavy_tar_kg=vals[5],
                unresolved_gas_kg=vals[6],unresolved_total_kg=vals[7],
            )
            self.assertLess(abs(MassLedger.from_product_state(1.0,p).closure_residual),1e-12)
        for _ in range(50):
            inp={e:rng.random() for e in ["C","H","O","N","S","Cl"]}
            self.assertLess(ElementLedger.from_totals(inp,dict(inp)).max_abs_residual(),1e-15)

    def test_generic_first_order_utility_never_claims_validation(self):
        result=FirstOrderScreeningModel(ArrheniusReaction(2.0,0.0)).run(simple_case())
        self.assertEqual(result.evidence_passport.evidence_status.value,"screening")

    def test_source_tree_has_no_generated_example_results(self):
        self.assertEqual(list((ROOT/"examples").glob("*_result.json")),[])


if __name__=="__main__":
    unittest.main()
