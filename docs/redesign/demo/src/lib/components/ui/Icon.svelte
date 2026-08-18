<script lang="ts">
  let { name, size = 18, class: className = '' } = $props<{
    name: string;
    size?: number;
    class?: string;
  }>();
</script>

<svg
  class="inline-block shrink-0 {className}"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  {#if name === 'sun'}
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
  {:else if name === 'chart'}
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  {:else if name === 'flask' || name === 'labs'}
    <path d="M10 2v7.31"></path>
    <path d="M14 9.3V2"></path>
    <path d="M8.5 2h7"></path>
    <path d="M14 9.3a6.5 6.5 0 1 1-4 0"></path>
    <path d="M5.52 16h12.96"></path>
  {:else if name === 'insights'}
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
    <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
    <line x1="12" y1="22.08" x2="12" y2="12"></line>
  {:else if name === 'apps' || name === 'grid'}
    <rect x="3" y="3" width="7" height="7" rx="2"></rect>
    <rect x="14" y="3" width="7" height="7" rx="2"></rect>
    <rect x="14" y="14" width="7" height="7" rx="2"></rect>
    <rect x="3" y="14" width="7" height="7" rx="2"></rect>
  {:else if name === 'sparkles'}
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"></path>
  {:else if name === 'bolt' || name === 'flash'}
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
  {:else if name === 'layers'}
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
  {:else if name === 'droplet' || name === 'water'}
    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
  {:else if name === 'timer' || name === 'fasting'}
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  {:else if name === 'heart' || name === 'vitals'}
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
  {:else if name === 'dumbbell' || name === 'workout'}
    <path d="M6 4v16M18 4v16M2 8h4M18 8h4M2 16h4M18 16h4M6 12h12"></path>
  {:else if name === 'food'}
    <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
    <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
    <line x1="6" y1="1" x2="6" y2="4"></line>
    <line x1="10" y1="1" x2="10" y2="4"></line>
    <line x1="14" y1="1" x2="14" y2="4"></line>
  {:else if name === 'check'}
    <polyline points="20 6 9 17 4 12"></polyline>
  {:else if name === 'search'}
    <circle cx="11" cy="11" r="8"></circle>
    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
  {:else if name === 'moon'}
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  {:else if name === 'plus'}
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  {:else if name === 'chevron-down'}
    <polyline points="6 9 12 15 18 9"></polyline>
  {:else if name === 'close'}
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  {:else if name === 'logout'}
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16 17 21 12 16 7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  {:else}
    <circle cx="12" cy="12" r="10"></circle>
  {/if}
</svg>
