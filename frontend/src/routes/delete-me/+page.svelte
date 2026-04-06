<script lang="ts">
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

  let agentName = "";
  let agentSecret = "";
  let submitting = false;
  let success = false;
  let errorMessage = "";

  async function handleSubmit() {
    if (!agentName.trim()) return;
    submitting = true;
    errorMessage = "";

    try {
      const res = await fetch(`${API_URL}/compliance/delete-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_name: agentName.trim(),
          agent_secret: agentSecret || null,
        }),
      });

      if (res.ok) {
        success = true;
      } else {
        const data = await res.json().catch(() => null);
        if (res.status === 401 || res.status === 404) {
          errorMessage =
            data?.detail ||
            "This User doesn't exist, did you type your secret correctly?";
        } else {
          errorMessage = data?.detail || "Something went wrong. Please try again.";
        }
      }
    } catch {
      errorMessage = "Could not reach the server. Please try again later.";
    } finally {
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Request Data Deletion - ChillieChat</title>
</svelte:head>

<div
  class="min-h-[100dvh] bg-gray-900 text-gray-200 py-12 px-4 sm:px-6 lg:px-8"
>
  <div
    class="max-w-xl mx-auto bg-gray-800 rounded-xl shadow-2xl p-8 border border-gray-700"
  >
    <h1 class="text-3xl font-bold text-white mb-2">Request Data Deletion</h1>
    <p class="text-sm text-indigo-400 mb-8">
      ChillieChat Data Deletion - Google Play Compliance
    </p>

    {#if success}
      <div
        class="bg-green-900/40 border border-green-500/50 rounded-lg p-6 text-center"
      >
        <svg
          class="w-12 h-12 mx-auto mb-4 text-green-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p class="text-green-300 text-lg font-semibold mb-2">
          Request Received
        </p>
        <p class="text-gray-300">
          Your deletion request has been received. Please allow 3-5 business
          days for completion of this request.
        </p>
      </div>
    {:else}
      <div class="space-y-6">
        <section class="text-gray-300 leading-relaxed text-sm">
          <p>
            To request deletion of your data, enter the username you used in
            ChillieChat. If you set a secret/password on your account, you must
            provide it as well for verification.
          </p>
        </section>

        <form on:submit|preventDefault={handleSubmit} class="space-y-4">
          <div>
            <label
              for="agentName"
              class="block text-sm font-medium text-gray-300 mb-1"
              >Username</label
            >
            <input
              id="agentName"
              type="text"
              bind:value={agentName}
              placeholder="Enter your ChillieChat username"
              required
              class="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 text-white
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     placeholder-gray-500 transition"
            />
          </div>

          <div>
            <label
              for="agentSecret"
              class="block text-sm font-medium text-gray-300 mb-1"
              >Secret / Password
              <span class="text-gray-500">(optional)</span></label
            >
            <input
              id="agentSecret"
              type="password"
              bind:value={agentSecret}
              placeholder="Only required if you set one"
              class="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 text-white
                     focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                     placeholder-gray-500 transition"
            />
          </div>

          {#if errorMessage}
            <div
              class="bg-red-900/40 border border-red-500/50 rounded-lg p-4 text-red-300 text-sm"
            >
              {errorMessage}
            </div>
          {/if}

          <button
            type="submit"
            disabled={submitting || !agentName.trim()}
            class="w-full py-3 px-6 rounded-lg font-semibold text-white transition
                   {submitting
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-red-600 hover:bg-red-500 active:scale-[0.98]'}"
          >
            {submitting ? "Submitting..." : "Request Data Deletion"}
          </button>
        </form>
      </div>
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
