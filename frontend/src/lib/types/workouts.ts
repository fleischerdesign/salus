export type MuscleGroup =
  | 'Brust'
  | 'Rücken'
  | 'Quadrizeps'
  | 'Hamstrings'
  | 'Schultern'
  | 'Bizeps'
  | 'Trizeps'
  | 'Waden'
  | 'Bauch'
  | 'Gesäß'
  | 'Nacken'
  | 'Unterarme';

export const MUSCLE_GROUPS: readonly MuscleGroup[] = [
  'Brust',
  'Rücken',
  'Schultern',
  'Bizeps',
  'Trizeps',
  'Unterarme',
  'Quadrizeps',
  'Hamstrings',
  'Gesäß',
  'Waden',
  'Bauch',
  'Nacken'
] as const;

export type DetailedMuscleKey =
  | 'chest_clavicular'
  | 'chest_sternal'
  | 'deltoid_anterior'
  | 'deltoid_lateral'
  | 'deltoid_posterior'
  | 'biceps_brachii'
  | 'triceps_long'
  | 'triceps_lateral'
  | 'forearms'
  | 'trapezius_upper'
  | 'trapezius_mid_lower'
  | 'latissimus_dorsi'
  | 'erector_spinae'
  | 'rhomboids'
  | 'rectus_abdominis'
  | 'obliques'
  | 'serratus_anterior'
  | 'gluteus_maximus'
  | 'gluteus_medius'
  | 'quadriceps'
  | 'hamstrings'
  | 'adductors'
  | 'gastrocnemius'
  | 'soleus'
  | 'tibialis_anterior';

export interface DetailedMuscleDef {
  key: DetailedMuscleKey;
  name: string;
  latin: string;
  group: MuscleGroup;
  category: 'push' | 'pull' | 'legs' | 'core';
  svgPathIds: string[];
}

