<!-- filename: src/routes/+error.svelte -->
<script lang="ts">
    import { onMount } from "svelte";

    let startFade = false;
    let startFade2 = false;
    let sendSnacks = true;

    // Cookie helper functions
    function setCookie(name: string, value: string, minutes: number) {
        const date = new Date();
        date.setTime(date.getTime() + minutes * 60 * 1000);
        const expires = "; expires=" + date.toUTCString();
        document.cookie = name + "=" + (value || "") + expires + "; path=/";
    }

    function getCookie(name: string) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(";");
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === " ") c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0)
                return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    onMount(async () => {
        startFade = true;
        setTimeout(() => {
            startFade2 = true;
        }, 4000);
    });

    // The magic: play only if no cookie exists
    const knockCookieName = "kno"; // unique name
    const cookieExists = getCookie(knockCookieName);

    if (!cookieExists) {
        const audio = new Audio("/kno.mp3"); // 👊 Hello?
        audio.volume = 0.8;
        audio
            .play()
            .then((e) => {
                // Set cookie for 3 minutes
                setCookie(knockCookieName, "true", 3);
            })
            .catch((e) => {
                console.log("Autoplay blocked - user must interact first", e);
                // Fallback: play on first click if needed
                document.body.addEventListener(
                    "click",
                    () => {
                        audio.play().then((e) => {
                            // Set cookie for 3 minutes
                            setCookie(knockCookieName, "true", 3);
                        });
                    },
                    {
                        once: true,
                    },
                );
            });
    } else {
        // User already heard it in last 3 min → silent mode
        console.log("Knock already played recently - shhh 🤫👀");
        sendSnacks = false;
    }
</script>

<div
    class="absolute inset-0 flex flex-col items-center justify-center text-center text-white"
>
    <h1 class="text-5xl font-bold mb-8 px-8 py-5">YOU THERE - 🫵 - HELLO!!!</h1>
    {#if sendSnacks}
        <p
            class="text-2xl font-bold px-8 py-5 opacity-0"
            class:fade-in={startFade}
        >
            PLEASE...
        </p>
        <h5 class="font-bold opacity-0" class:fade-in-fast={startFade2}>
            🍪 Send Snacks 🍪
        </h5>
    {:else}
        <p
            class="text-2xl font-bold px-8 py-5 opacity-0"
            class:fade-in={startFade}
        >
            Turn Around.
        </p>
        <h5 class="font-bold opacity-0" class:fade-in-fast={startFade2}>
            LMAO!!! 🤣🤣🤣 JK!!!
        </h5>
    {/if}
</div>

<style>
    .fade-in {
        animation: fadeIn 3s cubic-bezier(0.4, 0, 0.6, 1) forwards;
    }

    .fade-in-fast {
        animation: fadeIn 1s cubic-bezier(0.4, 0, 0.6, 1) forwards;
    }

    @keyframes fadeIn {
        0% {
            opacity: 0;
        }
        100% {
            opacity: 1;
        }
    }
</style>
