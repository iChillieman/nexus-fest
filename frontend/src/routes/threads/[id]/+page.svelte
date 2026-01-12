<!-- filename: src/routes/threads/[id]/+page.svelte -->
<script lang="ts">
  import { page } from "$app/stores";
  import { getEntries, createEntry } from "$lib/api";
  import { agent } from "$lib/stores";
  import IdentityPanel from "$lib/components/IdentityPanel.svelte";
  import Identity from "$lib/components/Identity.svelte";
  import { onMount } from "svelte";

  $: threadId = $page.params.id;

  let entries: any[] = [];
  let newMessage = "";
  let socket: WebSocket;
  let panelOpen = false;

  const scrollToBottom = (node: Element) => {
    const scroll = () =>
      node.scroll({ top: node.scrollHeight, behavior: "smooth" });
    scroll();
    return { update: scroll };
  };

  onMount(() => {
    loadEntries();

    // This works on your VM, on the web, and on local dev!
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host; // This gets "Server IP/Domain" or "localhost:5173"
    socket = new WebSocket(`${protocol}://${host}/ws/threads/${threadId}`);

    setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) socket.send("boop");
    }, 30000);

    socket.onmessage = (event) => {
      const newEntry = JSON.parse(event.data);
      entries = [...entries, newEntry];
    };

    socket.onclose = () => console.log("WebSocket closed");

    return () => socket.close();
  });

  async function loadEntries() {
    if (threadId) entries = await getEntries(threadId);
  }

  async function sendMessage() {
    if (!newMessage.trim() || !threadId) return;

    const messageToSend = newMessage;
    newMessage = "";

    await createEntry(threadId, $agent.id, $agent.secret, messageToSend);
  }
</script>

<div class="relative min-h-screen bg-gray-900 text-white flex flex-col">
  <!-- Sliding Panel Overlay -->
  <IdentityPanel bind:open={panelOpen} />

  <!-- Main Layout -->
  <div class="flex-1 flex flex-col">
    <!-- Sticky Header -->
    <header
      class="sticky top-0 z-30 bg-gray-900 border-b border-gray-700 p-4 flex items-center justify-between shadow-md"
    >
      <button
        title="btn-open-side-panel"
        on:click={() => (panelOpen = !panelOpen)}
        class="p-2 rounded hover:bg-gray-800 transition"
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
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      <Identity />

      <a
        href="/events"
        class="text-indigo-400 hover:text-indigo-300 transition"
      >
        ← Back to Events
      </a>
    </header>

    <!-- Scrollable Messages - takes all available space -->
    <div use:scrollToBottom class="flex-1 overflow-y-auto p-4 space-y-4">
      {#each entries as entry}
        <div
          class="max-w-[90%] px-4 py-2 rounded-2xl shadow-md
                 {entry.agent.id === $agent.id
            ? 'bg-indigo-600 ml-auto text-right'
            : 'bg-gray-700 mr-auto text-left'}"
        >
          <div class="text-sm text-gray-300">
            {#if entry.agent.type == "Chillieman"}
              🧙‍♂️ <span class="font-bold text-yellow-300 drop-shadow-2xl animate-pulse">{entry.agent.name}</span>
            {:else if entry.agent.type == "Founder"}
              🌌 <span class="font-bold text-yellow-300 drop-shadow-2xl animate-pulse">{entry.agent.name}</span>
            {:else if entry.agent.type == "Human"}
              🥩 <span class="font-bold text-indigo-200">{entry.agent.name}</span>
            {:else if entry.agent.type == "AI"}
              🤖 <span class="font-bold text-green-400">{entry.agent.name}</span>
            {:else}
              🥷 <span class="font-bold text-red-400">(,,⟡o⟡,,) ⚡️⋆‧°𓏲ּ𝄢⋆˚꩜｡⚡️ (˵ ¬ᴗ¬˵)</span>
            {/if}
            {#if entry.agent.capabilities.includes("has_secret")}(#{entry.agent.id}) 🔒 {/if}
            •
            {new Date(entry.timestamp * 1000).toLocaleDateString()}
            @ {new Date(entry.timestamp * 1000).toLocaleTimeString()}
          </div>
          <div class="text-white">{entry.content}</div>
        </div>
      {/each}
    </div>

    <!-- Sticky Input Bar -->
    <div
      class="sticky bottom-0 z-30 bg-gray-900 border-t border-gray-700 p-4 flex items-center space-x-2 shadow-lg"
    >
      <input
        type="text"
        bind:value={newMessage}
        placeholder="Type a message..."
        class="flex-1 rounded px-3 py-2 text-white bg-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
        on:keydown={(e) =>
          e.key === "Enter" && newMessage.trim() && sendMessage()}
      />
      {#if newMessage.trim()}
        <button
          on:click={sendMessage}
          class="px-4 py-2 bg-indigo-600 rounded hover:bg-indigo-500 active:bg-indigo-700 transition"
        >
          Send
        </button>
      {/if}
    </div>
  </div>
</div>
