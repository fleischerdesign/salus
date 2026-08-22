import { render, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, it } from 'vitest';
import BiomarkerTable from '$components/labs/BiomarkerTable.svelte';
import { db } from '$lib/db/database';
import { resetDb } from '../helpers/db';

beforeEach(async () => {
  await resetDb();
  await db.lab_marker.add({
    code: 'HDL',
    category: 'lipids',
    reference_low: 40,
    reference_high: 60,
    optimal_low: null,
    optimal_high: null,
    description: 'HDL-Cholesterin'
  });
  await db.lab_result.add({
    id: 'r1',
    panel_id: 'p1',
    user_id: 'u',
    metric_code: 'HDL',
    value: 55,
    unit: 'mg/dL',
    is_abnormal: false,
    reference_low: 40,
    reference_high: 60,
    created_at: '2026-01-01T00:00:00.000Z',
    updated_at: null,
    deleted_at: null
  });
});

describe('BiomarkerTable', () => {
  it('shows a clear title without matrix jargon', async () => {
    const { container } = render(BiomarkerTable);
    await waitFor(() => {
      expect(container.textContent).toContain('Laborwert-Verlauf');
      expect(container.textContent).not.toContain('Multi-Draw');
      expect(container.textContent).not.toContain('Verlaufsmatrix');
      expect(container.textContent).not.toContain('Biomarker-Verlaufsmatrix');
    });
  });

  it('renders lab rows and no redundant export placeholder button', async () => {
    const { container } = render(BiomarkerTable);
    await waitFor(() => {
      expect(container.textContent).toContain('HDL-Cholesterin');
    });
    expect(container.textContent).not.toContain('Arztbericht exportieren');
    expect(container.textContent).not.toContain('ISO/DIN');
  });
});