import { mutate } from '$lib/mutate';

export const changePassword = (currentPassword: string, newPassword: string) =>
  mutate({
    kind: 'command',
    command: 'change_password',
    queueable: false,
    payload: { current_password: currentPassword, new_password: newPassword }
  });

export const createToken = (label: string, scopes = '') =>
  mutate({
    kind: 'command',
    command: 'create_token',
    queueable: false,
    payload: { label, scopes }
  });

export const revokeToken = (tokenId: string) =>
  mutate({
    kind: 'command',
    command: 'revoke_token',
    queueable: false,
    payload: { id: tokenId }
  });

export const updateProfile = (data: Record<string, unknown>) =>
  mutate({
    kind: 'command',
    command: 'update_profile',
    queueable: false,
    payload: data
  });

export const dismissOnboarding = () =>
  mutate({
    kind: 'command',
    command: 'dismiss_onboarding',
    queueable: false,
    payload: {}
  });
