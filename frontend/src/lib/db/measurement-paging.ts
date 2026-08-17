import Dexie from 'dexie';
import type { IndexableType } from 'dexie';

/**
 * Cursor position for paging measurements on the [metric_code+start_time] index.
 * `top` = the newest page; `older`/`newer` navigate away/toward the newest.
 */
export type MeasurementCursor =
  { mode: 'top' } | { mode: 'older'; time: string } | { mode: 'newer'; time: string };

/** Code-bounded key-range bounds for a cursor page (pure, unit-testable). */
export interface PageBounds {
  lower: [string, IndexableType];
  upper: [string, IndexableType];
  includeLower: boolean;
  includeUpper: boolean;
}

/**
 * Computes the bounds for one measurement page. The range is always closed to the
 * metric's code — a plain `above`/`below` on the composite index would bleed into
 * lexicographically neighboring metrics. `older` excludes the boundary timestamp
 * (strictly older), `newer` excludes it (strictly newer), so pages never repeat a row.
 */
export function measurementPageBounds(code: string, cursor: MeasurementCursor): PageBounds {
  switch (cursor.mode) {
    case 'older':
      return {
        lower: [code, Dexie.minKey],
        upper: [code, cursor.time],
        includeLower: true,
        includeUpper: false
      };
    case 'newer':
      return {
        lower: [code, cursor.time],
        upper: [code, Dexie.maxKey],
        includeLower: false,
        includeUpper: true
      };
    default:
      return {
        lower: [code, Dexie.minKey],
        upper: [code, Dexie.maxKey],
        includeLower: true,
        includeUpper: true
      };
  }
}
