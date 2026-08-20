from salus.services.workout.progression import suggest_linear_weight


def test_linear_increases_on_success():
    assert suggest_linear_weight(
        last_weight=60.0, target_reps=8, target_rpe=8.0,
        last_reps=8, last_rpe=7.0, increment=2.5,
    ) == 62.5


def test_linear_holds_on_missed_reps():
    assert suggest_linear_weight(
        last_weight=60.0, target_reps=8, target_rpe=8.0,
        last_reps=6, last_rpe=7.0, increment=2.5,
    ) == 60.0


def test_linear_holds_on_excessive_rpe():
    assert suggest_linear_weight(
        last_weight=60.0, target_reps=8, target_rpe=8.0,
        last_reps=8, last_rpe=9.5, increment=2.5,
    ) == 60.0


def test_linear_missing_rpe_counts_as_success():
    assert suggest_linear_weight(
        last_weight=60.0, target_reps=8, target_rpe=8.0,
        last_reps=8, last_rpe=None, increment=2.5,
    ) == 62.5


def test_linear_no_history_returns_none():
    assert suggest_linear_weight(
        last_weight=None, target_reps=8, target_rpe=8.0,
        last_reps=None, last_rpe=None, increment=2.5,
    ) is None


def test_linear_no_performance_holds_weight():
    assert suggest_linear_weight(
        last_weight=60.0, target_reps=8, target_rpe=8.0,
        last_reps=None, last_rpe=None, increment=2.5,
    ) == 60.0
