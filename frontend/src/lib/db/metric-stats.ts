import Dexie from 'dexie';
import { db } from '$lib/db/database';

export const STATS_VERSION = 2;

export interface MetricStat {
  metric_code: string;
  entry_count: number;
  latest_value: string | null;
  latest_date: string | null;
  latest_timestamp: number | null;
}

export interface SourceStat {
  source_id: string;
  entry_count: number;
  latest_time: string | null;
  metrics: Record<string, number>;
}

export interface SystemStats {
  version: number;
  metrics: Record<string, MetricStat>;
  sources: Record<string, SourceStat>;
  total_measurements: number;
  last_updated: number;
}

// L1 RAM Cache
let _memoryStats: SystemStats | null = null;
let _isRecomputing = false;

/**
 * Retrieves the materialized system statistics:
 * 1. L1: RAM (0.0001 ms)
 * 2. L2: Disk / db.meta (0.1 ms)
 * 3. Fallback: Fast indexed computation + write to L1 and L2
 */
export async function getSystemStats(): Promise<SystemStats> {
  if (_memoryStats && _memoryStats.version === STATS_VERSION) {
    return _memoryStats;
  }

  try {
    const entry = await db.meta.get('system_stats');
    if (entry && entry.value) {
      const val = entry.value as SystemStats;
      if (val.version === STATS_VERSION) {
        _memoryStats = val;
        return _memoryStats;
      }
    }
  } catch {
    /* fallback to compute */
  }
  return recomputeAllStats();
}

/**
 * Recomputes all metric and source statistics in a fast indexed pass,
 * stores in L1 RAM immediately, and writes to L2 Disk in background.
 */
export async function recomputeAllStats(): Promise<SystemStats> {
  if (_isRecomputing && _memoryStats) {
    return _memoryStats;
  }
  _isRecomputing = true;

  try {
    const defs = await db.metric_definition.toArray();
    const metrics: Record<string, MetricStat> = {};
    const sources: Record<string, SourceStat> = {};
    let total = 0;

    function metricRange(code: string) {
      return db.measurement
        .where('[metric_code+start_time]')
        .between([code, Dexie.minKey], [code, Dexie.maxKey]);
    }

    await Promise.all(
      defs.map(async (d) => {
        const latest = await metricRange(d.code).last();
        if (latest && !latest.deleted_at) {
          const count = await metricRange(d.code).count();
          total += count;
          metrics[d.code] = {
            metric_code: d.code,
            entry_count: count,
            latest_value: latest.value_text ?? latest.value_numeric?.toString() ?? null,
            latest_date: latest.start_time ? latest.start_time.split('T')[0] : null,
            latest_timestamp: latest.start_time ? new Date(latest.start_time).getTime() : null
          };
        } else {
          metrics[d.code] = {
            metric_code: d.code,
            entry_count: 0,
            latest_value: null,
            latest_date: null,
            latest_timestamp: null
          };
        }
      })
    );

    for (const src of ['manual', 'health_connect', 'salus_sensor', 'apple_health']) {
      const srcCnt = await db.measurement.where('source').equals(src).count();
      sources[src] = {
        source_id: src,
        entry_count: srcCnt,
        latest_time: null,
        metrics: {}
      };
    }

    const stats: SystemStats = {
      version: STATS_VERSION,
      metrics,
      sources,
      total_measurements: total,
      last_updated: Date.now()
    };

    // Store in L1 RAM immediately
    _memoryStats = stats;

    // Persist to L2 Disk outside of any active read transaction context
    setTimeout(async () => {
      try {
        await db.meta.put({ key: 'system_stats', value: stats });
      } catch (err) {
        console.warn('Failed to persist system_stats to db.meta:', err);
      }
    }, 0);

    return stats;
  } finally {
    _isRecomputing = false;
  }
}

export async function getMetricStats(): Promise<Record<string, MetricStat>> {
  const stats = await getSystemStats();
  return stats.metrics;
}

export async function getMetricStat(code: string): Promise<MetricStat | null> {
  const stats = await getSystemStats();
  return stats.metrics[code] ?? null;
}

export async function getSourceStats(): Promise<Record<string, SourceStat>> {
  const stats = await getSystemStats();
  return stats.sources;
}

export async function getSourceStat(sourceId: string): Promise<SourceStat | null> {
  const stats = await getSystemStats();
  return stats.sources[sourceId] ?? null;
}
