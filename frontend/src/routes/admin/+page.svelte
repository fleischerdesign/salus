<script lang="ts">
  import { goto } from '$app/navigation';

  $effect(() => {
    goto('/admin/stats', { replaceState: true });
  });
</script>
