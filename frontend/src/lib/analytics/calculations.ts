/* ── Sleep stage mapping ── */

const SLEEP_STAGE_MAP: Record<string, string> = {
  '1': 'Awake',
  '4': 'Light',
  '5': 'Deep',
  '6': 'REM'
};

export function mapSleepStage(code: string): string {
  return SLEEP_STAGE_MAP[code] ?? `Stage ${code}`;
}

/* ── Exercise type mapping ── */

const EXERCISE_TYPE_MAP: Record<number, string> = {
  0: 'Other Workout',
  2: 'Badminton',
  4: 'Baseball',
  5: 'Basketball',
  8: 'Cycling',
  9: 'Cycling (Stationary)',
  10: 'Boot Camp',
  11: 'Boxing',
  13: 'Calisthenics',
  14: 'Cricket',
  16: 'Dancing',
  25: 'Elliptical',
  26: 'Fitness Class',
  27: 'Fencing',
  28: 'Football (American)',
  29: 'Football (Australian)',
  31: 'Frisbee',
  32: 'Golf',
  33: 'Guided Breathing',
  34: 'Gymnastics',
  35: 'Handball',
  36: 'HIIT',
  37: 'Hiking',
  38: 'Ice Hockey',
  39: 'Ice Skating',
  44: 'Martial Arts',
  46: 'Paddling',
  47: 'Paragliding',
  48: 'Pilates',
  50: 'Racquetball',
  51: 'Rock Climbing',
  52: 'Roller Hockey',
  53: 'Rowing',
  54: 'Rowing Machine',
  55: 'Rugby',
  56: 'Running',
  57: 'Running (Treadmill)',
  58: 'Sailing',
  59: 'Scuba Diving',
  60: 'Skating',
  61: 'Skiing',
  62: 'Snowboarding',
  63: 'Snowshoeing',
  64: 'Soccer',
  65: 'Softball',
  66: 'Squash',
  68: 'Stair Climbing',
  69: 'Stair Climbing (Machine)',
  70: 'Strength Training',
  71: 'Stretching',
  72: 'Surfing',
  73: 'Swimming (Open Water)',
  74: 'Swimming (Pool)',
  75: 'Table Tennis',
  76: 'Tennis',
  78: 'Volleyball',
  79: 'Walking',
  80: 'Water Polo',
  81: 'Weightlifting',
  82: 'Wheelchair',
  83: 'Yoga'
};

export function mapExerciseType(code: number): string {
  return EXERCISE_TYPE_MAP[code] ?? `Activity ${code}`;
}

/* ── BMR via Cunningham formula ── */

export function calcBmrCunningham(weightKg: number, bodyFatPct?: number | null): number {
  if (bodyFatPct != null && bodyFatPct >= 0 && bodyFatPct < 1) {
    const lbm = weightKg * (1.0 - bodyFatPct);
    return Math.round((500 + 22.0 * lbm) * 10) / 10;
  }
  // Mifflin-St Jeor fallback (male, 30yo, 181cm)
  return Math.round((10 * weightKg + 6.25 * 181 - 5 * 30 + 5) * 10) / 10;
}

/* ── Thermic effect of food ── */

export function calcTef(proteinG: number, carbsG: number, fatG: number): number {
  return Math.round((proteinG * 4 * 0.25 + carbsG * 4 * 0.06 + fatG * 9 * 0.02) * 10) / 10;
}

/* ── TDEE ── */

export function calcTdee(
  bmr: number,
  hrAvgAwake: number,
  hrResting: number,
  age: number = 30,
  tef: number = 0,
  calibrationFactor: number = 1.5
): { tdeeKcal: number; palFactor: number; hrrPct: number } | null {
  const hrMax = 208 - 0.7 * age;
  if (hrMax <= hrResting) return null;

  let hrrPct = (hrAvgAwake - hrResting) / (hrMax - hrResting);
  hrrPct = Math.max(0.05, Math.min(0.85, hrrPct));

  const pal = Math.max(1.0, Math.min(2.5, 1.0 + hrrPct * calibrationFactor));
  const tdee = Math.round(bmr * pal + tef);

  return {
    tdeeKcal: tdee,
    palFactor: Math.round(pal * 1000) / 1000,
    hrrPct: Math.round(hrrPct * 1000) / 1000
  };
}

/* ── Goal progress ── */

export type GoalDirection = 'INCREASE' | 'DECREASE';
export type GoalFrequency = 'DAILY' | 'WEEKLY' | 'ONCE';
export type GoalStatus = 'fulfilled' | 'pending' | 'missed';

export function computeGoalProgress(
  currentValue: number | null,
  targetValue: number,
  direction: GoalDirection,
  frequency: GoalFrequency,
  deadlinePassed: boolean = false
): { percent: number; status: GoalStatus; isFulfilled: boolean } {
  if (currentValue == null) {
    return { percent: 0, status: 'pending', isFulfilled: false };
  }

  const fulfilled =
    direction === 'INCREASE' ? currentValue >= targetValue : currentValue <= targetValue;

  if (fulfilled) {
    return { percent: 100, status: 'fulfilled', isFulfilled: true };
  }

  let percent: number;
  if (direction === 'INCREASE') {
    percent = Math.min(Math.floor((currentValue / targetValue) * 100), 100);
  } else {
    if (currentValue <= targetValue) {
      percent = 100;
    } else {
      percent = Math.max(0, Math.floor((targetValue / currentValue) * 100));
    }
  }

  if (frequency === 'ONCE' && deadlinePassed) {
    return { percent, status: 'missed', isFulfilled: false };
  }

  return { percent, status: 'pending', isFulfilled: false };
}

/* ── Epley formula for estimated 1RM ── */

export function epley1Rm(weight: number, reps: number): number {
  if (reps <= 0) return weight;
  return Math.round((weight / (1.0278 - 0.0278 * reps)) * 100) / 100;
}