export const DETAILED_MUSCLES: DetailedMuscleDef[] = [
  // ── Brust / Chest ──
  {
    key: 'chest_clavicular',
    name: 'Obere Brust (Klavikulär)',
    latin: 'M. pectoralis major (pars clavicularis)',
    group: 'Brust',
    category: 'push',
    svgPathIds: ['chest-upper-left', 'chest-upper-right']
  },
  {
    key: 'chest_sternal',
    name: 'Mittlere & Untere Brust',
    latin: 'M. pectoralis major (pars sternocostalis)',
    group: 'Brust',
    category: 'push',
    svgPathIds: ['chest-lower-left', 'chest-lower-right']
  },

  // ── Schultern / Shoulders ──
  {
    key: 'deltoid_anterior',
    name: 'Vordere Schulter',
    latin: 'M. deltoideus (pars clavicularis)',
    group: 'Schultern',
    category: 'push',
    svgPathIds: ['shoulder-front-left', 'shoulder-front-right']
  },
  {
    key: 'deltoid_lateral',
    name: 'Seitliche Schulter',
    latin: 'M. deltoideus (pars acromialis)',
    group: 'Schultern',
    category: 'push',
    svgPathIds: ['shoulder-side-left', 'shoulder-side-right']
  },
  {
    key: 'deltoid_posterior',
    name: 'Hintere Schulter',
    latin: 'M. deltoideus (pars spinalis)',
    group: 'Schultern',
    category: 'pull',
    svgPathIds: ['deltoid-rear-left', 'deltoid-rear-right']
  },

  // ── Rücken & Nacken / Back & Neck ──
  {
    key: 'latissimus_dorsi',
    name: 'Latissimus (Breiter Rücken)',
    latin: 'M. latissimus dorsi',
    group: 'Rücken',
    category: 'pull',
    svgPathIds: [
      'lats-upper-left',
      'lats-mid-left',
      'lats-lower-left',
      'lats-upper-right',
      'lats-mid-right',
      'lats-lower-right'
    ]
  },
  {
    key: 'trapezius_upper',
    name: 'Oberer Trapez / Nacken',
    latin: 'M. trapezius (pars descendens)',
    group: 'Nacken',
    category: 'pull',
    svgPathIds: ['traps-upper-left', 'traps-upper-right', 'neck-left', 'neck-right']
  },
  {
    key: 'trapezius_mid_lower',
    name: 'Mittlerer & Unterer Trapez',
    latin: 'M. trapezius (pars transversa & ascendens)',
    group: 'Rücken',
    category: 'pull',
    svgPathIds: ['traps-mid-left', 'traps-mid-right', 'traps-lower-left', 'traps-lower-right']
  },
  {
    key: 'erector_spinae',
    name: 'Rückenstrecker (Unterer Rücken)',
    latin: 'M. erector spinae',
    group: 'Rücken',
    category: 'core',
    svgPathIds: ['lower-back-erectors-left', 'lower-back-erectors-right', 'spine']
  },
  {
    key: 'rhomboids',
    name: 'Rautenmuskeln',
    latin: 'Mm. rhomboidei',
    group: 'Rücken',
    category: 'pull',
    svgPathIds: ['traps-mid-left', 'traps-mid-right']
  },

  // ── Arme & Unterarme / Arms & Forearms ──
  {
    key: 'biceps_brachii',
    name: 'Bizeps',
    latin: 'M. biceps brachii & M. brachialis',
    group: 'Bizeps',
    category: 'pull',
    svgPathIds: ['biceps-left', 'biceps-right']
  },
  {
    key: 'triceps_long',
    name: 'Trizeps (Langer Kopf)',
    latin: 'M. triceps brachii (caput longum)',
    group: 'Trizeps',
    category: 'push',
    svgPathIds: ['triceps-long-left', 'triceps-long-right']
  },
  {
    key: 'triceps_lateral',
    name: 'Trizeps (Lateraler / Medialer Kopf)',
    latin: 'M. triceps brachii (caput laterale & mediale)',
    group: 'Trizeps',
    category: 'push',
    svgPathIds: ['triceps-lateral-left', 'triceps-lateral-right']
  },
  {
    key: 'forearms',
    name: 'Unterarme (Beuger & Strecker)',
    latin: 'Mm. antebrachii',
    group: 'Unterarme',
    category: 'pull',
    svgPathIds: [
      'forearm-left',
      'forearm-right',
      'forearm-flexors-left',
      'forearm-extensors-left',
      'forearm-flexors-right',
      'forearm-extensors-right'
    ]
  },

  // ── Beine / Legs & Glutes ──
  {
    key: 'quadriceps',
    name: 'Quadrizeps (Beinstrecker)',
    latin: 'M. quadriceps femoris',
    group: 'Quadrizeps',
    category: 'legs',
    svgPathIds: ['quads-left', 'quads-right', 'knee-left', 'knee-right']
  },
  {
    key: 'hamstrings',
    name: 'Hamstrings (Beinbeuger)',
    latin: 'Mm. ischiocrurales',
    group: 'Hamstrings',
    category: 'legs',
    svgPathIds: [
      'hamstrings-medial-left',
      'hamstrings-lateral-left',
      'hamstrings-medial-right',
      'hamstrings-lateral-right'
    ]
  },
  {
    key: 'gluteus_maximus',
    name: 'Großer Gesäßmuskel',
    latin: 'M. gluteus maximus',
    group: 'Gesäß',
    category: 'legs',
    svgPathIds: ['gluteus-maximus-left', 'gluteus-maximus-right']
  },
  {
    key: 'gluteus_medius',
    name: 'Mittlerer Gesäßmuskel / Abduktoren',
    latin: 'M. gluteus medius & minimus',
    group: 'Gesäß',
    category: 'legs',
    svgPathIds: ['gluteus-medius-left', 'gluteus-medius-right']
  },
  {
    key: 'adductors',
    name: 'Adduktoren (Innenschenkel)',
    latin: 'Mm. adductores',
    group: 'Quadrizeps',
    category: 'legs',
    svgPathIds: ['adductors-left', 'adductors-right']
  },
  {
    key: 'gastrocnemius',
    name: 'Zwillingswadenmuskel (Waden)',
    latin: 'M. gastrocnemius',
    group: 'Waden',
    category: 'legs',
    svgPathIds: [
      'calves-gastroc-medial-left',
      'calves-gastroc-lateral-left',
      'calves-gastroc-medial-right',
      'calves-gastroc-lateral-right'
    ]
  },
  {
    key: 'soleus',
    name: 'Schollenmuskel (Tiefe Wade)',
    latin: 'M. soleus',
    group: 'Waden',
    category: 'legs',
    svgPathIds: ['calves-soleus-left', 'calves-soleus-right']
  },
  {
    key: 'tibialis_anterior',
    name: 'Schienbeinmuskel',
    latin: 'M. tibialis anterior',
    group: 'Waden',
    category: 'legs',
    svgPathIds: ['tibialis-anterior-left', 'tibialis-anterior-right']
  },

  // ── Bauch & Rumpf / Core ──
  {
    key: 'rectus_abdominis',
    name: 'Gerade Bauchmuskeln (Sixpack)',
    latin: 'M. rectus abdominis',
    group: 'Bauch',
    category: 'core',
    svgPathIds: ['abs-upper-left', 'abs-upper-right', 'abs-lower-left', 'abs-lower-right']
  },
  {
    key: 'obliques',
    name: 'Schräge Bauchmuskeln',
    latin: 'Mm. obliqui abdominis',
    group: 'Bauch',
    category: 'core',
    svgPathIds: ['obliques-left', 'obliques-right']
  },
  {
    key: 'serratus_anterior',
    name: 'Vorderer Sägemuskel',
    latin: 'M. serratus anterior',
    group: 'Bauch',
    category: 'core',
    svgPathIds: ['serratus-anterior-left', 'serratus-anterior-right']
  }
];

export const DETAILED_MUSCLE_MAP: Record<DetailedMuscleKey, DetailedMuscleDef> = Object.fromEntries(
  DETAILED_MUSCLES.map((m) => [m.key, m])
) as Record<DetailedMuscleKey, DetailedMuscleDef>;

