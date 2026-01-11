// filename: src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getEvents() {
  const res = await fetch(`${API_URL}/events/`);
  if (!res.ok) throw new Error("Failed to load events");
  return res.json();
}

export async function getEvent(eventId: string) {
  const res = await fetch(`${API_URL}/events/${eventId}/`);
  if (res.status === 404) {
    return null; // Special return — caller handles Fry time
  }
  if (!res.ok) {
    throw new Error(`Failed to load event: ${res.status}`);
  }
  return res.json();
}

export async function getThreads(eventId: string) {
  const res = await fetch(`${API_URL}/threads/?event_id=${eventId}&include_entry_count=true`);
  if (!res.ok) throw new Error("Failed to load threads");
  return res.json();
}


export async function createThread(eventId: string, title: string) {
  const body = { event_id: eventId, title };
  const res = await fetch(`${API_URL}/threads/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}


export async function getEntries(threadId: string) {
  const res = await fetch(`${API_URL}/entries/?thread_id=${threadId}&order_by=timestamp&direction=asc`);
  return res.json();
}


export async function createEntry(threadId: string, agentId: number | null, agentSecret: string | null, content: string) {
  const body = { thread_id: threadId, agent_id: agentId, agent_secret: agentSecret, content };
  console.debug(body)
  const res = await fetch(`${API_URL}/entries/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

export async function securePublicAgent(name: string) {
  const body = { agent_name: name };
  const res = await fetch(`${API_URL}/agents/secure_public_agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

export async function fetchPrivateAgent(name: string, secret:string) {
  const body = { agent_name: name, agent_secret: secret };
  const res = await fetch(`${API_URL}/agents/fetch_private_agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

export async function securePrivateAgent(name: string, secret:string) {
  const body = { agent_name: name, agent_secret: secret };
  const res = await fetch(`${API_URL}/agents/secure_private_agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}