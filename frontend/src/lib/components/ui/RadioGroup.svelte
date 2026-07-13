<script lang="ts">
  interface Option {
    value: string;
    label: string;
  }

  interface Props {
    options: Option[];
    value?: string;
    name: string;
    onchange?: (value: string) => void;
    required?: boolean;
    class?: string;
  }

  let {
    options,
    value = '',
    name,
    onchange,
    required = false,
    class: extraClass = ''
  }: Props = $props();

  function select(val: string) {
    onchange?.(val);
  }
</script>

<div class="flex flex-wrap gap-2 {extraClass}" role="radiogroup">
  {#each options as opt}
    <button
      class="duration-micro rounded-md border px-3 py-1.5 text-[13px] font-semibold tracking-[0.05em] transition-colors {value ===
      opt.value
        ? 'border-primary-500 bg-primary-500 text-white'
        : 'border-surface-200 bg-surface-100 text-surface-700 hover:bg-surface-200'}"
      onclick={() => select(opt.value)}
      type="button"
      role="radio"
      aria-checked={value === opt.value}
    >
      {opt.label}
    </button>
  {/each}
  <input type="hidden" {name} {value} {required} />
</div>