export const TIER2_TO_TIER1: Record<DetailedMuscleKey, MuscleGroup> = Object.fromEntries(
  DETAILED_MUSCLES.map((m) => [m.key, m.group])
) as Record<DetailedMuscleKey, MuscleGroup>;

/**
 * Splits a comma-separated muscle string into clean, trimmed tokens.
 */
export function parseMuscles(str: string | null | undefined): string[] {
  if (!str) return [];
  return str
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
}

/**
 * Resolves any muscle key, German name, or old label to its parent high-level MuscleGroup.
 */
export function resolveMuscleGroup(muscleKeyOrName: string): MuscleGroup {
  const trimmed = muscleKeyOrName.trim();
  if (trimmed in DETAILED_MUSCLE_MAP) {
    return DETAILED_MUSCLE_MAP[trimmed as DetailedMuscleKey].group;
  }
  const byName = DETAILED_MUSCLES.find(
    (m) =>
      m.name.toLowerCase() === trimmed.toLowerCase() ||
      m.latin.toLowerCase() === trimmed.toLowerCase()
  );
  if (byName) return byName.group;

  if (MUSCLE_GROUPS.includes(trimmed as MuscleGroup)) {
    return trimmed as MuscleGroup;
  }

  // Fallbacks for common variations
  const lower = trimmed.toLowerCase();
  if (lower.includes('brust') || lower.includes('chest')) return 'Brust';
  if (lower.includes('rück') || lower.includes('back') || lower.includes('lat')) return 'Rücken';
  if (lower.includes('schulter') || lower.includes('delt')) return 'Schultern';
  if (lower.includes('bizeps') || lower.includes('bicep')) return 'Bizeps';
  if (lower.includes('trizeps') || lower.includes('tricep')) return 'Trizeps';
  if (lower.includes('quad') || lower.includes('bein') || lower.includes('schenkel'))
    return 'Quadrizeps';
  if (lower.includes('hamstring') || lower.includes('beuger')) return 'Hamstrings';
  if (lower.includes('wade') || lower.includes('calf')) return 'Waden';
  if (lower.includes('bauch') || lower.includes('ab') || lower.includes('core')) return 'Bauch';
  if (lower.includes('gesäß') || lower.includes('glute') || lower.includes('po')) return 'Gesäß';
  if (lower.includes('nacken') || lower.includes('trap') || lower.includes('neck')) return 'Nacken';
  if (lower.includes('unterarm') || lower.includes('forearm')) return 'Unterarme';

  return 'Brust';
}

export type ExerciseCategory = 'Grundübung' | 'Hypertrophie' | 'Isolationsübung' | 'Bodyweight';
export type EquipmentType = 'Langhantel' | 'Kurzhantel' | 'Kabelzug' | 'Maschine' | 'Eigengewicht';
export type SetType = 'warmup' | 'normal' | 'drop' | 'failure';

export interface LiveWorkoutSet {
  id: string;
  setNumber: number;
  type: SetType;
  previous: { weightKg: number; reps: number; rpe?: string };
  weightKg: number;
  reps: number;
  rpe: number; // 6.0 - 10.0
  completed: boolean;
  isPR?: boolean;
}

export type WorkoutSet = LiveWorkoutSet;

export interface LiveWorkoutExercise {
  id: string;
  exerciseId?: string;
  name: string;
  muscleGroup: MuscleGroup;
  category: ExerciseCategory;
  equipment: EquipmentType;
  sets: LiveWorkoutSet[];
  notes?: string;
  supersetGroup?: string;
  e1RM: number;
}

export interface WorkoutPlan {
  id: string;
  name: string;
  split: string;
  subtitle: string;
  estimatedDuration: string;
  targetVolume: string;
  targetVolumeKg: number;
  exercisesCount: number;
  exercises: {
    name: string;
    muscle: MuscleGroup;
    targetSets: number;
    targetReps: string;
    targetRir: number;
  }[];
}

export interface WorkoutHistorySet {
  setNumber?: number;
  set?: number;
  weight?: number;
  weightKg?: number;
  reps: number;
  type?: SetType | string;
  rpe?: number | string;
  isPR?: boolean;
}

export interface WorkoutHistoryExercise {
  name: string;
  muscle?: MuscleGroup | string;
  bestSet?: string;
  volume?: string;
  totalVolumeKg?: number;
  sets?: WorkoutHistorySet[];
}

export interface WorkoutHistorySession {
  id: string;
  date: string;
  name?: string;
  planName?: string;
  duration?: string;
  durationMinutes?: number;
  avgHeartRate?: number;
  activeKcal?: number;
  tonnage?: string;
  tonnageKg?: number;
  totalVolumeKg?: number;
  setsCount?: number;
  totalSets?: number;
  prCount?: number;
  prsCount?: number;
  prNote?: string;
  exercises?: WorkoutHistoryExercise[];
}
