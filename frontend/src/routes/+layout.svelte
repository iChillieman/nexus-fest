<!-- src/routes/+layout.svelte -->
<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	export const prerender = true;
	export const ssr = false; // This makes it a Single Page Application (SPA)

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
