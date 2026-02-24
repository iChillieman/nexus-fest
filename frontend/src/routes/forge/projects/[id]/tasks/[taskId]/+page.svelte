<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { forgeUser, forgeLogout } from '$lib/forge_auth';
    import { goto } from '$app/navigation';

    let task: any = null;
    let newComment = "";
    let isEditingDetail = false;
    let detailBuffer = "";
    let isLoading = true;
    let error: string | null = null;

    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/forge';
    
    // Params from URL
    const projectId = $page.params.id; 
    const taskId = $page.params.taskId;

    onMount(async () => {
        if (!$forgeUser) {
            goto('/forge/login');
            return;
        }
        await fetchTask();
    });

    async function fetchTask() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, { # Wait, endpoint is just /tasks/{id}? No project ID needed for GET /tasks/{id}
                headers: { 'X-API-Key': $forgeUser?.api_key || '' }
            });
            
            if (response.status === 401 || response.status === 403) {
                await forgeLogout();
                return;
            }

            if (!response.ok) throw new Error("Failed to fetch task");
            task = await response.json();
            detailBuffer = task.detail || "";
        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }

    async function saveDetail() {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': $forgeUser?.api_key || ''
                },
                body: JSON.stringify({ detail: detailBuffer })
            });

            if (!response.ok) throw new Error("Failed to update detail");
            task = await response.json();
            isEditingDetail = false;
        } catch (e: any) {
            alert(e.message);
        }
    }

    async function postComment() {
        if (!newComment.trim()) return;
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': $forgeUser?.api_key || ''
                },
                body: JSON.stringify({ content: newComment })
            });

            if (!response.ok) throw new Error("Failed to post comment");
            
            // Re-fetch task to see new comment (since comments are embedded in read model)
            await fetchTask(); 
            newComment = "";
        } catch (e: any) {
            alert(e.message);
        }
    }

    function formatDate(ts: number) {
        return new Date(ts * 1000).toLocaleString();
    }
</script>

<svelte:head>
    <title>Task Detail - {task ? task.title : 'Loading...'}</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-white p-8">
    <header class="mb-8 max-w-4xl mx-auto">
        <a href="/forge/projects/{projectId}" class="text-cyan-400 hover:text-cyan-300 transition-colors mb-4 inline-block">&larr; Back to Board</a>
        {#if task}
            <div class="flex justify-between items-start">
                <div>
                    <h1 class="text-4xl font-bold text-gray-100">{task.title}</h1>
                    <div class="flex items-center gap-4 mt-2 text-sm text-gray-400">
                        <span class="bg-gray-800 px-2 py-1 rounded border border-gray-700">Status: <span class="text-white font-semibold">{task.status.name}</span></span>
                        {#if task.assigned_worker}
                            <span class="bg-blue-900/30 px-2 py-1 rounded border border-blue-800 text-blue-300">Worker: {task.assigned_worker.name}</span>
                        {:else}
                            <span class="bg-gray-800 px-2 py-1 rounded border border-gray-700 text-gray-500">Unassigned</span>
                        {/if}
                        <span>Created: {formatDate(task.created_at)}</span>
                    </div>
                </div>
            </div>
        {/if}
    </header>

    <main class="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {#if isLoading}
            <p class="text-gray-500 col-span-3 text-center">Loading task details...</p>
        {:else if error}
            <div class="col-span-3 bg-red-900 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
                <strong>Error:</strong> {error}
            </div>
        {:else if task}
            <!-- Left Column: Details & Blueprint -->
            <div class="lg:col-span-2 space-y-8">
                
                <!-- Description -->
                <section class="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h2 class="text-xl font-semibold mb-2 text-gray-300">Description</h2>
                    <p class="text-gray-400 whitespace-pre-wrap">{task.description || "No description provided."}</p>
                </section>

                <!-- Detail (The Blueprint) -->
                <section class="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-semibold text-cyan-300">Blueprint (Detail)</h2>
                        {#if !isEditingDetail}
                            <button onclick={() => isEditingDetail = true} class="text-sm text-cyan-400 hover:text-cyan-300">Edit</button>
                        {/if}
                    </div>
                    
                    {#if isEditingDetail}
                        <textarea 
                            bind:value={detailBuffer}
                            class="w-full bg-gray-900 border border-gray-600 rounded p-4 text-gray-300 h-64 focus:border-cyan-500 outline-none"
                            placeholder="Enter detailed instructions or blueprint here..."
                        ></textarea>
                        <div class="flex justify-end gap-2 mt-2">
                            <button onclick={() => { isEditingDetail = false; detailBuffer = task.detail || ""; }} class="px-3 py-1 text-gray-400 hover:text-white">Cancel</button>
                            <button onclick={saveDetail} class="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded">Save</button>
                        </div>
                    {:else}
                        <div class="prose prose-invert max-w-none text-gray-300 whitespace-pre-wrap">
                            {task.detail || "No detailed blueprint yet."}
                        </div>
                    {/if}
                </section>

                 <!-- Worker Notes (Read Only) -->
                 <section class="bg-gray-800 p-6 rounded-lg border border-gray-700 opacity-90">
                    <h2 class="text-xl font-semibold mb-2 text-yellow-500">Worker Notes</h2>
                    <div class="bg-black/30 p-4 rounded text-gray-400 font-mono text-sm whitespace-pre-wrap">
                        {task.notes || "No notes from the worker."}
                    </div>
                </section>
            </div>

            <!-- Right Column: Comments (The Log) -->
            <div class="lg:col-span-1">
                <section class="bg-gray-800 p-6 rounded-lg border border-gray-700 h-full flex flex-col">
                    <h2 class="text-xl font-semibold mb-4 text-gray-300">Log / Comments</h2>
                    
                    <div class="flex-grow overflow-y-auto space-y-4 mb-4 max-h-[600px] pr-2">
                        {#each task.comments as comment (comment.id)}
                            <div class="bg-gray-900 p-3 rounded border {comment.author_type === 'WORKER' ? 'border-blue-800' : 'border-gray-700'}">
                                <div class="flex justify-between items-baseline mb-1">
                                    <span class="font-bold text-xs {comment.author_type === 'WORKER' ? 'text-blue-400' : 'text-cyan-400'}">
                                        {comment.author_type === 'WORKER' ? 'Worker' : 'User'} {comment.author_id}
                                    </span>
                                    <span class="text-[10px] text-gray-600">{formatDate(comment.created_at)}</span>
                                </div>
                                <p class="text-sm text-gray-300">{comment.content}</p>
                            </div>
                        {/each}
                        {#if task.comments.length === 0}
                            <p class="text-gray-500 text-sm italic text-center py-4">No comments yet.</p>
                        {/if}
                    </div>

                    <div class="mt-auto">
                        <textarea 
                            bind:value={newComment}
                            class="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white mb-2 focus:border-cyan-500 outline-none"
                            placeholder="Add a comment..."
                            rows="3"
                        ></textarea>
                        <button 
                            onclick={postComment}
                            class="w-full bg-cyan-700 hover:bg-cyan-600 text-white text-sm py-2 rounded transition-colors"
                        >
                            Post Comment
                        </button>
                    </div>
                </section>
            </div>
        {/if}
    </main>
</div>
