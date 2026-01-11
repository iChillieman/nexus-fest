<!-- filename: src/routes/events/+page.svelte -->
<script lang="ts">
  import { getEvents } from "$lib/api";
  import { onMount } from "svelte";

  type Event = {
    id: number;
    title: string;
    description: string | null;
    start_time: number;
    end_time: number | null;
    max_thread_amount: number;
  };

  let events: Event[] = [];
  let onlyActive = false;
  let loading = true;
  let error: string | null = null;

  const imagePool = [
    "/cosmic0.jpg",
    "/cosmic1.jpg",
    "/cosmic2.jpg",
    "/cosmic3.jpg",
    "/cosmic4.jpg",
    "/cosmic5.jpg",
  ];

  function getEventImage(eventId: number): string {
    return imagePool[eventId % imagePool.length];
  }

  function getStatus(event: Event): "active" | "upcoming" | "ended" {
    const now = Math.floor(Date.now() / 1000);

    if (event.end_time && now > event.end_time) return "ended";
    if (now < event.start_time) return "upcoming";
    return "active"; // default: ongoing or no times set
  }

  onMount(async () => {
    try {
      events = await getEvents();
    } catch (err) {
      error = "Could not load events. Is the backend running?";
      console.error(err);
    } finally {
      loading = false;
    }
  });

  $: filteredEvents = events
    .filter((e) => (onlyActive ? getStatus(e) === "active" : true))
    .sort((a, b) => a.start_time - b.start_time);
</script>

<div class="min-h-screen bg-gray-900 text-white p-6">
  <header class="flex items-center justify-between mb-6">
    <h1 class="text-3xl font-bold">Events</h1>
    <label class="flex items-center space-x-2 cursor-pointer">
      <input
        type="checkbox"
        bind:checked={onlyActive}
        class="w-5 h-5 accent-indigo-500 rounded"
      />
      <span class="select-none">Only show active events</span>
    </label>
  </header>

  {#if loading}
    <p class="text-center text-gray-400 mt-20">Loading cosmic gatherings...</p>
  {:else if error}
    <p class="text-center text-red-400 mt-20">{error}</p>
  {:else if filteredEvents.length === 0}
    <p class="text-center text-gray-400 mt-20">
      {onlyActive
        ? "No active events right now."
        : "No events yet. The void awaits."}
    </p>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {#each filteredEvents as event}
        <a
          href={`/events/${event.id}`}
          class="block rounded-2xl shadow-2xl overflow-hidden relative transform transition-all hover:scale-105 hover:shadow-indigo-500/50 focus:outline-none focus:ring-4 focus:ring-indigo-500"
        >
          <div class="relative h-64">
            <img
              src={getEventImage(event.id)}
              alt={event.title}
              class="w-full h-full object-cover"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"
            ></div>
          </div>

          <div class="absolute bottom-0 left-0 right-0 p-6">
            <div class="flex justify-between items-end">
              <div>
                <h2 class="text-2xl font-bold text-white drop-shadow-lg">
                  {event.title}
                </h2>
                {#if event.description}
                  <p class="text-gray-200 text-sm mt-1 line-clamp-2">
                    {event.description}
                  </p>
                {/if}
              </div>
            </div>
          </div>

          <div
            class="absolute top-4 right-4 px-4 py-2 rounded-full bg-black/70 text-sm font-bold backdrop-blur-sm
            {getStatus(event) === 'active'
              ? 'text-green-400'
              : getStatus(event) === 'upcoming'
                ? 'text-yellow-300'
                : 'text-red-400'}"
          >
            {getStatus(event) === "active"
              ? "Active"
              : getStatus(event) === "upcoming"
                ? "Upcoming"
                : "Ended"}
          </div>
        </a>
      {/each}
    </div>
  {/if}
</div>
