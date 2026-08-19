import type { Component } from 'svelte';
import HeroRingsWidget from '$components/dashboard/widgets/HeroRingsWidget.svelte';
import BloodPressureWidget from '$components/dashboard/widgets/BloodPressureWidget.svelte';
import RestingHeartRateWidget from '$components/dashboard/widgets/RestingHeartRateWidget.svelte';
import SleepHypnogramWidget from '$components/dashboard/widgets/SleepHypnogramWidget.svelte';
import HabitCheckPillsWidget from '$components/dashboard/widgets/HabitCheckPillsWidget.svelte';
import MedicationDoseWidget from '$components/dashboard/widgets/MedicationDoseWidget.svelte';
import HydrationGlassWidget from '$components/dashboard/widgets/HydrationGlassWidget.svelte';
import MetabolicClockWidget from '$components/dashboard/widgets/MetabolicClockWidget.svelte';
import CircadianArcWidget from '$components/dashboard/widgets/CircadianArcWidget.svelte';
import Spo2Widget from '$components/dashboard/widgets/Spo2Widget.svelte';
import BloodGlucoseWidget from '$components/dashboard/widgets/BloodGlucoseWidget.svelte';
import Vo2MaxWidget from '$components/dashboard/widgets/Vo2MaxWidget.svelte';
import HrvWidget from '$components/dashboard/widgets/HrvWidget.svelte';
import HabitYearMatrixWidget from '$components/dashboard/widgets/HabitYearMatrixWidget.svelte';
import MoodValenceWidget from '$components/dashboard/widgets/MoodValenceWidget.svelte';

export interface WidgetContextProps {
  date?: string;
  config?: Record<string, unknown>;
  preview?: boolean;
  onopen?: (route: string) => void;
}

export interface WidgetManifest {
  type: string;
  title: string;
  subtitle?: string;
  description: string;
  category: 'vitals' | 'activity' | 'sleep' | 'nutrition' | 'wellness' | 'special';
  icon: string;
  iconColor: string;
  defaultSize?: 'small' | 'medium' | 'large';
  component: Component<WidgetContextProps>;
}

