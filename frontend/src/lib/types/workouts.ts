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
