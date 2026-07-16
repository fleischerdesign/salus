import math
import os
import sys

import yaml

import salus.services.analytics.stats as ks
from salus.services.analytics.stats import _dataclasses as dt


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "stats")


def _load_fixture(name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, name)
    if not os.path.exists(path):
        pytest.skip(f"fixture {name} not found")
    with open(path) as f:
        return yaml.safe_load(f)


class TestLinearRegression:
    def test_golden(self) -> None:
        fx = _load_fixture("linear_regression.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        reg = ks.linear_regression(inp["xs"], inp["ys"])
        assert reg is not None
        assert math.isclose(reg.slope, exp["slope"], rel_tol=1e-4)
        assert math.isclose(reg.intercept, exp["intercept"], rel_tol=1e-4)
        assert math.isclose(reg.r_squared, exp["r_squared"], rel_tol=1e-4)
        assert math.isclose(reg.standard_error, exp["standard_error"], rel_tol=1e-4)
        assert reg.n == exp["n"]


class TestPearson:
    def test_golden(self) -> None:
        fx = _load_fixture("pearson.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        c = ks.pearson(inp["xs"], inp["ys"])
        assert c is not None
        assert math.isclose(c.r, exp["r"], rel_tol=1e-6)
        assert math.isclose(c.t_statistic, exp["t_statistic"], rel_tol=1e-4)
        assert math.isclose(c.p_value, exp["p_value"], abs_tol=1e-3)
        assert math.isclose(c.ci_lower, exp["ci_lower"], abs_tol=1e-4)
        assert math.isclose(c.ci_upper, exp["ci_upper"], abs_tol=1e-4)
        assert c.n == exp["n"]


class TestSpearman:
    def test_golden(self) -> None:
        fx = _load_fixture("spearman.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        c = ks.spearman(inp["xs"], inp["ys"])
        assert math.isclose(c.r, exp["r"], rel_tol=1e-6)
        assert c.n == exp["n"]


class TestBenjaminiHochberg:
    def test_golden(self) -> None:
        fx = _load_fixture("benjamini_hochberg.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        result = ks.benjamini_hochberg(inp["p_values"], alpha=inp.get("alpha", 0.05))
        assert len(result.adjusted) == len(exp["adjusted"])
        for got, want in zip(result.adjusted, exp["adjusted"]):
            assert math.isclose(got, want, rel_tol=1e-6)
        expected_rejected = [adj <= inp["alpha"] for adj in result.adjusted]
        assert list(result.rejected) == expected_rejected


class TestMannKendall:
    def test_golden(self) -> None:
        fx = _load_fixture("mann_kendall.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        mk = ks.mann_kendall(inp["series"])
        assert mk is not None
        assert math.isclose(mk.s, exp["s"], abs_tol=0.01)
        assert math.isclose(mk.z, exp["z"], rel_tol=1e-4)
        assert math.isclose(mk.p_value, exp["p_value"], abs_tol=1e-3)
        assert mk.trend == exp["trend"]
        assert math.isclose(mk.tau, exp["tau"], rel_tol=1e-6)


class TestBootstrapCI:
    def test_golden(self) -> None:
        fx = _load_fixture("bootstrap_ci.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        bc = ks.bootstrap_ci(
            inp["xs"],
            ks.mean,
            n_iter=inp["n_iter"],
            seed=inp["seed"],
            confidence=inp["confidence"],
        )
        assert bc is not None
        assert math.isclose(bc.point_estimate, exp["point_estimate"], rel_tol=1e-6)
        assert bc.n_iter == exp["n_iter"]


class TestPredictionInterval:
    def test_golden(self) -> None:
        fx = _load_fixture("prediction_interval.yaml")
        inp = fx["input"]
        reg = ks.linear_regression(inp["xs"], inp["ys"])
        assert reg is not None
        pi = ks.prediction_interval(reg, inp["x_new"], inp["confidence"])
        assert pi is not None
        assert math.isclose(pi.point_estimate, fx["expected"]["point_estimate"], rel_tol=1e-4)
        assert pi.lower <= pi.point_estimate <= pi.upper


class TestCohensD:
    def test_golden(self) -> None:
        fx = _load_fixture("cohens_d_paired.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        es = ks.cohens_d_paired(inp["x"], inp["y"])
        assert es is not None
        assert math.isclose(es.d, exp["d"], rel_tol=1e-4)
        assert math.isclose(es.hedges_g, exp["hedges_g"], rel_tol=1e-4)
        assert es.interpretation == exp["interpretation"]


class TestEWMA:
    def test_golden(self) -> None:
        fx = _load_fixture("ewma_forecast.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        fc = ks.ewma_forecast(inp["series"], inp["alpha"], inp["horizon"])
        assert fc is not None
        assert fc.n_train == exp["n_train"]


class TestMAPE:
    def test_golden(self) -> None:
        fx = _load_fixture("mape.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        m = ks.mape(inp["y_true"], inp["y_pred"])
        assert m is not None
        assert math.isclose(m, exp["mape"], rel_tol=1e-6)


class TestSleepEfficiency:
    def test_golden(self) -> None:
        fx = _load_fixture("sleep_efficiency.yaml")
        inp = fx["input"]
        exp = inp["expected"]
        cases = inp["test_cases"]
        eff = ks.sleep_efficiency(cases[0]["tst_min"], cases[0]["tib_min"])
        assert math.isclose(eff.efficiency, exp["efficiency_0"], rel_tol=1e-6)
        eff0 = ks.sleep_efficiency(0, 0)
        assert eff0.efficiency == 0.0
        assert eff0.warning == "TIB was zero"


class TestSleepDebt:
    def test_golden(self) -> None:
        fx = _load_fixture("sleep_debt_cumulative.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        sd = ks.sleep_debt_cumulative(inp["durations_h"], inp["age_y"])
        assert math.isclose(sd.baseline_h, exp["baseline_h"])
        assert math.isclose(sd.debt[6], exp["debt_7d"], rel_tol=1e-6)
        assert math.isclose(sd.debt[-1], exp["debt_14d"], rel_tol=1e-6)


class TestHRV:
    def test_golden(self) -> None:
        fx = _load_fixture("hrv_time_domain.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        hrv = ks.hrv_time_domain(inp["rr_intervals_ms"])
        assert hrv is not None
        assert math.isclose(hrv.mean_rr, exp["mean_rr"], rel_tol=1e-4)
        assert math.isclose(hrv.sdnn, exp["sdnn"], rel_tol=1e-4)
        assert math.isclose(hrv.rmssd, exp["rmssd"], rel_tol=1e-4)
        assert math.isclose(hrv.pnn50, exp["pnn50"], rel_tol=1e-4)


class TestBMRCunningham:
    def test_golden(self) -> None:
        fx = _load_fixture("bmr_cunningham.yaml")
        inp = fx["input"]
        cases = inp["test_cases"]
        bmr = ks.bmr_cunningham(cases[0]["weight_kg"], cases[0]["body_fat_pct"])
        assert bmr is not None
        assert bmr == inp["expected"]["bmr_0"]
        assert ks.bmr_cunningham(cases[1]["weight_kg"], cases[1]["body_fat_pct"]) is None


class TestBMRMifflin:
    def test_golden(self) -> None:
        fx = _load_fixture("bmr_mifflin_st_jeor.yaml")
        inp = fx["input"]
        cases = inp["test_cases"]
        bmr_m = ks.bmr_mifflin_st_jeor(cases[0]["weight_kg"], cases[0]["height_cm"], cases[0]["age_y"], cases[0]["sex"])
        assert bmr_m == inp["expected"]["bmr_male"]
        bmr_null = ks.bmr_mifflin_st_jeor(cases[2]["weight_kg"], cases[2]["height_cm"], cases[2]["age_y"], cases[2]["sex"])
        assert bmr_null == inp["expected"]["bmr_null"]


class TestHRMax:
    def test_golden(self) -> None:
        fx = _load_fixture("hr_max_tanaka.yaml")
        inp = fx["input"]
        cases = inp["test_cases"]
        assert ks.hr_max_tanaka(cases[0]["age_y"]) == inp["expected"]["hr_30"]


class TestHRRPct:
    def test_golden(self) -> None:
        fx = _load_fixture("hrr_pct.yaml")
        inp = fx["input"]
        cases = inp["test_cases"]
        assert math.isclose(
            ks.hrr_pct(120, 60, 190), cases[0]["expected"], abs_tol=1e-5
        )
        assert ks.hrr_pct(200, 60, 190) == cases[1]["expected"]


class TestPAL:
    def test_golden(self) -> None:
        fx = _load_fixture("pal_from_hrr.yaml")
        inp = fx["input"]
        assert math.isclose(ks.pal_from_hrr(0.5, 1.5), inp["expected"]["normal"], rel_tol=1e-6)


class TestTEF:
    def test_golden(self) -> None:
        fx = _load_fixture("tef_from_macros.yaml")
        inp = fx["input"]
        assert math.isclose(ks.tef_from_macros(inp["protein_g"], inp["carbs_g"], inp["fat_g"]), fx["expected"]["tef"], rel_tol=1e-6)


class TestTDEE:
    def test_golden(self) -> None:
        fx = _load_fixture("tdee.yaml")
        inp = fx["input"]
        assert ks.tdee(inp["bmr"], inp["pal"], inp["tef"]) == fx["expected"]["tdee"]


class TestEpley:
    def test_golden(self) -> None:
        fx = _load_fixture("epley_1rm.yaml")
        inp = fx["input"]
        assert math.isclose(ks.epley_1rm(100, 5), inp["expected"]["rm_100x5"], rel_tol=1e-6)


class TestBrzycki:
    def test_golden(self) -> None:
        fx = _load_fixture("brzycki_1rm.yaml")
        inp = fx["input"]
        assert math.isclose(ks.brzycki_1rm(100, 5) or 0, inp["expected"]["rm_100x5"], rel_tol=1e-6)
        assert ks.brzycki_1rm(80, 12) is None


class TestInternalErf:
    def test_golden(self) -> None:
        fx = _load_fixture("internal_erf.yaml")
        inp = fx["input"]
        exp = inp["expected"]
        assert math.isclose(ks.erf(0.0), exp["erf_0"], abs_tol=1.5e-7)
        assert math.isclose(ks.erf(0.5), exp["erf_0_5"], abs_tol=1.5e-7)
        assert math.isclose(ks.erf(1.0), exp["erf_1"], abs_tol=1.5e-7)
        assert math.isclose(ks.erf(2.0), exp["erf_2"], abs_tol=1.5e-7)


class TestInternalNormalCDF:
    def test_golden(self) -> None:
        fx = _load_fixture("internal_normal_cdf.yaml")
        inp = fx["input"]
        exp = inp["expected"]
        assert math.isclose(ks.normal_cdf(0.0), exp["phi_0"], abs_tol=1e-4)
        assert math.isclose(ks.normal_cdf(1.96), exp["phi_1_96"], abs_tol=1e-4)


class TestInternalQuantile:
    def test_golden(self) -> None:
        fx = _load_fixture("internal_quantile.yaml")
        inp = fx["input"]
        exp = fx["expected"]
        q = ks.quantile(inp["xs"], inp["p"])
        assert q is not None
        assert math.isclose(q, exp["median"], rel_tol=1e-6)