const REGISTRY: Record<string, WidgetManifest> = {
  hero_rings: {
    type: 'hero_rings',
    title: 'Hero Ziel-Ringe',
    subtitle: 'Schritte, Hydratation, Gewohnheiten',
    description: 'Konzentrische Fortschrittsringe für die wichtigsten Tagesziele.',
    category: 'activity',
    icon: 'emoji-events',
    iconColor: 'var(--color-primary)',
    defaultSize: 'large',
    component: HeroRingsWidget
  },
  blood_pressure_dial: {
    type: 'blood_pressure_dial',
    title: 'Arterieller Blutdruck',
    subtitle: 'Systolisch / Diastolisch',
    description: 'Barometrische Farbskala nach europäischen ESC/ESH 2024 Leitlinien.',
    category: 'vitals',
    icon: 'vital-signs',
    iconColor: 'var(--color-vital)',
    defaultSize: 'medium',
    component: BloodPressureWidget
  },
  resting_heart_rate: {
    type: 'resting_heart_rate',
    title: 'Ruhepuls (RHR)',
    subtitle: 'Herzfrequenz in Ruhe',
    description: 'Nächtliche Baseline und Ruhepuls-Zonen für kardiovaskuläre Gesundheit.',
    category: 'vitals',
    icon: 'ecg-heart',
    iconColor: 'var(--color-vital)',
    defaultSize: 'medium',
    component: RestingHeartRateWidget
  },
  sleep_hypnogram: {
    type: 'sleep_hypnogram',
    title: 'Schlafarchitektur',
    subtitle: 'Hypnogramm & Phasen',
    description: 'Phasenanalyse von Tiefschlaf, REM und Leichtschlaf mit Erholungs-Score.',
    category: 'sleep',
    icon: 'bedtime',
    iconColor: 'var(--color-sleep)',
    defaultSize: 'large',
    component: SleepHypnogramWidget
  },
  habit_check_pills: {
    type: 'habit_check_pills',
    title: 'Tägliche Gewohnheiten',
    subtitle: 'Habit Tracker',
    description: 'Interaktive Schnellabhak-Kacheln für tägliche Routinen und Gewohnheiten.',
    category: 'wellness',
    icon: 'check',
    iconColor: 'var(--color-success)',
    defaultSize: 'medium',
    component: HabitCheckPillsWidget
  },
  medication_dose: {
    type: 'medication_dose',
    title: 'Medikamente & Dosen',
    subtitle: 'Supplement- & Einnahmeplan',
    description: 'Tägliche Einnahme-Checkliste für Nahrungsergänzungsmittel und Medikamente.',
    category: 'wellness',
    icon: 'medication',
    iconColor: 'var(--color-primary)',
    defaultSize: 'medium',
    component: MedicationDoseWidget
  },
  hydration_glass: {
    type: 'hydration_glass',
    title: 'Wasseraufnahme',
    subtitle: 'Hydratations-Pegel',
    description: 'Interaktives Wellenglas mit Schnell-Protokollierung (+250ml, +500ml).',
    category: 'nutrition',
    icon: 'water-drop',
    iconColor: 'var(--color-primary)',
    defaultSize: 'medium',
    component: HydrationGlassWidget
  },
  metabolic_clock: {
    type: 'metabolic_clock',
    title: 'Metabolische Uhr',
    subtitle: 'Intervallfasten & Phasen',
    description: 'Zirkuläre Anzeige von Ketose, Autophagie und aktuellem Fastenfenster.',
    category: 'nutrition',
    icon: 'schedule',
    iconColor: 'var(--color-fasting)',
    defaultSize: 'medium',
    component: MetabolicClockWidget
  },
  mood_sphere: {
    type: 'mood_sphere',
    title: 'Psychobiometrie (Stimmung)',
    subtitle: 'Valenz & Erregung',
    description: '2D Russell Circumplex-Modell für mentale Verfassung und Erregungszustand.',
    category: 'wellness',
    icon: 'insights',
    iconColor: 'var(--color-circadian)',
    defaultSize: 'medium',
    component: MoodValenceWidget
  },
  circadian_arc: {
    type: 'circadian_arc',
    title: 'Zirkadianer Sonnenbogen',
    subtitle: 'Biorhythmus & Melatonin',
    description: 'Realer Sonnenverlauf mit optimalen Fenstern für Licht, Koffein & Schlaf.',
    category: 'special',
    icon: 'wb-sunny',
    iconColor: 'var(--color-circadian)',
    defaultSize: 'large',
    component: CircadianArcWidget
  },
  spo2_card: {
    type: 'spo2_card',
    title: 'Blutsauerstoff (SpO2)',
    subtitle: 'Sauerstoffsättigung',
    description: 'Pulsoxymetrische Sättigung der arteriellen Gefäße während der Nacht.',
    category: 'vitals',
    icon: 'vital-signs',
    iconColor: 'var(--color-vital)',
    defaultSize: 'small',
    component: Spo2Widget
  },
  blood_glucose: {
    type: 'blood_glucose',
    title: 'Blutzucker',
    subtitle: 'Glukosespiegel',
    description: 'Nüchtern- und Postprandial-Werte zur Überwachung der Insulinsensitivität.',
    category: 'vitals',
    icon: 'science',
    iconColor: 'var(--color-vital)',
    defaultSize: 'small',
    component: BloodGlucoseWidget
  },
  vo2_max: {
    type: 'vo2_max',
    title: 'VO2max (Fitness)',
    subtitle: 'Kardiorespiratorische Kapazität',
    description: 'Indikator für Langlebigkeit und aerobe Leistungsfähigkeit.',
    category: 'activity',
    icon: 'directions-run',
    iconColor: 'var(--color-activity)',
    defaultSize: 'small',
    component: Vo2MaxWidget
  },
  hrv_card: {
    type: 'hrv_card',
    title: 'Herzfrequenzvariabilität (HRV)',
    subtitle: 'Parasympathikus / Erholung',
    description: 'rMSSD- und SDNN-Werte zur Überwachung des vegetativen Nervensystems.',
    category: 'vitals',
    icon: 'monitoring',
    iconColor: 'var(--color-vital)',
    defaultSize: 'small',
    component: HrvWidget
  },
  habit_year_matrix: {
    type: 'habit_year_matrix',
    title: 'Jahres-Konsistenz Matrix',
    subtitle: '52-Wochen Übersicht',
    description: 'GitHub-Style Heatmap aller Check-ins und Aktivitäten im Jahresverlauf.',
    category: 'wellness',
    icon: 'calendar-month',
    iconColor: 'var(--color-success)',
    defaultSize: 'large',
    component: HabitYearMatrixWidget
  }
};

export function getWidgetManifest(type: string): WidgetManifest | undefined {
  return REGISTRY[type];
}

export function getAllWidgetManifests(): WidgetManifest[] {
  return Object.values(REGISTRY);
}

export function registerWidget(manifest: WidgetManifest): void {
  REGISTRY[manifest.type] = manifest;
}
