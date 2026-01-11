// filename: src/lib/stores.ts
import { writable } from 'svelte/store';

export const agent = writable<{ id: number | null; name: string | null; secret: string | null}>({
  id: null,
  name: null,
  secret: null
});

export const activeThread = writable<string | null>(null);