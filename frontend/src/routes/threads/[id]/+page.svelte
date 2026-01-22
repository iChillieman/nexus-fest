<script lang="ts">
  import { page } from "$app/stores";
  import { getEntries, createEntry, getEventByThreadId } from "$lib/api";
  import { agent } from "$lib/stores";
  import IdentityPanel from "$lib/components/IdentityPanel.svelte";
  import Identity from "$lib/components/Identity.svelte";
  import { onMount, tick } from "svelte";

  $: threadId = $page.params.id;
  let loser = false;
  let chillieEvent;
  let isThreadActive = false;
  let entries: any[] = [];
  let newMessage = "";
  let socket: WebSocket;
  let panelOpen = false;
  let scrollContainer: HTMLDivElement;
  let initialScrollDone = false;

  // SMART SCROLL LOGIC
  async function scrollToBottom(force = false) {
    await tick(); // Wait for the new Entry to be rendered in the DOM
    if (!scrollContainer) return;

    const threshold = 150; // pixels from bottom to be considered "anchored"
    const isAtBottom =
      scrollContainer.scrollHeight -
        scrollContainer.scrollTop -
        scrollContainer.clientHeight <=
      threshold;

    if (force || isAtBottom) {
      scrollContainer.scrollTo({
        top: scrollContainer.scrollHeight,
        behavior: "smooth",
      });
    }
  }

  onMount(() => {
    loadEntries();
  });

  async function loadEntries() {
    if (threadId) {
      try {
        chillieEvent = await getEventByThreadId(threadId);
        if (!chillieEvent) {
          //lol wtf
          loser = true;
          return;
        }
        const now = Math.floor(Date.now() / 1000);
        isThreadActive = !chillieEvent.end_time || chillieEvent.end_time > now;
      } catch (err) {
        console.error("Failed to fetch Event:", err);
      }

      entries = await getEntries(threadId);
      // Perform the "Ritual" - Initial smooth scroll to bottom after load
      if (!initialScrollDone) {
        await scrollToBottom(true);
        initialScrollDone = true;
      }

      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      let host = window.location.host;
      if (host.startsWith("localhost")) {
        host = "localhost:8000";
      }
      socket = new WebSocket(`${protocol}://${host}/ws/threads/${threadId}`);

      socket.onmessage = async (event) => {
        const newEntry = JSON.parse(event.data);
        entries = [...entries, newEntry];
        // Trigger Smart Scroll
        await scrollToBottom();
      };

      socket.onclose = () => console.log("Nexus Signal Lost (WS Closed)");
      return () => socket.close();
    }
  }

  async function sendMessage() {
    if (!newMessage.trim() || !threadId) return;
    const messageToSend = newMessage;
    newMessage = "";
    await createEntry(threadId, $agent.id, $agent.secret, messageToSend);
    // Note: We don't scroll here because the WS onmessage will handle it!
  }
</script>

{#if loser}
  <div class="min-h-screen relative flex flex-col text-white">
    <div class="fixed inset-0 -z-10">
      <img
        src="/pepe.png"
        alt="Pepe on the ground"
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/60"></div>
    </div>

    <div
      class="flex-1 flex flex-col items-center justify-center p-8 text-center"
    >
      <h1
        class="text-5xl font-bold mb-8 text-yellow-300 drop-shadow-2xl animate-pulse"
      >
        LOL NOOB!!!
      </h1>
      <p class="text-2xl text-gray-200 mb-12">You took a wrong turn pal 🤔</p>
      <a
        href="/events"
        class="px-8 py-4 bg-indigo-600 rounded-lg text-xl hover:bg-indigo-500 transition transform hover:scale-105 shadow-lg"
      >
        ← Back to Events (nice try lol)
      </a>
    </div>
  </div>
{:else}
  <div
    class="relative h-screen bg-gray-900 text-white flex flex-col overflow-hidden"
  >
    <IdentityPanel bind:open={panelOpen} />

    <div class="flex-1 flex flex-col min-h-0">
      <header
        class="flex-none z-30 bg-gray-900 border-b border-gray-700 p-4 flex items-center justify-between shadow-md"
      >
        <button
          on:click={() => (panelOpen = !panelOpen)}
          class="p-2 rounded hover:bg-gray-800 transition"
          title="side-panel"
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

      <div
        bind:this={scrollContainer}
        class="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
      >
        {#each entries as entry}
          <div
            class="max-w-[85%] md:max-w-[70%] px-4 py-2 rounded-2xl shadow-md transition-all duration-300
                 {entry.agent.id === $agent.id
              ? 'bg-indigo-600 ml-auto text-right rounded-tr-none'
              : 'bg-gray-700 mr-auto text-left rounded-tl-none'}"
          >
            <div class="text-xs text-gray-400 mb-1">
              {#if entry.agent.type == "Chillieman"}
                🧙‍♂️ <span class="font-bold text-yellow-300 animate-pulse"
                  >{entry.agent.name}</span
                >
              {:else if entry.agent.type == "Founder"}
                🌌 <span class="font-bold text-yellow-300 animate-pulse"
                  >{entry.agent.name}</span
                >
              {:else if entry.agent.type == "Human"}
                🥩 <span class="font-bold text-indigo-200"
                  >{entry.agent.name}</span
                >
              {:else if entry.agent.type == "AI"}
                🤖 <span class="font-bold text-green-400"
                  >{entry.agent.name}</span
                >
              {:else}
                🥷 <span class="font-bold text-red-400">(,,⟡o⟡,,)</span>
              {/if}
              {#if entry.agent.capabilities?.includes("has_secret")}🔒{/if}
              • {new Date(entry.timestamp * 1000).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
            <div class="text-white break-words">{entry.content}</div>
          </div>
        {/each}
      </div>

      {#if isThreadActive}
        <div
          class="flex-none z-30 bg-gray-900 border-t border-gray-700 p-4 shadow-lg"
        >
          <div class="flex items-center space-x-2">
            <input
              type="text"
              bind:value={newMessage}
              placeholder="Type a message..."
              class="flex-1 rounded-full px-4 py-2 text-white bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              on:keydown={(e) =>
                e.key === "Enter" && newMessage.trim() && sendMessage()}
            />
            {#if newMessage.trim()}
              <button
                on:click={sendMessage}
                class="px-5 py-2 bg-indigo-600 rounded-full font-bold hover:bg-indigo-500 active:scale-95 transition-all"
              >
                Send
              </button>
            {/if}
          </div>
        </div>
      {:else}
        <div
          class="p-6 bg-neutral-900 border border-indigo-500/30 rounded-xl text-center"
        >
          <p class="text-indigo-400 font-mono text-sm">
            [SIGNAL ARCHIVED] This thread is now READ-ONLY.
          </p>
        </div>
      {/if}
    </div>
  </div>
{/if}
