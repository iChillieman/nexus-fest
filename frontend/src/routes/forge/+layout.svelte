<script>
    import "../../../app.css";
    import favicon from '$lib/assets/favicon.svg';
    import { forgeUser, forgeLogout } from '$lib/forge_auth';
    import { goto } from '$app/navigation';

    let { children } = $props();

    function handleLogout() {
        forgeLogout();
        goto('/forge/login');
    }
</script>

<svelte:head>
	<link rel="icon" href="{favicon}" />
</svelte:head>

<div class="bg-gray-900 min-h-screen text-white flex flex-col">
    <nav class="border-b border-gray-800 bg-gray-900/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16 items-center">
                <div class="flex items-center">
                    <a href="/forge" class="text-xl font-bold text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-2">
                        <span class="text-2xl">🔥</span> The Forge
                    </a>
                </div>
                <div class="flex items-center gap-4">
                    {#if $forgeUser}
                        <span class="text-sm text-gray-400 hidden sm:inline">Logged in as <span class="text-white">{$forgeUser.username}</span></span>
                        <button 
                            onclick={handleLogout}
                            class="text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded border border-gray-700 transition-colors"
                        >
                            Logout
                        </button>
                    {:else}
                        <a href="/forge/login" class="text-sm text-gray-300 hover:text-white">Login</a>
                        <a 
                            href="/forge/register" 
                            class="text-sm bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded transition-colors"
                        >
                            Sign Up
                        </a>
                    {/if}
                </div>
            </div>
        </div>
    </nav>

    <div class="flex-grow">
        {@render children()}
    </div>
</div>

