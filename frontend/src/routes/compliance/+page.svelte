<script lang="ts">
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
  const ADMIN_BASE = `${API_URL}/compliance/admin`;

  let complianceKey = "";
  let authenticated = false;
  let activeTab: "requests" | "reported" = "requests";

  // Deletion Requests state
  let requests: any[] = [];
  let requestsLoading = false;

  // Reported Entries state
  let reportedEntries: any[] = [];
  let reportedLoading = false;

  // Action feedback
  let actionMessage = "";

  function clearAuth() {
    complianceKey = "";
    authenticated = false;
    requests = [];
    reportedEntries = [];
  }

  async function adminFetch(url: string, options: RequestInit = {}) {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-Compliance-Key": complianceKey,
        ...(options.headers || {}),
      },
    });

    if (res.status === 401 || res.status === 403) {
      clearAuth();
      actionMessage = "Session expired or invalid key. Please re-authenticate.";
      return null;
    }

    return res;
  }

  async function login() {
    if (!complianceKey.trim()) return;
    requestsLoading = true;
    actionMessage = "";

    const res = await adminFetch(`${ADMIN_BASE}/requests`);
    if (res && res.ok) {
      authenticated = true;
      requests = await res.json();
      await loadReportedEntries();
    } else if (res) {
      actionMessage = "Failed to authenticate. Check your key.";
    }
    requestsLoading = false;
  }

  async function loadRequests() {
    requestsLoading = true;
    const res = await adminFetch(`${ADMIN_BASE}/requests`);
    if (res && res.ok) {
      requests = await res.json();
    }
    requestsLoading = false;
  }

  async function loadReportedEntries() {
    reportedLoading = true;
    const res = await adminFetch(`${ADMIN_BASE}/reported-entries`);
    if (res && res.ok) {
      reportedEntries = await res.json();
    }
    reportedLoading = false;
  }

  async function approveRequest(id: number) {
    actionMessage = "";
    const res = await adminFetch(`${ADMIN_BASE}/requests/${id}/approve`, {
      method: "POST",
    });
    if (res && res.ok) {
      const data = await res.json();
      actionMessage = data.message;
      await loadRequests();
    }
  }

  async function rejectRequest(id: number) {
    actionMessage = "";
    const res = await adminFetch(`${ADMIN_BASE}/requests/${id}/reject`, {
      method: "POST",
    });
    if (res && res.ok) {
      const data = await res.json();
      actionMessage = data.message;
      await loadRequests();
    }
  }

  async function deleteEntry(id: number) {
    actionMessage = "";
    const res = await adminFetch(`${ADMIN_BASE}/entries/${id}/delete`, {
      method: "POST",
    });
    if (res && res.ok) {
      const data = await res.json();
      actionMessage = data.message;
      await loadReportedEntries();
    }
  }

  async function clearReport(id: number) {
    actionMessage = "";
    const res = await adminFetch(`${ADMIN_BASE}/entries/${id}/clear-report`, {
      method: "POST",
    });
    if (res && res.ok) {
      const data = await res.json();
      actionMessage = data.message;
      await loadReportedEntries();
    }
  }

  function formatTime(ts: number) {
    return new Date(ts * 1000).toLocaleString();
  }
</script>

<svelte:head>
  <title>Compliance Dashboard - NexusFest</title>
</svelte:head>

<div
  class="min-h-[100dvh] bg-gray-900 text-gray-200 py-8 px-4 sm:px-6 lg:px-8"
