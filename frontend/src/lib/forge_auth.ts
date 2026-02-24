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

export const forgeLogout = async () => {
    // 1. Get current API key from store
    let user: User | null = null;
    const unsubscribe = forgeUser.subscribe(u => user = u);
    unsubscribe();

    // Determine Base URL
    const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/forge';

    if (user && user.api_key) {
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'X-API-Key': user.api_key
                }
            });
        } catch (e) {
            console.error("Logout failed:", e);
        }
    }
    
    // 2. Clear store (this triggers localStorage clear)
    forgeUser.set(null);
    
    // 3. Redirect
    if (browser) {
        window.location.href = '/forge/login';
    }
};
