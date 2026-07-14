import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

export const saveCircadianProfile = (
  latitude: number,
  longitude: number,
  timezoneOffsetHours: number,
  configuredChronotype: string = 'intermediate'
) =>
  mutate({
    kind: 'command',
    command: 'save_circadian_profile',
    queueable: false,
    payload: {
      latitude,
      longitude,
      timezone_offset_hours: timezoneOffsetHours,
      configured_chronotype: configuredChronotype
    },
    responseTable: 'circadian_profile'
  });

export const generateInsight = (date?: string) =>
  mutate({
    kind: 'command',
    command: 'generate_insight',
    queueable: false,
    payload: { date },
    responseTable: 'insight'
  });

export const synthesizeOpenScience = (payload: Record<string, unknown>) =>
  mutate({
    kind: 'command',
    command: 'synthesize_open_science',
    queueable: false,
    payload
  });

export const createShareRecipient = (name: string, publicKey: string) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_share_recipient',
    queueable: false,
    payload: { id, name, public_key: publicKey },
    responseTable: 'share_recipient'
  });
};

export const deleteShareRecipient = (recipientId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_share_recipient',
    queueable: false,
    payload: { id: recipientId }
  });

export const createAsymmetricShare = (
  recipientId: string,
  encryptedData: string,
  encryptedKey: string,
  expiresInHours?: number
) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_asymmetric_share',
    queueable: false,
    payload: {
      id,
      recipient_id: recipientId,
      encrypted_data: encryptedData,
      encrypted_key: encryptedKey,
      expires_in_hours: expiresInHours
    },
    responseTable: 'asymmetric_share'
  });
};

export const deleteAsymmetricShare = (shareId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_asymmetric_share',
    queueable: false,
    payload: { id: shareId }
  });
