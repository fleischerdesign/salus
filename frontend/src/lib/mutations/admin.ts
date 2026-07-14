import { mutate } from '$lib/mutate';

export const toggleAdmin = (userId: string) =>
  mutate({
    kind: 'command',
    command: 'toggle_admin',
    queueable: false,
    payload: { user_id: userId }
  });

export const toggleActive = (userId: string) =>
  mutate({
    kind: 'command',
    command: 'toggle_active',
    queueable: false,
    payload: { user_id: userId }
  });

export const deleteUser = (userId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_user',
    queueable: false,
    payload: { user_id: userId }
  });

export const adminRevokeToken = (tokenId: string) =>
  mutate({
    kind: 'command',
    command: 'admin_revoke_token',
    queueable: false,
    payload: { id: tokenId }
  });

export const setConfig = (key: string, value: string) =>
  mutate({
    kind: 'command',
    command: 'set_config',
    queueable: false,
    payload: { key, value }
  });
