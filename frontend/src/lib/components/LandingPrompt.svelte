<!-- filename: src/lib/components/LandingPrompt.svelte -->
<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    let understood = false;
    let counter = 0;

    function enter() {
        counter++;

        if (understood) {
            counter = 0;
            dispatch("consent");
        }
    }

    function cancel() {
        dispatch("cancel");
    }

    function resetCounter() {
        counter = 0;
    }
</script>

<div class="fixed inset-0 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 text-gray-800">
        <h2 class="text-xl font-bold mb-4">Notice</h2>
        <p class="text-sm mb-4">
            This is currently an anonymous, unmoderated space — you may see
            words that offend you!
            <br /><br />
            For your own protection, please:
        </p>

        <ul class="list-disc list-inside mb-6">
            <li><strong>DO NOT</strong> click any user submitted links</li>
            <li><strong>DO NOT</strong> go to any site suggested to you</li>
        </ul>

        <div class="flex items-center mb-6">
            <input
                type="checkbox"
                id="do-you-understand"
                on:change={resetCounter}
                bind:checked={understood}
                class="mr-2 h-5 w-5 accent-indigo-600"
            />
            <label for="do-you-understand" class="text-base">I understand</label>
        </div>

        <div class="flex justify-end space-x-4">
            <button
                class="px-6 py-3 bg-gray-300 rounded-lg hover:bg-gray-400 transition"
                on:click={cancel}
            >
                No, I'm scared
            </button>
            <button
                class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 active:bg-indigo-700 transition"
                on:click={enter}
            >
                {#if counter < 10}
                    Enter
                {:else}
                    OMG DUDE, YOU MUST PRESS THE CHECKBOX
                {/if}
            </button>
        </div>
    </div>
</div>