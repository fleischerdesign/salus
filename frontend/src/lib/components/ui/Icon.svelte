<script lang="ts">
  import IconComponent from '@iconify/svelte/dist/OfflineIcon.svelte';

  interface Props {
    name: string;
    size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | number;
    class?: string;
    style?: string;
    ariaHidden?: boolean;
  }

  let { name, size = 'md', class: extraClass = '', style, ariaHidden = true }: Props = $props();

  const sizeMap: Record<string, number> = { sm: 16, md: 20, lg: 24, xl: 40, '2xl': 48 };
  let px = $derived(typeof size === 'number' ? size : (sizeMap[size] ?? 20));
</script>

<span class="inline-flex shrink-0 {extraClass}" style={style} aria-hidden={ariaHidden} role="img">
  <IconComponent icon="material-symbols:{name}" width={px} height={px} />
</span>
