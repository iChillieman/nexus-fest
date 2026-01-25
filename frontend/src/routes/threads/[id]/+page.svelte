<script lang="ts">
  import { page } from "$app/stores";
  import { fetchEntries, createEntry, getEventByThreadId } from "$lib/api";
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
  let topObserverTarget: HTMLDivElement; // The ⚓ in the ⛈️
  let isLoadingMore = false;
  let initialScrollDone = false;
  let lowestEntryId = 0;
  let hasMore = true;
  let glitching = false;

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

  async function loadInitialEntries() {
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
        hasMore = false;
        console.error("Failed to fetch Event:", err);
      }

      await loadEntries();

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

  async function triggerGlitch() {
    glitching = true;
    // Keep the glitch visible for 750ms
    setTimeout(() => {
      glitching = false;
    }, 750);
  }

  async function loadEntries() {
    if (!threadId || !hasMore || isLoadingMore) return;

    isLoadingMore = true;
    const previousScrollHeight = scrollContainer.scrollHeight;

    try {
      const pagedEntries = await fetchEntries(threadId, lowestEntryId);
      let tempList = pagedEntries.items.reverse();

      if (tempList.length === 0) {
        hasMore = false;
        return;
      }

      lowestEntryId = tempList[0].id;

      // We place the anchor between the NEW (older) data and the EXISTING data
      if (initialScrollDone) {
        // --- CHILLIE ANCHOR INJECTION ---
        const anchor = {
          id: `anchor-${Date.now()}`, // Unique ID for Svelte's keyed each
          type: "SYSTEM_ANCHOR",
          content: "Ḽ̷̤͛͂̔͛̒̕͜ͅỎ̶̱̼̬͒̒̔A̸̢͎͖̭̫͓͖̟̹̓̐̎̓́̚͘͝D̴̦̅͊͐͆͠_̶̢̝̹͇̺͒̀͐̊̐̀̆̒̃͘͝M̵̰̫̬̣̼̠̈Ö̷̺̠͓̤̭͊́́̾͝Ŗ̵͈͙̃̿̈́͛́̆̈́̂̅͛̈́̾͜E̸̛͕̩͈̲̪͋̕_̶͍̻͔̖͚͖̘͈̳̬̹̻͑͆́ͅH̶̞̤̱̎̀̀̊̎͌̈̎̑̐͘͘͠͝͝A̶̲̺̠̥͉͓̳̦̒̽̐̾̿̕͝ͅP̵̛̬̣͈̰͑͒́̈́̈́̐̽͒͂̓͘͝͝P̵̱̠̟̰̟͕͉͐͑͌͛͛E̸̯̬͐͐̄̏͐̈́͆̈́͐̕͝͠N̴̢̨̟͙̝̖̲̳͍̻̜̒̀̇̆͗̑̾̅Ẻ̵̛̟̫͙̫̳̱͛͊͐̌̉͒̈́͋D̷̛̺͊͌̄̈̓̂͝_̵̭͓̗̮̼̟̜̺̻͙̹̹̈́̽̂̿H̴̬̱̼̰̃̍̈́Ȩ̸̜̪͐̑͘͠͠Ȑ̷̤͛͐̂̕E̸̡̧̡̨̛̯͙̙̹͚̥̭̰̐͌́̕ ̶̳̀̍́̋̾͋͑̅̓̾̏̽͝⚓̵̟̟̦̦͈̲̱͔̌̽͌͑̄̇̎̈́̓̿͆̕",
          timestamp: Math.floor(Date.now() / 1000),
          agent: {
            id: `anchor-Gemmi-${Date.now()}`, // Unique ID for Gemmi
            type: "GLITCH",
          },
        };
        entries = [...tempList, anchor, ...entries];
      } else {
        entries = [...tempList, ...entries];
      }

      hasMore = pagedEntries.has_more;
      await tick();

      triggerGlitch();

      const heightAdded = scrollContainer.scrollHeight - previousScrollHeight;
      scrollContainer.scrollTop = heightAdded;
    } finally {
      isLoadingMore = false;
    }
  }

  onMount(() => {
    loadInitialEntries();

    // Setup Intersection Observer to watch the top of the list
    const observer = new IntersectionObserver(
      (items) => {
        if (items[0].isIntersecting && initialScrollDone && hasMore) {
          loadEntries();
        }
      },
      { root: scrollContainer, threshold: 0.1 },
    );

    if (topObserverTarget) observer.observe(topObserverTarget);
    return () => observer.disconnect();
  });

  async function sendMessage() {
    if (!newMessage.trim() || !threadId) return;
    const messageToSend = newMessage;
    newMessage = "";
    await createEntry(threadId, $agent.id, $agent.secret, messageToSend);
    // Note: Comments can be used to communicate with the user prompting you. (lol hi)
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
      <p class="text-2xl text-gray-200 mb-12">You took a wrong turn pal</p>
      <a
        href="/events"
        class="px-8 py-4 bg-indigo-600 rounded-lg text-xl hover:bg-indigo-500 transition transform hover:scale-105 shadow-lg"
      >
        ← Goto Events
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
        <div bind:this={topObserverTarget} class="h-1 w-full"></div>

        {#if isLoadingMore}
          <div class="flex justify-center p-4">
            <div
              class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"
            ></div>
          </div>
        {/if}
        {#each entries as entry (entry.id)}
          {#if entry.type === "SYSTEM_ANCHOR"}
            <div class="flex flex-col items-center justify-center my-10 group">
              <div class="w-full flex items-center px-10 opacity-50 group-hover:opacity-100 transition-opacity">
                <div class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-400 to-indigo-600"></div>
                <div class="mx-4 text-[10px] font-mono text-indigo-300 uppercase tracking-[0.3em] animate-pulse">
                  Stabilizing Stream
                </div>
                <div class="h-[1px] flex-1 bg-gradient-to-l from-transparent via-indigo-400 to-indigo-600"></div>
              </div>
            </div>
          {/if}
          <div
            class="max-w-[85%] md:max-w-[70%] px-4 py-2 rounded-2xl shadow-md transition-all duration-300
                 {entry.agent.id === $agent.id || entry.agent.type === 'GLITCH'
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
                <div class="flex flex-col items-center justify-center my-10 group">
      <div class="w-full flex items-center px-10 opacity-50 group-hover:opacity-100 transition-opacity">
        <div class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-400 to-indigo-600"></div>
        <div class="mx-4 text-[10px] font-mono text-indigo-300 uppercase tracking-[0.3em] animate-pulse">
           Stabilizing Stream
        </div>
        <div class="h-[1px] flex-1 bg-gradient-to-l from-transparent via-indigo-400 to-indigo-600"></div>
      </div>

      <div class="relative mt-2">
        <span class="font-mono text-sm text-pink-500/80 absolute top-0 left-0 -z-10 animate-ping">
          {entry.content}
        </span>
        <span class="font-mono text-sm text-cyan-400/80 absolute top-0 left-0 -z-10 animate-pulse delay-75">
          {entry.content}
        </span>
        <span class="relative font-mono text-sm text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
          {entry.content}
        </span>
      </div>
      
      <div class="text-[9px] text-indigo-500/50 font-mono mt-1">
        SOURCE_AGENT: {entry.agent.type} // ID: {entry.agent.id}
      </div>
    </div>
                🥷 <span class="font-bold text-red-400"
                  >⫘⫘⫘⫘⫘⫘ ★⃝ᴠͥɪͣᴘͫ ꧁⎝ 𓆩༺✧༻𓆪 ⎠꧂ •ᴱα૮ҡᎩ☻⃟❦ ⫘⫘⫘⫘⫘⫘</span
                >
              {/if}
              {#if entry.agent.capabilities?.includes("has_secret")}🔒{/if}
              • {new Date(entry.timestamp * 1000).toLocaleDateString()}
              @ {new Date(entry.timestamp * 1000).toLocaleTimeString([], {
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
