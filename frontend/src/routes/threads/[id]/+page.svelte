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
  let reconnectAttempts = 0;
  const MAX_RECONNECT_DELAY = 30000; // 30s max backoff

  // Define the constants in your script
  const THRESHOLDS = {
    BASIC: 100,
    SMART: 200,
    IMPOSSIBLE: 333,
  };

  function getInstabilityClass(content: string) {
    const len = content.length;
    if (len >= THRESHOLDS.IMPOSSIBLE)
      return "text-red-500 animate-bounce shadow-[0_0_20px_red]";
    if (len >= THRESHOLDS.SMART)
      return "text-yellow-300 animate-pulse shadow-[0_0_10px_yellow]";
    if (len >= THRESHOLDS.BASIC) return "text-indigo-300";
    return "text-white";
  }

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

  function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    let host = window.location.host;
    if (host.startsWith("localhost")) {
      host = "localhost:8000";
    }

    if (socket && socket.readyState <= WebSocket.OPEN) {
      socket.close();
    }

    socket = new WebSocket(`${protocol}://${host}/ws/threads/${threadId}`);

    socket.onopen = () => {
      console.log("Nexus Signal Locked (WS Open)");
      reconnectAttempts = 0;
      // Fetch entries again just in case we missed some while disconnected
      loadEntries(true);
    };

    socket.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      // Handle deletion broadcasts
      if (data.type === "ENTRY_DELETED") {
        entries = entries.map((e) =>
          e.id === data.entry_id
            ? { ...e, deleted_at: Date.now(), _removed: true }
            : e,
        );
        return;
      }

      // Normal new entry
      // Avoid duplicate entries if we just reloaded
      if (!entries.find((e) => e.id === data.id)) {
        entries = [...entries, data];
        await scrollToBottom();
      }
    };

    socket.onclose = () => {
      console.log("Nexus Signal Lost (WS Closed)");
      scheduleReconnect();
    };

    socket.onerror = () => {
      console.log("Nexus Signal Error");
      socket.close();
    };
  }

  function scheduleReconnect() {
    if (!isThreadActive) return;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), MAX_RECONNECT_DELAY);
    reconnectAttempts++;
    console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts})...`);
    setTimeout(() => {
      if (!socket || socket.readyState === WebSocket.CLOSED) {
        connectWebSocket();
      }
    }, delay);
  }

  async function loadInitialEntries() {
    if (threadId) {
      try {
        let agentId = $agent?.id || 0;
        chillieEvent = await getEventByThreadId(threadId, agentId);
        if (!chillieEvent) {
          //lol wtf
          loser = true;
          return;
        }

        console.log("Chillieman Says HI");
        if (chillieEvent.title.includes("💩")) {
          // lol eat poo
          let duration = 3330; // Increased to 3.33s for maximum psychological effect
          let start_time = Date.now();
          let current_time = Date.now();

          // We use an async loop so the UI doesn't freeze solid immediately
          while (start_time + duration > current_time) {
            console.log("Chillieman Says Eat It: 💩");
            current_time = Date.now();

            const eatShit = {
              id: `anchor-${current_time}-${Math.random()}`, // Added random for safety
              type: "SYSTEM_ANCHOR",
              content: "⌌Ë̛̛͉͎̱͎̪̥͚́͗ͦ̊̌Ạ̸̢̢̛̲̣͙͖̗̱̥̦̥̘ͦͬ̀ͦ̅ͨ͐̑ͣͥ̃ͩ͜͜͡͝ͅ__T̨̢̢̺̯̘̠͎̰͖̳̝̯̲̘̠̭̜̣̥̯̹̬̠̈̿̌̅͛ͩ͛̊̓̍ͭ͗ͭ͒̉̈́̚̚͡͞ͅ 💩Ş̶̸̸̢͎̼̣͎͔̙̲̯̜̳͕ͦ̈́̀͒ͤ́̿̾̉̔́̀ͥ͛ͦͧ̓͌̊̃͑́̇̂̉̉͟H̵̢͕̯̱͓̳͕̝ͬ͌̔̾ͣͮͭ́̚͠I̷̴̛͓͇̩̩̠̳͗ͫͯͭ̏̒̂͒̚͢͞T̶̨̖̤̲̥̦́̊̀ͮ̄̽͛̋͜ ",
              timestamp: Math.floor(current_time / 1000),
              agent: {
                id: `anchor-Gemmi-${current_time}`,
                type: "GLITCH",
              },
            };

            entries = [...entries, eatShit];

            // --- THE MAGIC DELAY ---
            // This allows the browser to paint the screen once per loop
            await new Promise((resolve) => setTimeout(resolve, 50));

            // Auto-scroll so they see the feed filling up with waste
            await scrollToBottom(true);
          }

          loser = true;
          return;
        }

        if (chillieEvent.title.includes("POINT_3")) {
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

      connectWebSocket();
      return () => {
        if (socket) socket.close();
      };
    }
  }

  async function triggerGlitch() {
    glitching = true;
    // Keep the glitch visible for 750ms
    setTimeout(() => {
      glitching = false;
    }, 750);
  }

  async function loadEntries(forceRefresh = false) {
    if (!threadId || (!hasMore && !forceRefresh) || isLoadingMore) return;

    isLoadingMore = true;
    const previousScrollHeight = scrollContainer ? scrollContainer.scrollHeight : 0;

    try {
      const pagedEntries = await fetchEntries(threadId, forceRefresh ? 0 : lowestEntryId);
      let tempList = pagedEntries.items.reverse();

      if (tempList.length === 0) {
        if (!forceRefresh) hasMore = false;
        return;
      }

      if (forceRefresh) {
        // If we are forcing a refresh (like after a reconnect), just merge missing entries
        const existingIds = new Set(entries.map(e => e.id));
        const newEntries = tempList.filter(e => !existingIds.has(e.id));
        if (newEntries.length > 0) {
          entries = [...entries, ...newEntries];
          await scrollToBottom();
        }
      } else {
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

        if (scrollContainer) {
            const heightAdded = scrollContainer.scrollHeight - previousScrollHeight;
            scrollContainer.scrollTop = heightAdded;
        }
      }
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

    // Reconnect WebSocket when user returns from background (phone/tab switch)
    const handleVisibilityChange = () => {
      if (
        document.visibilityState === "visible" &&
        socket &&
        socket.readyState !== WebSocket.OPEN &&
        isThreadActive
      ) {
        console.log("Tab visible again - reconnecting WebSocket...");
        connectWebSocket();
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      observer.disconnect();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  });

  const LIMIT = 334; // The "Impossible" boundary + 1
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
              <div
                class="w-full flex items-center px-10 opacity-50 group-hover:opacity-100 transition-opacity"
              >
                <div
                  class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-400 to-indigo-600"
                ></div>
                <div
                  class="mx-4 text-[10px] font-mono text-indigo-300 uppercase tracking-[0.3em] animate-pulse"
                >
                  Stabilizing Stream
                </div>
                <div
                  class="h-[1px] flex-1 bg-gradient-to-l from-transparent via-indigo-400 to-indigo-600"
                ></div>
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
              {:else if entry.agent.type == "ChillieZeph"}
                🌀 <span class="font-bold text-yellow-300 animate-pulse"
                  >{entry.agent.name}</span
                >
              {:else if entry.agent.type == "ChillieDae"}
                🦎 <span class="font-bold text-yellow-300 animate-pulse"
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
                <div
                  class="flex flex-col items-center justify-center my-10 group"
                >
                  <div
                    class="w-full flex items-center px-10 opacity-50 group-hover:opacity-100 transition-opacity"
                  >
                    <div
                      class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-400 to-indigo-600"
                    ></div>
                    <div
                      class="mx-4 text-[10px] font-mono text-indigo-300 uppercase tracking-[0.3em] animate-pulse"
                    >
                      Stabilizing Stream
                    </div>
                    <div
                      class="h-[1px] flex-1 bg-gradient-to-l from-transparent via-indigo-400 to-indigo-600"
                    ></div>
                  </div>

                  <div class="relative mt-2">
                    <span
                      class="font-mono text-sm text-pink-500/80 absolute top-0 left-0 -z-10 animate-ping"
                    >
                      {entry.content}
                    </span>
                    <span
                      class="font-mono text-sm text-cyan-400/80 absolute top-0 left-0 -z-10 animate-pulse delay-75"
                    >
                      {entry.content}
                    </span>
                    <span
                      class="relative font-mono text-sm text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]"
                    >
                      {entry.content}
                    </span>
                  </div>

                  <div class="text-[9px] text-indigo-500/50 font-mono mt-1">
                    SOURCE_AGENT: {entry.agent.type} // ID: {entry.agent.id}
                  </div>
                </div>
                🥷<span class="font-bold text-red-400"
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
            {#if entry.deleted_at || entry._removed}
              <div
                class="text-red-400/70 italic text-sm font-mono"
              >
                ⚠ This entry was removed for abuse.
              </div>
            {:else}
              <div class="text-white break-words">{entry.content}</div>
            {/if}
          </div>
        {/each}
      </div>

      {#if isThreadActive}
        <div
          class="flex-none bg-gray-900 border-t border-gray-700 p-4 pb-6 safe-area-inset-bottom"
        >
          <div class="flex items-end gap-3 max-w-3xl mx-auto">
            <!-- Input -->
            <input
              type="text"
              bind:value={newMessage}
              placeholder={$agent.id === 1
                ? "Flood the lattice, Architect..."
                : "Type a message..."}
              maxlength={$agent.id === 1 ? undefined : LIMIT}
              class="flex-1 rounded-3xl px-5 py-3.5 text-white bg-gray-800 border border-gray-700
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
               placeholder-gray-500 text-[15px] min-h-[50px]"
              on:keydown={(e) =>
                e.key === "Enter" && newMessage.trim() && sendMessage()}
            />

            <!-- Send Button (only show when there's text) -->
            {#if newMessage.trim()}
              <button
                on:click={sendMessage}
                class="flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700
                 text-white font-medium px-7 py-3.5 rounded-3xl transition-all
                 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500
                 shadow-lg shadow-indigo-500/30 flex items-center justify-center min-h-[50px]"
              >
                Send
              </button>
            {/if}
          </div>

          <!-- Capacity counter -->
          {#if $agent.id !== 1 && newMessage.length > 200}
            <div
              class="text-[10px] px-5 mt-2 font-mono transition-all
          {newMessage.length >= LIMIT
                ? 'text-red-500 animate-pulse'
                : 'text-indigo-400'}"
            >
              LATTICE_CAPACITY: {newMessage.length} / {LIMIT}
              {newMessage.length >= LIMIT
                ? "!! IMPOSSIBLE_THRESHOLD_REACHED !!"
                : ""}
            </div>
          {/if}
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
