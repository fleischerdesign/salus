import { render, waitFor } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import LabsPage from '$components/pages/LabsPage.svelte';

vi.mock('$app/state', () => ({
  page: { url: { pathname: '/labs/matrix' } }
}));

describe('LabsPage header', () => {
  it('shows a clear human-friendly heading and subtitle without jargon', async () => {
    const { container } = render(LabsPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Laborwerte');
      expect(container.textContent).toContain('Laborwert-Verlauf, Organprofile und Befund-Freigabe');
    });
  });

  it('does not show the misleading fasting badge or crypto jargon badges', async () => {
    const { container } = render(LabsPage);
    await waitFor(() => {
      expect(container.textContent).not.toContain('Nüchternblut');
      expect(container.textContent).not.toContain('Optimal');
      expect(container.textContent).not.toContain('3 Panels');
      expect(container.textContent).not.toContain('ECDH');
      expect(container.textContent).not.toContain('Multi-Draw');
      expect(container.textContent).not.toContain('Verlaufsmatrix');
    });
  });
});

describe('LabsPage action buttons and tabs', () => {
  it('uses concise action button labels', async () => {
    const { container } = render(LabsPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Arzt-Freigabe');
      expect(container.textContent).toContain('PDF-Arztbericht');
    });
  });

  it('labels the tabs understandably', async () => {
    const { container } = render(LabsPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Laborwert-Verlauf');
      expect(container.textContent).toContain('Organprofile');
      expect(container.textContent).toContain('Arzt-Freigabe');
    });
  });

  it('gives the tab icons a uniform inherited color instead of hardcoded per-tab colors', async () => {
    const { container } = render(LabsPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Arzt-Freigabe');
    });
    const shareLink = [...container.querySelectorAll('a')].find((a) =>
      a.textContent?.includes('Arzt-Freigabe')
    );
    expect(shareLink).toBeDefined();
    expect(shareLink!.textContent).not.toContain('ECDH');
    // Inactive share tab (matrix is active): the icon must not carry a hardcoded color class.
    expect(shareLink!.outerHTML).not.toContain('text-circadian');
    expect(shareLink!.outerHTML).not.toContain('text-primary');
    expect(shareLink!.outerHTML).not.toContain('text-vital');
  });
});