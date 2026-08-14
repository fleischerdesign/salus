import { mutate } from '$lib/mutate';

export function runDataQualityCheck() {
  return mutate({
    kind: 'command',
    command: 'data_quality_recheck',
    queueable: true,
    payload: {}
  });
}

export function acknowledgeDataQualityFlag(flagId: string) {
  return mutate({
    kind: 'command',
    command: 'data_quality_acknowledge',
    queueable: true,
    payload: { flag_id: flagId }
  });
}
