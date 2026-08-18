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
  | 'Gesäß';

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

export interface LiveWorkoutExercise {
  id: string;
  name: string;
  muscleGroup: MuscleGroup;
  category: ExerciseCategory;
  equipment: EquipmentType;
  sets: LiveWorkoutSet[];
  notes?: string;
  supersetGroup?: string; // e.g. 'A1', 'A2'
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

export interface WorkoutHistorySession {
  id: string;
  date: string;
  planName: string;
  duration: string;
  durationMinutes: number;
  tonnage: string;
  tonnageKg: number;
  setsCount: number;
  prCount: number;
  prNote: string;
  avgHeartRate: number;
  activeKcal: number;
  exercises: {
    name: string;
    muscle: MuscleGroup;
    sets: { setNumber: number; weight: number; reps: number; type: SetType; rpe: number; isPR?: boolean }[];
    totalVolumeKg: number;
  }[];
}
