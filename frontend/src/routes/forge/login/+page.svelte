<!-- filename: src/routes/forge/login/+page.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { forgeUser } from '$lib/forge_auth';

    let username = '';
    let password = '';
    let error: string | null = null;
    let isLoading = false;

    // In Production, VITE_API_URL appends /api for us... but we need to explictly set it for localhost:8000
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api') + '/forge';

    async function handleLogin() {
        isLoading = true;
        error = null;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Login failed');
            }

            const userData = await response.json();
            forgeUser.set(userData);
            goto('/forge');
        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }
</script>

<svelte:head>
    <title>The Forge - Login</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
        <h2 class="text-3xl font-bold text-cyan-400 mb-6 text-center">Enter The Forge</h2>
        
        {#if error}
            <div class="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded mb-6 text-sm">
                {error}
            </div>
        {/if}

        <form on:submit|preventDefault={handleLogin} class="space-y-6">
            <div>
                <label for="username" class="block text-sm font-medium text-gray-400 mb-2">Username</label>
                <input 
                    id="username" 
                    type="text" 
                    bind:value={username}
                    class="w-full bg-gray-900 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                    placeholder="Daedalus"
                    required
                />
            </div>

            <div>
                <label for="password" class="block text-sm font-medium text-gray-400 mb-2">Password</label>
                <input 
                    id="password" 
                    type="password" 
                    bind:value={password}
                    class="w-full bg-gray-900 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                    placeholder="••••••••"
                    required
                />
            </div>

            <button 
                type="submit" 
                disabled={isLoading}
                class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isLoading ? 'Authenticating...' : 'Login'}
            </button>
        </form>

        <div class="mt-6 text-center text-sm text-gray-500">
            Need an account? <a href="/forge/register" class="text-cyan-400 hover:text-cyan-300">Sign up</a>
        </div>
    </div>
</div>
