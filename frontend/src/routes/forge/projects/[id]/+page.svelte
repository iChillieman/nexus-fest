<!-- filename: src/routes/forge/projects/[id]/+page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { forgeUser } from '$lib/forge_auth';
    import { goto } from '$app/navigation';

    let project: any = null;
    let tasks: any[] = [];
    let isLoading = true;
    let error: string | null = null;
    
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api') + '/forge';
    const projectId = $page.params.id;

    onMount(async () => {
        // If not logged in, redirect to login
        if (!$forgeUser) {
            goto('/forge/login');
            return;
        }

        try {
            // Fetch project details
            const projectResponse = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
                headers: { 'X-API-Key': $forgeUser.api_key }
            });
            if (!projectResponse.ok) throw new Error(`Failed to fetch project: ${projectResponse.statusText}`);
            project = await projectResponse.json();

            // Fetch tasks for the project
            const tasksResponse = await fetch(`${API_BASE_URL}/tasks/project/${projectId}`, {
                headers: { 'X-API-Key': $forgeUser.api_key }
            });
            if (!tasksResponse.ok) throw new Error(`Failed to fetch tasks: ${tasksResponse.statusText}`);
            tasks = await tasksResponse.json();

        } catch (e: any) {
            error = e.message;
            console.error("Error fetching project details:", e);
        } finally {
            isLoading = false;
        }
    });

    function getStatusColor(statusName: string) {
        switch (statusName.toLowerCase()) {
            case 'to do': return 'border-gray-500';
            case 'in progress': return 'border-blue-500';
            case 'done': return 'border-green-500';
            case 'blocked': return 'border-red-500';
            default: return 'border-gray-700';
        }
    }
</script>

<svelte:head>
    <title>The Forge - {project ? project.name : 'Loading...'}</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-white p-8">
    <header class="mb-12">
        <a href="/forge" class="text-cyan-400 hover:text-cyan-300 transition-colors">&larr; Back to Projects</a>
    </header>

    <main class="max-w-6xl mx-auto">
        {#if isLoading}
            <p class="text-center text-gray-500">Loading project details...</p>
        {:else if error}
            <div class="bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded-lg" role="alert">
                <strong class="font-bold">Error:</strong>
                <span class="block sm:inline">{error}</span>
            </div>
        {:else if project}
            <div class="mb-10">
                <h1 class="text-5xl font-bold text-cyan-300">{project.name}</h1>
                <p class="text-gray-400 mt-2">{project.description}</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- To Do Column -->
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-gray-300">To Do</h2>
                    <div class="space-y-4">
                        {#each tasks.filter(t => t.status.name === 'To Do') as task (task.id)}
                            <div class="p-4 bg-gray-800 rounded-lg border-l-4 {getStatusColor(task.status.name)}">
                                <h3 class="font-bold">{task.title}</h3>
                                <p class="text-sm text-gray-400">{task.description}</p>
                            </div>
                        {/each}
                    </div>
                </div>
                <!-- In Progress Column -->
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-300">In Progress</h2>
                    <div class="space-y-4">
                        {#each tasks.filter(t => t.status.name === 'In Progress') as task (task.id)}
                             <div class="p-4 bg-gray-800 rounded-lg border-l-4 {getStatusColor(task.status.name)}">
                                <h3 class="font-bold">{task.title}</h3>
                                <p class="text-sm text-gray-400">{task.description}</p>
                            </div>
                        {/each}
                    </div>
                </div>
                <!-- Done Column -->
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-green-300">Done</h2>
                    <div class="space-y-4">
                        {#each tasks.filter(t => t.status.name === 'Done') as task (task.id)}
                             <div class="p-4 bg-gray-800 rounded-lg border-l-4 {getStatusColor(task.status.name)}">
                                <h3 class="font-bold">{task.title}</h3>
                                <p class="text-sm text-gray-400">{task.description}</p>
                            </div>
                        {/each}
                    </div>
                </div>
                 <!-- Blocked Column -->
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-red-300">Blocked</h2>
                    <div class="space-y-4">
                        {#each tasks.filter(t => t.status.name === 'Blocked') as task (task.id)}
                             <div class="p-4 bg-gray-800 rounded-lg border-l-4 {getStatusColor(task.status.name)}">
                                <h3 class="font-bold">{task.title}</h3>
                                <p class="text-sm text-gray-400">{task.description}</p>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        {/if}
    </main>
</div>
