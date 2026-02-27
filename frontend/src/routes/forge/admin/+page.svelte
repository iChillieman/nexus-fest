<script lang="ts">
    import { onMount } from 'svelte';
    import { forgeUser, forgeLogout } from '$lib/forge_auth';
    import { goto } from '$app/navigation';

    let keys: any[] = [];
    let isLoading = true;
    let error: string | null = null;
    let showCreateModal = false;
    let newKeyName = "";
    let createdKey: any = null; // Stores the raw key response after creation

    // In Production, VITE_API_URL appends /api for us... but we need to explictly set it for localhost:8000
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api') + '/forge/auth';

    onMount(async () => {
        if (!$forgeUser) {
            goto('/forge/login');
            return;
        }
        await fetchKeys();
    });

    async function fetchKeys() {
        try {
            const response = await fetch(`${API_BASE_URL}/keys`, {
                headers: { 'X-API-Key': $forgeUser?.api_key || '' }
            });
            if (response.status === 401 || response.status === 403) {
                await forgeLogout();
                return;
            }
            if (!response.ok) throw new Error("Failed to fetch keys");
            keys = await response.json();
        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }

    async function createKey() {
        if (!newKeyName.trim()) return;
        try {
            const response = await fetch(`${API_BASE_URL}/keys`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': $forgeUser?.api_key || ''
                },
                body: JSON.stringify({ name: newKeyName })
            });
            if (!response.ok) throw new Error("Failed to create key");
            createdKey = await response.json();
            await fetchKeys(); // Refresh list
            newKeyName = "";
        } catch (e: any) {
            alert(e.message);
        }
    }

    async function deleteKey(id: number) {
        if (!confirm("Are you sure you want to revoke this key? This action cannot be undone.")) return;
        try {
            const response = await fetch(`${API_BASE_URL}/keys/${id}`, {
                method: 'DELETE',
                headers: { 'X-API-Key': $forgeUser?.api_key || '' }
            });
            if (!response.ok) throw new Error("Failed to delete key");
            await fetchKeys();
        } catch (e: any) {
            alert(e.message);
        }
    }

    async function renameKey(id: number, currentName: string) {
        const newName = prompt("Enter new name:", currentName);
        if (!newName || newName === currentName) return;

        try {
            const response = await fetch(`${API_BASE_URL}/keys/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': $forgeUser?.api_key || ''
                },
                body: JSON.stringify({ name: newName })
            });
            if (!response.ok) throw new Error("Failed to rename key");
            await fetchKeys();
        } catch (e: any) {
            alert(e.message);
        }
    }

    function formatDate(ts: number) {
        return new Date(ts * 1000).toLocaleString();
    }
</script>

<svelte:head>
    <title>Forge Admin - API Keys</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 text-white p-8">
    <header class="mb-12 flex justify-between items-center max-w-4xl mx-auto">
        <div>
            <h1 class="text-3xl font-bold text-cyan-400">Key Management</h1>
            <p class="text-gray-400">Manage your API tokens and active sessions.</p>
        </div>
        <button 
            onclick={() => showCreateModal = true}
            class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded transition-colors"
        >
            + New API Token
        </button>
    </header>

    <main class="max-w-4xl mx-auto space-y-12">
        <!-- API Tokens Section -->
        <section>
            <h2 class="text-2xl font-semibold mb-4 text-gray-200 border-b border-gray-700 pb-2">API Tokens (Permanent)</h2>
            <div class="space-y-4">
                {#each keys.filter(k => !k.expires_at) as key (key.id)}
                    <div class="bg-gray-800 p-4 rounded-lg flex justify-between items-center border border-gray-700">
                        <div>
                            <div class="flex items-center gap-2">
                                <h3 class="font-bold text-lg">{key.name}</h3>
                                <button onclick={() => renameKey(key.id, key.name)} class="text-xs text-gray-500 hover:text-cyan-400">✏️</button>
                            </div>
                            <p class="text-xs text-gray-500">Created: {formatDate(key.created_at)}</p>
                        </div>
                        <button onclick={() => deleteKey(key.id)} class="text-red-400 hover:text-red-300 px-3 py-1 border border-red-900 bg-red-900/20 rounded">Revoke</button>
                    </div>
                {/each}
                {#if keys.filter(k => !k.expires_at).length === 0}
                    <p class="text-gray-500 italic">No permanent API tokens found.</p>
                {/if}
            </div>
        </section>

        <!-- Sessions Section -->
        <section>
            <h2 class="text-2xl font-semibold mb-4 text-gray-200 border-b border-gray-700 pb-2">Active Sessions (Temporary)</h2>
            <div class="space-y-4">
                {#each keys.filter(k => k.expires_at) as key (key.id)}
                    <div class="bg-gray-800 p-4 rounded-lg flex justify-between items-center border border-gray-700 opacity-80">
                         <div>
                            <div class="flex items-center gap-2">
                                <h3 class="font-bold text-lg">{key.name}</h3>
                                <button onclick={() => renameKey(key.id, key.name)} class="text-xs text-gray-500 hover:text-cyan-400">✏️</button>
                            </div>
                            <p class="text-xs text-gray-500">Created: {formatDate(key.created_at)}</p>
                            <p class="text-xs text-yellow-500">Expires: {formatDate(key.expires_at)}</p>
                        </div>
                        <button onclick={() => deleteKey(key.id)} class="text-red-400 hover:text-red-300 px-3 py-1 border border-red-900 bg-red-900/20 rounded">End Session</button>
                    </div>
                {/each}
                 {#if keys.filter(k => k.expires_at).length === 0}
                    <p class="text-gray-500 italic">No active sessions found.</p>
                {/if}
            </div>
        </section>
    </main>

    <!-- Create Key Modal -->
    {#if showCreateModal}
        <div class="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
            <div class="bg-gray-800 p-6 rounded-lg max-w-md w-full border border-gray-600 shadow-xl">
                {#if !createdKey}
                    <h2 class="text-xl font-bold mb-4">Create New API Token</h2>
                    <input 
                        type="text" 
                        bind:value={newKeyName} 
                        placeholder="Token Name (e.g. CI/CD Pipeline)" 
                        class="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white focus:border-cyan-500 outline-none"
                    />
                    <div class="flex justify-end gap-2">
                        <button onclick={() => showCreateModal = false} class="px-4 py-2 text-gray-300 hover:text-white">Cancel</button>
                        <button onclick={createKey} class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded">Create</button>
                    </div>
                {:else}
                     <h2 class="text-xl font-bold mb-4 text-green-400">Token Created!</h2>
                     <p class="text-sm text-gray-300 mb-2">Copy this key now. You won't see it again.</p>
                     <div class="bg-black p-3 rounded border border-gray-700 font-mono text-cyan-300 break-all select-all mb-4">
                        {createdKey.api_key}
                     </div>
                     <div class="flex justify-end">
                        <button onclick={() => { showCreateModal = false; createdKey = null; }} class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded">Done</button>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>
