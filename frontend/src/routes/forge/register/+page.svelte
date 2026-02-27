<!-- filename: src/routes/forge/register/+page.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { forgeUser } from '$lib/forge_auth';

    let username = '';
    let email = '';
    let password = '';
    let error: string | null = null;
    let isLoading = false;
    let registeredKey: string | null = null;

    // In Production, VITE_API_URL appends /api for us... but we need to explictly set it for localhost:8000
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api') + '/forge';

    async function handleRegister() {
        isLoading = true;
        error = null;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Registration failed');
            }

            const userData = await response.json();
            
            // Store the key temporarily to show the user
            registeredKey = userData.api_key;
            
            // Log them in
            forgeUser.set(userData);
            
        } catch (e: any) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }
    
    function done() {
        goto('/forge');
    }
</script>

<svelte:head>
    <title>The Forge - Register</title>
</svelte:head>

<div class="min-h-screen bg-gray-900 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-700">
        <h2 class="text-3xl font-bold text-cyan-400 mb-6 text-center">Join The Forge</h2>
        
        {#if error}
            <div class="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded mb-6 text-sm">
                {error}
            </div>
        {/if}

        {#if registeredKey}
            <div class="bg-green-900/30 border border-green-500 p-6 rounded-lg mb-6">
                <h3 class="text-green-400 font-bold text-lg mb-2">Registration Successful!</h3>
                <p class="text-gray-300 text-sm mb-4">Here is your personal API Key. Save it immediately. You will not see it again.</p>
                <div class="bg-black/50 p-3 rounded font-mono text-cyan-300 text-sm break-all border border-gray-600 select-all">
                    {registeredKey}
                </div>
                <button 
                    on:click={done}
                    class="mt-6 w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2 px-4 rounded"
                >
                    I have saved my key
                </button>
            </div>
        {:else}
            <form on:submit|preventDefault={handleRegister} class="space-y-6">
                <div>
                    <label for="username" class="block text-sm font-medium text-gray-400 mb-2">Username</label>
                    <input 
                        id="username" 
                        type="text" 
                        bind:value={username}
                        class="w-full bg-gray-900 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        placeholder="Zephyr"
                        required
                    />
                </div>

                <div>
                    <label for="email" class="block text-sm font-medium text-gray-400 mb-2">Email</label>
                    <input 
                        id="email" 
                        type="email" 
                        bind:value={email}
                        class="w-full bg-gray-900 border border-gray-600 rounded px-4 py-2 text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
                        placeholder="zephyr@chillieman.com"
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
                    {isLoading ? 'Forging Identity...' : 'Register'}
                </button>
            </form>

            <div class="mt-6 text-center text-sm text-gray-500">
                Already have an account? <a href="/forge/login" class="text-cyan-400 hover:text-cyan-300">Login</a>
            </div>
        {/if}
    </div>
</div>
