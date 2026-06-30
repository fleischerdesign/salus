from salus.services.analytics.calculations import (
    calc_bmr_cunningham,
    calc_tef,
    calc_tdee,
    map_exercise_type,
    map_sleep_stage,
    day_boundary,
)


class TestSleepStageMapping:
    def test_maps_known_stages(self):
        assert map_sleep_stage("1") == "Awake"
        assert map_sleep_stage("4") == "Light"
        assert map_sleep_stage("5") == "Deep"
        assert map_sleep_stage("6") == "REM"

    def test_unknown_stage_returns_generic(self):
        assert map_sleep_stage("99") == "Stage 99"


class TestExerciseTypeMapping:
    def test_maps_known_exercises(self):
        assert map_exercise_type(56) == "Running"
        assert map_exercise_type(0) == "Other Workout"
        assert map_exercise_type(10) == "Boot Camp"

    def test_unknown_exercise_returns_generic(self):
        assert map_exercise_type(999) == "Activity 999"


class TestBMRCalculation:
    def test_cunningham_with_body_fat(self):
        bmr = calc_bmr_cunningham(80.5, 0.20)
        assert 1800 < bmr < 2200

    def test_mifflin_fallback_without_body_fat(self):
        bmr = calc_bmr_cunningham(80.5)
        assert bmr > 0

    def test_cunningham_zero_body_fat(self):
        bmr = calc_bmr_cunningham(80.5, 0.0)
        assert 2200 < bmr < 2300


class TestTEFCalculation:
    def test_tef_with_macros(self):
        tef = calc_tef(protein_g=150, carbs_g=250, fat_g=70)
        assert tef > 0

    def test_tef_zero_for_no_macros(self):
        tef = calc_tef(0, 0, 0)
        assert tef == 0


class TestTDEECalculation:
    def test_tdee_with_valid_inputs(self):
        result = calc_tdee(bmr=1900, hr_avg_awake=75, hr_resting=60, tef=200)
        assert result is not None
        tdee, pal, hrr = result
        assert tdee > 1900
        assert pal > 1.0
        assert 0 < hrr < 1

    def test_tdee_returns_none_for_invalid(self):
        result = calc_tdee(bmr=0, hr_avg_awake=75, hr_resting=60)
        assert result is None

    def test_hrr_clamped(self):
        result = calc_tdee(bmr=1900, hr_avg_awake=200, hr_resting=60)
        assert result is not None
        _, _, hrr = result
        assert hrr <= 0.85


class TestDayBoundary:
    def test_returns_22_00_boundary(self):
        start, end = day_boundary("2026-06-24")
        assert start == "2026-06-23T22:00:01"
        assert end == "2026-06-24T22:00:01"