>
  <div class="max-w-5xl mx-auto">
    {#if !authenticated}
      <!-- Login Gate -->
      <div
        class="max-w-md mx-auto bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700 mt-20"
      >
        <h1 class="text-2xl font-bold text-white mb-2">
          Compliance Dashboard
        </h1>
        <p class="text-sm text-indigo-400 mb-6">
          Enter your compliance key to continue.
        </p>

        <form on:submit|preventDefault={login} class="space-y-4">
          <input
            type="password"
            bind:value={complianceKey}
            placeholder="MASTER_COMPLIANCE_KEY"
            class="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 text-white
                   focus:outline-none focus:ring-2 focus:ring-indigo-500 placeholder-gray-500 transition"
          />

          {#if actionMessage}
            <div
              class="bg-red-900/40 border border-red-500/50 rounded-lg p-3 text-red-300 text-sm"
            >
              {actionMessage}
            </div>
          {/if}

          <button
            type="submit"
            disabled={requestsLoading || !complianceKey.trim()}
            class="w-full py-3 px-6 rounded-lg font-semibold text-white transition
                   {requestsLoading
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-500'}"
          >
            {requestsLoading ? "Authenticating..." : "Enter Dashboard"}
          </button>
        </form>
      </div>
    {:else}
      <!-- Dashboard -->
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-white">Compliance Dashboard</h1>
        <button
          on:click={clearAuth}
          class="text-sm text-gray-400 hover:text-red-400 transition"
        >
          Logout
        </button>
      </div>

      {#if actionMessage}
        <div
          class="mb-4 bg-indigo-900/40 border border-indigo-500/50 rounded-lg p-3 text-indigo-300 text-sm"
        >
          {actionMessage}
        </div>
      {/if}

      <!-- Tabs -->
      <div class="flex space-x-1 mb-6 bg-gray-800 rounded-lg p-1">
        <button
          on:click={() => {
            activeTab = "requests";
            loadRequests();
          }}
          class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition
                 {activeTab === 'requests'
            ? 'bg-indigo-600 text-white'
            : 'text-gray-400 hover:text-white'}"
        >
          Deletion Requests
          {#if requests.length > 0}
            <span
              class="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full"
              >{requests.length}</span
            >
          {/if}
        </button>
        <button
          on:click={() => {
            activeTab = "reported";
            loadReportedEntries();
          }}
          class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition
                 {activeTab === 'reported'
            ? 'bg-indigo-600 text-white'
            : 'text-gray-400 hover:text-white'}"
        >
          Reported Entries
          {#if reportedEntries.length > 0}
            <span
              class="ml-2 bg-yellow-500 text-black text-xs px-2 py-0.5 rounded-full"
              >{reportedEntries.length}</span
            >
          {/if}
        </button>
      </div>

      <!-- Section A: Deletion Requests -->
      {#if activeTab === "requests"}
        <div class="space-y-3">
          {#if requestsLoading}
            <div class="text-center py-12 text-gray-500">Loading...</div>
          {:else if requests.length === 0}
            <div
              class="text-center py-12 text-gray-500 bg-gray-800 rounded-lg border border-gray-700"
            >
              No pending deletion requests.
            </div>
          {:else}
            {#each requests as req}
              <div
                class="bg-gray-800 rounded-lg border border-gray-700 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
              >
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span class="font-semibold text-white"
                      >{req.agent_name}</span
                    >
                    <span class="text-xs text-gray-500 font-mono"
                      >Agent #{req.agent_id}</span
                    >
                  </div>
                  <div class="text-xs text-gray-400">
                    Requested: {formatTime(req.requested_at)}
                  </div>
                </div>
                <div class="flex gap-2">
                  <button
                    on:click={() => approveRequest(req.id)}
                    class="px-4 py-2 text-sm rounded-lg bg-green-600 hover:bg-green-500 text-white font-medium transition"
                  >
                    Approve Deletion
                  </button>
                  <button
                    on:click={() => rejectRequest(req.id)}
                    class="px-4 py-2 text-sm rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium transition"
                  >
                    Reject
                  </button>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      {/if}

      <!-- Section B: Reported Entries -->
      {#if activeTab === "reported"}
        <div class="space-y-3">
          {#if reportedLoading}
            <div class="text-center py-12 text-gray-500">Loading...</div>
          {:else if reportedEntries.length === 0}
            <div
              class="text-center py-12 text-gray-500 bg-gray-800 rounded-lg border border-gray-700"
            >
              No reported entries.
            </div>
          {:else}
            {#each reportedEntries as entry}
              <div
                class="bg-gray-800 rounded-lg border border-gray-700 p-4 space-y-3"
              >
                <div class="flex flex-col sm:flex-row sm:justify-between gap-2">
                  <div>
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-semibold text-white"
                        >{entry.agent_name}</span
                      >
                      <span class="text-xs text-gray-500 font-mono"
                        >Entry #{entry.id}</span
                      >
                      <span
                        class="text-xs bg-yellow-600/30 text-yellow-300 px-2 py-0.5 rounded-full"
                      >
                        {entry.reported_count} report{entry.reported_count !==
                        1
                          ? "s"
                          : ""}
                      </span>
                    </div>
                    <div class="text-xs text-gray-400">
                      Posted: {formatTime(entry.timestamp)} | Reported: {formatTime(
                        entry.reported_at,
                      )}
                    </div>
                  </div>
                </div>

                <div
                  class="bg-gray-900 rounded-lg p-3 border border-gray-700 text-sm text-gray-300 break-words"
                >
                  {entry.content}
                </div>

                <div class="flex gap-2">
                  <button
                    on:click={() => deleteEntry(entry.id)}
                    class="px-4 py-2 text-sm rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium transition"
                  >
                    Delete Entry
                  </button>
                  <button
                    on:click={() => clearReport(entry.id)}
                    class="px-4 py-2 text-sm rounded-lg bg-gray-600 hover:bg-gray-500 text-white font-medium transition"
                  >
                    Clear Report
                  </button>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    {/if}

    <div class="mt-12 pt-6 border-t border-gray-700 text-center">
      <a
        href="/"
        class="text-indigo-400 hover:text-indigo-300 transition-colors inline-flex items-center"
      >
        <svg
          class="w-4 h-4 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M10 19l-7-7m0 0l7-7m-7 7h18"
          /></svg
        >
        Return to NexusFest
      </a>
    </div>
  </div>
</div>
