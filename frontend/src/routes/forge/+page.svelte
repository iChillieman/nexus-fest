<script lang="ts">
    import { onMount } from 'svelte';
    import { forgeUser } from '$lib/forge_auth';
    import { goto } from '$app/navigation';

    // This will hold the data fetched from our API
    let projects: any[] = [];
    let isLoading = true;
    let error: string | null = null;

    // The API endpoint for our backend.
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/forge';

    onMount(async () => {
        // If not logged in, redirect to login
        if (!$forgeUser) {
            goto('/forge/login');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/projects/`, {
                headers: {
                    'X-API-Key': $forgeUser.api_key
                }
            });
            
            if (response.status === 403) {
                // Key invalid or expired
                // We don't auto-logout here to avoid loops, just show error or redirect
                goto('/forge/login');
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            projects = await response.json();
        } catch (e: any) {
            error = e.message;
            console.error("Error fetching projects:", e);
        } finally {
            isLoading = false;
        }
    });
</script>

<svelte:head>
    <title>The Forge - Projects</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-white p-8">
    <header class="mb-12 text-center">
        <h1 class="text-5xl font-bold text-cyan-400">The Forge</h1>
        <p class="text-gray-400 mt-2">A window into the workshop of Daedalus.</p>
    </header>

    <main class="max-w-4xl mx-auto">
        {#if isLoading}
            <p class="text-center text-gray-500">Forging the project list...</p>
        {:else if error}
            <div class="bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded-lg" role="alert">
                <strong class="font-bold">Error:</strong>
                <span class="block sm:inline">{error}</span>
            </div>
        {:else if projects.length === 0}
            <p class="text-center text-gray-500">The forge is quiet. No projects have been created yet.</p>
        {:else}
            <div class="space-y-4">
                {#each projects as project}
                    <a href="/forge/projects/{project.id}" class="block p-6 bg-gray-800 rounded-lg border border-gray-700 hover:bg-gray-700 transition-colors duration-300">
                        <h2 class="text-2xl font-semibold text-cyan-300">{project.name}</h2>
                        <p class="text-gray-400 mt-2">{project.description || 'No description provided.'}</p>
                        <div class="text-xs text-gray-500 mt-4">
                            <!-- Handle integer timestamp from Nexus DB -->
                            Created: {new Date(project.created_at * 1000).toLocaleString()}
                        </div>
                    </a>
                {/each}
            </div>
        {/if}
    </main>
</div>
