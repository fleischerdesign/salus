class ToastSettings {
  healthConnect = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_toast_health_connect') !== 'false'
      : true
  );

  manualSync = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_toast_manual_sync') !== 'false'
      : true
  );

  backgroundSync = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_toast_bg_sync') === 'true'
      : false
  );

  networkStatus = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('salus_toast_network_status') !== 'false'
      : true
  );

  setHealthConnect(val: boolean) {
    this.healthConnect = val;
    localStorage.setItem('salus_toast_health_connect', val ? 'true' : 'false');
  }

  setManualSync(val: boolean) {
    this.manualSync = val;
    localStorage.setItem('salus_toast_manual_sync', val ? 'true' : 'false');
  }

  setBackgroundSync(val: boolean) {
    this.backgroundSync = val;
    localStorage.setItem('salus_toast_bg_sync', val ? 'true' : 'false');
  }

  setNetworkStatus(val: boolean) {
    this.networkStatus = val;
    localStorage.setItem('salus_toast_network_status', val ? 'true' : 'false');
  }
}

export const toastSettings = new ToastSettings();
