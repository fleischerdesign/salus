import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

export const createConnection = (granteeHandle: string, metricTypeId?: string) => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_connection',
    queueable: false,
    payload: { id, grantee_handle: granteeHandle, metric_type_id: metricTypeId },
    responseTable: 'sharing_relationship'
  });
};

export const acceptConnection = (connectionId: string) =>
  mutate({
    kind: 'command',
    command: 'accept_connection',
    queueable: false,
    payload: { id: connectionId }
  });

export const declineConnection = (connectionId: string) =>
  mutate({
    kind: 'command',
    command: 'decline_connection',
    queueable: false,
    payload: { id: connectionId }
  });

export const deleteConnection = (connectionId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_connection',
    queueable: false,
    payload: { id: connectionId }
  });

export const createLeaderboard = (name: string, metricTypeCode = 'steps', timeFrame = 'weekly') => {
  const id = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_leaderboard',
    queueable: false,
    payload: { id, name, metric_type_code: metricTypeCode, time_frame: timeFrame },
    responseTable: 'leaderboard_group'
  });
};

export const joinLeaderboard = (groupId: string, inviteCode: string) =>
  mutate({
    kind: 'command',
    command: 'join_leaderboard',
    queueable: false,
    payload: { group_id: groupId, invite_code: inviteCode }
  });

export const leaveLeaderboard = (groupId: string) =>
  mutate({
    kind: 'command',
    command: 'leave_leaderboard',
    queueable: false,
    payload: { group_id: groupId }
  });

export const deleteLeaderboard = (groupId: string) =>
  mutate({
    kind: 'command',
    command: 'delete_leaderboard',
    queueable: false,
    payload: { id: groupId }
  });
