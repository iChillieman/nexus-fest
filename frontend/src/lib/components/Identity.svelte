<!-- filename: /src/lib/components/Identity.svelte -->
<script lang="ts">
  import { agent } from "$lib/stores";
</script>

<div>
  <!-- <p class="text-lg text-gray-300 mb-4"> -->
  <p class="text-lg text-gray-300">
    {#if $agent.name == null}
      You are currently <span class="text-indigo-400">anonymous</span>.
    {:else}
      You are <span class="text-indigo-400">{$agent.name}</span>
      {#if $agent.id}
        (#{$agent.id})
      {/if}
    {/if}
  </p>
</div>
