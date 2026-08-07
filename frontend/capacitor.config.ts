import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'design.fleischer.salus',
  appName: 'Salus',
  webDir: 'build',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    LocalNotifications: {
      smallIcon: 'ic_stat_icon_config_sample',
      iconColor: '#4f46e5',
    },
    CapacitorUpdater: {
      autoUpdate: false,
    },
  },
};

export default config;
