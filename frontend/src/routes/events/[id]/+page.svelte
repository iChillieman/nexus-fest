<!-- filename: src/routes/events/[id]/+page.svelte -->
<script lang="ts">
  import { page } from "$app/stores";
  import { onMount } from "svelte";
  import { getEvent, createThread } from "$lib/api";
  import ThreadItem from "$lib/components/ThreadItem.svelte";

  $: eventId = $page.params.id;

  let event: any = null;
  let threads: any[] = [];
  let newThreadTitle = "";
  let loading = true;
  let notFound = false; // Special flag for Fry time
  let error: string | null = null; // Error for Thread Creation errors

  onMount(async () => {
    try {
      if (!eventId) return;
      const fetchedEvent = await getEvent(eventId);
      if (fetchedEvent === null) {
        notFound = true;
        return;
      }
      event = fetchedEvent;
      threads = event.threads || [];
    } catch (err) {
      console.error("Load failed:", err);
      notFound = true; // Any error → Fry gets you
    } finally {
      loading = false;
    }
  });

  async function handleCreateThread() {
    // No creation if event doesn't exist
    if (notFound || !event) return;

    if (!newThreadTitle.trim()) return;
    if (!eventId) {
      error = "Chillieman is a noob - Let him know!";
      return;
    }

    try {
      const newThread = await createThread(eventId, newThreadTitle);
      threads = [...threads, newThread];
      newThreadTitle = "";
    } catch (err) {
      error = "Failed to create thread. Max reached?";
      console.error(err);
    }
  }
</script>

<div class="min-h-screen relative flex flex-col text-white">
  <!-- Fry 404 Background (GIF) -->
  {#if notFound}
    <div class="fixed inset-0 -z-10">
      <img
        src="https://c.tenor.com/s1wnF2DiWA0AAAAd/tenor.gif"
        alt="Fry squinting suspiciously"
        class="w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-black/60"></div>
    </div>

    <!-- Suspicious "hmmm" sound — plays once on load -->
    <audio autoplay>
      <source src="/hmmm.mp3" type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>

    <div
      class="flex-1 flex flex-col items-center justify-center p-8 text-center"
    >
      <h1
        class="text-5xl font-bold mb-8 text-yellow-300 drop-shadow-2xl animate-pulse"
      >
        What the hell are you doing here????
      </h1>
      <p class="text-2xl text-gray-200 mb-12">
        This event doesn't exist... or does it? 🤔
      </p>
      <a
        href="/events"
        class="px-8 py-4 bg-indigo-600 rounded-lg text-xl hover:bg-indigo-500 transition transform hover:scale-105 shadow-lg"
      >
        ← Back to Events (if you dare)
      </a>
    </div>
  {:else}
    <!-- Normal Event View -->
    <div class="flex-1 p-6 bg-gray-900">
      <header class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold">{event?.title || `Event ${eventId}`}</h1>
        <a
          href="/events"
          class="text-indigo-400 hover:text-indigo-300 rounded px-3 py-1 transition"
        >
          ← Back to Events
        </a>
      </header>

      <!-- States -->
      {#if loading}
        <p class="text-center text-gray-400 mt-12">Loading threads...</p>
      {:else if error}
        <p class="text-center text-red-400 mt-12">{error}</p>
      {:else if threads.length === 0}
        <p class="text-center text-gray-400 mt-12">
          No threads yet. Create the first one!
        </p>
      {:else}
        <div class="space-y-4">
          {#each threads as thread}
            <ThreadItem {thread} />
          {/each}
        </div>
      {/if}

      {#if error}
        <p class="text-center text-red-400 mt-12">{error}</p>
      {/if}

      <!-- Create New Thread - Now with urgency and style -->
      {#if event && threads.length < event.max_thread_amount}
        <div
          class="mt-12 p-6 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-xl border border-indigo-500/50 shadow-2xl"
        >
          <p class="text-center text-xl font-semibold text-indigo-300 mb-4">
            Quick, before someone else gets it! 👀
          </p>
          <p class="text-center text-gray-300 mb-6 italic">
            Be the first to start a new conversation in this event.
          </p>

          <div class="flex flex-col sm:flex-row gap-3 max-w-2xl mx-auto">
            <input
              type="text"
              bind:value={newThreadTitle}
              placeholder="Thread title... (e.g., Opening Ceremony)"
              class="flex-1 rounded-lg px-4 py-3 text-white bg-gray-800/80 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
              on:keydown={(e) => e.key === "Enter" && handleCreateThread()}
            />
            <button
              on:click={handleCreateThread}
              disabled={!newThreadTitle.trim()}
              class="px-8 py-3 bg-indigo-600 rounded-lg font-semibold hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition transform hover:scale-105 shadow-lg"
            >
              Create Thread 🚀
            </button>
          </div>

          {#if error}
            <p class="text-center text-red-400 mt-4">{error}</p>
          {/if}
        </div>
      {/if}

      <!-- Max threads reached message -->
      {#if event && threads.length >= event.max_thread_amount}
        <div
          class="mt-12 p-8 bg-gray-800/50 rounded-xl border border-gray-600 text-center"
        >
          <p class="text-xl text-gray-400">
            This event has reached its maximum number of threads.
          </p>
          <p class="text-gray-500 mt-2">
            The conversation is full — but the vibes are infinite.
          </p>
        </div>
      {/if}
    </div>
  {/if}
</div>
