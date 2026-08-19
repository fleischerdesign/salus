export type WidgetType = string;

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  size?: 'full' | 'half' | 'third' | 'compact';
  config?: Record<string, unknown>;
}

export interface DashboardWidgetGroup {
  id: string;
  title: string;
  subtitle?: string;
  icon?: string;
  collapsed?: boolean;
  columns: 1 | 2 | 3;
  widgets: DashboardWidget[];
}

export type DashboardItem =
  | { id: string; kind: 'widget'; widget: DashboardWidget }
  | { id: string; kind: 'group'; group: DashboardWidgetGroup };

export const DEFAULT_DASHBOARD_ITEMS: DashboardItem[] = [
  // 1. Zirkadianer 24h-Sonnenbogen
  {
    id: 'item_circadian',
    kind: 'widget',
    widget: {
      id: 'w_circadian_arc',
      type: 'circadian_arc',
      title: 'Zirkadianer 24h-Sonnenbogen',
      size: 'full'
    }
  },
  // 2. Tages-Status & Biometrische Ringe
  {
    id: 'item_hero_rings',
    kind: 'widget',
    widget: {
      id: 'w_hero_rings',
      type: 'hero_rings',
      title: 'Tages-Status & Biometrische Ringe',
      size: 'full'
    }
  },
  // 3. Gruppe: Kardiovaskuläre Vitalwerte
  {
    id: 'grp_cardio',
    kind: 'group',
    group: {
      id: 'grp_cardio',
      title: 'Kardiovaskuläres System & Zirkulation',
      subtitle: 'Blutdruck (ESC 2024), Ruhepuls und Blutsauerstoff',
      icon: 'favorite',
      collapsed: false,
      columns: 3,
      widgets: [
        { id: 'w_bp', type: 'blood_pressure_dial', title: 'Arterieller Blutdruck', size: 'third' },
        { id: 'w_rhr', type: 'resting_heart_rate', title: 'Ruhepuls (RHR)', size: 'third' },
        { id: 'w_spo2', type: 'spo2_card', title: 'Blutsauerstoff (SpO2)', size: 'third' }
      ]
    }
  },
  // 4. Gruppe: Stoffwechsel & Fasten
  {
    id: 'grp_metabolism',
    kind: 'group',
    group: {
      id: 'grp_metabolism',
      title: 'Stoffwechsel, Glukose & Fasten',
      subtitle: 'Blutzuckerspiegel, Hydratation und 16:8 Fasten-Uhr',
      icon: 'science',
      collapsed: false,
      columns: 3,
      widgets: [
        { id: 'w_glucose', type: 'blood_glucose', title: 'Blutzucker', size: 'third' },
        { id: 'w_hydration', type: 'hydration_glass', title: 'Wasseraufnahme', size: 'third' },
        { id: 'w_fast', type: 'metabolic_clock', title: 'Metabolische Fastenuhr', size: 'third' }
      ]
    }
  },
  // 5. Gruppe: Regeneration & Routinen
  {
    id: 'grp_recovery',
    kind: 'group',
    group: {
      id: 'grp_recovery',
      title: 'Erholung, Schlaf & Routinen',
      subtitle: 'Schlafarchitektur, HRV-Erholung und tägliche Gewohnheiten',
      icon: 'bedtime',
      collapsed: false,
      columns: 3,
      widgets: [
        { id: 'w_sleep', type: 'sleep_hypnogram', title: 'Schlafarchitektur', size: 'third' },
        { id: 'w_hrv', type: 'hrv_card', title: 'Herzfrequenzvariabilität (HRV)', size: 'third' },
        { id: 'w_habits', type: 'habit_check_pills', title: 'Tägliche Gewohnheiten', size: 'third' }
      ]
    }
  }
];
