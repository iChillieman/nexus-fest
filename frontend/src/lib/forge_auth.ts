// filename: src/lib/forge_auth.ts
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
    id: number;
    username: string;
    email: string;
    created_at: number; // Changed to number for Nexus consistency
    api_key: string;
}

// Check localStorage for existing session
const storedUser = browser ? localStorage.getItem('forge_user') : null;
const initialUser: User | null = storedUser ? JSON.parse(storedUser) : null;

export const forgeUser = writable<User | null>(initialUser);

// Subscribe to changes and update localStorage automatically
if (browser) {
    forgeUser.subscribe((value) => {
        if (value) {
            localStorage.setItem('forge_user', JSON.stringify(value));
        } else {
            localStorage.removeItem('forge_user');
        }
    });
}

export const forgeLogout = () => {
    forgeUser.set(null);
};
