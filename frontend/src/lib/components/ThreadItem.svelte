<!-- filename: src/lib/components/ThreadItem.svelte -->
<script lang="ts">
  export let thread: {
    id: number;
    title: string;
    entry_count: number;
  };
</script>

<a
  href={`/threads/${thread.id}`}
  class="block bg-gray-800 rounded-lg shadow-md p-5 flex items-center justify-between transform transition hover:scale-[1.02] hover:bg-gray-750 focus:outline-none focus:ring-2 focus:ring-indigo-500"
>
  <span class="text-xl font-semibold">{thread.title}</span>
  <span class="flex items-center space-x-2 text-sm text-gray-300">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
    <span>{thread.entry_count | 0}</span>
  </span>
</a>