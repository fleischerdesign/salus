class UpdateService {
  updatePending = $state(false);

  // Guards
  isDirty = $state(false);
  activeWorkout = $state(false);
  isSyncing = $state(false);
  isSpeaking = $state(false);

  canAutoReload = $derived(
    this.updatePending &&
      !this.isDirty &&
      !this.activeWorkout &&
      !this.isSyncing &&
      !this.isSpeaking
  );

  setUpdatePending(pending: boolean) {
    this.updatePending = pending;
  }

  setIsDirty(dirty: boolean) {
    this.isDirty = dirty;
  }

  setActiveWorkout(active: boolean) {
    this.activeWorkout = active;
  }

  setIsSyncing(syncing: boolean) {
    this.isSyncing = syncing;
  }

  setIsSpeaking(speaking: boolean) {
    this.isSpeaking = speaking;
  }

  triggerSafeReload(): boolean {
    if (this.canAutoReload) {
      if (typeof window !== 'undefined') {
        window.location.reload();
      }
      return true;
    }
    return false;
  }
}

export const updateService = new UpdateService();
