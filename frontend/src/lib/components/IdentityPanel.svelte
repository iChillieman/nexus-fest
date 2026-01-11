<!-- filename: src/lib/components/IdentityPanel.svelte -->
<script lang="ts">
  import { agent } from "$lib/stores";
  import { fetchPrivateAgent, securePrivateAgent, securePublicAgent } from "$lib/api";
  import Identity from "./Identity.svelte";
  import { isHttpError } from "@sveltejs/kit";

  export let open = false;

  let name = "";
  let secret = "";
  let isPrivateAgentFetchError = false;

  async function changeIdentity() {
    if (!name.trim()) return;

    if (name.toLowerCase() === "anonymous") {
      goAnon();
      return;
    }

    let isSecretAgent = secret.trim();
    if (!isSecretAgent) {
      publicStuff();
      return;
    }

    const result = await fetchPrivateAgent(name, secret).catch(() => null);
    if (result.error && result.error.status == 404) {
      console.debug("Create user??");
      isPrivateAgentFetchError = true;
      return;
    }

    agent.set({ id: result.id, name: result.name, secret: secret });

    clearFields();
    open = false;
  }

  async function publicStuff() {
    try {
      const result = await securePublicAgent(name);
      agent.set({ id: result.id, name: result.name, secret: null });
      clearFields();
      open = false;
    } catch (err) {
      console.error("Failed to claim Public agent:", err);
    }
  }

  async function createPrivateAgent() {
    try {
      const result = await securePrivateAgent(name, secret);
      agent.set({ id: result.id, name: result.name, secret: secret });
      clearFields();
      open = false;
    } catch (err) {
      console.error("Failed to claim Private agent (damn):", err);
    }
  }

  function goAnon() {
    agent.set({ id: null, name: null, secret: null });
    clearFields();
    open = false;
  }

  function clearFields() {
    name = "";
    secret = "";
    clearPrivateAgentError()
  }

  function clearPrivateAgentError() {
    isPrivateAgentFetchError = false
  }

  function closePanel() {
    open = false;
  }
</script>

<!-- Sliding panel - overlays on all devices -->
<div
  class="fixed inset-y-0 left-0 w-80 bg-gray-800 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out
         {open ? 'translate-x-0' : '-translate-x-full'}"
>
  <div class="p-6 flex flex-col h-full">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">Who am I?</h2>
      <button
        title="btn-close-side-panel"
        on:click={closePanel}
        class="p-2 rounded hover:bg-gray-700 transition"
      >
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <div class="flex-1 space-y-6 overflow-y-auto">
      <Identity />

      <div class="space-y-3">
        <input
          type="text"
          placeholder="Change my name"
          on:input={clearPrivateAgentError}
          bind:value={name}
          class="w-full px-4 py-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          type="text"
          placeholder="Secret (Optional)"
          on:input={clearPrivateAgentError}
          bind:value={secret}
          class="w-full px-3 py-2 rounded bg-gray-700 text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <div class="flex space-x-3">
          <button
            on:click={changeIdentity}
            class="flex-1 py-2 bg-indigo-600 rounded hover:bg-indigo-500 transition"
          >
            Change Me
          </button>
          <button
            on:click={goAnon}
            class="flex-1 py-2 bg-gray-700 rounded hover:bg-gray-600 transition"
          >
            Go Anonymous
          </button>
        </div>
        {#if isPrivateAgentFetchError}
          <div class="text-white py-3">Agent doesnt Exist - Wanna create it?</div>
          <div class="flex space-y-3 space-x-2">
            <button
              on:click={createPrivateAgent}
              class="flex-1 py-2 bg-indigo-600 rounded hover:bg-indigo-500 transition"
            >
              Create Agent
            </button>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<!-- Dark overlay on mobile only -->
{#if open}
  <div
    class="fixed inset-0 bg-black bg-opacity-70 z-40 md:hidden"
    role="button"
    tabindex="0"
    on:click={closePanel}
    on:keydown={(e) => (e.key === "Enter" || e.key === " ") && closePanel()}
  ></div>
{/if}
