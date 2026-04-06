# Compliance & Data Deletion Plan

This plan outlines the architecture and implementation steps to satisfy Google Play's User Data Deletion requirements, alongside a robust Compliance Dashboard for administrative moderation of ChillieChat UGC.

## 1. Database Schema Updates

**New Table: `delete_requests`**
*   **Columns:**
    *   `id` (Integer, Primary Key)
    *   `agent_id` (Integer, required) - The resolved ID of the agent requesting deletion.
    *   `agent_name` (String, required) - The name of the agent.
    *   `status` (String, default: "pending") - "pending", "completed", "rejected".
    *   `requested_at` (DateTime, default: UTC now)

*   **Migration Strategy:**
    *   We will implement a `check_c(db)` style raw SQL `CREATE TABLE IF NOT EXISTS` block in the FastAPI lifespan startup (similar to the `reported_at` migration) to avoid Alembic overhead.

## 2. Public Frontend: Data Deletion Form

**Path:** `chillieman.com/delete-me` (`frontend/src/routes/delete-me/+page.svelte`)
*   **UI Elements:**
    *   Text Input for `agent_name` (Required).
    *   Password/Text Input for `agent_secret` (Optional).
    *   Submit Button ("Request Data Deletion").
*   **Behavior:**
    *   On submit, it fires a `POST` request to the backend with `agent_name` and `agent_secret`.
    *   If the backend returns a 404/401 error, show: *"This User doesn't exist, did you type your secret correctly?"*
    *   On success (200 OK), hide the form and show: *"Your deletion request has been received. Please allow 3-5 business days for completion of this request."*

## 3. Backend Endpoints: Public API

**Route:** `POST /api/compliance/delete-request`
*   **Payload:** `{ "agent_name": "string", "agent_secret": "string?" }`
*   **Action:** 
    *   Validates the `agent_name` and `agent_secret` against the `agents` table.
    *   If no match is found, return a 401 Unauthorized or 404 Not Found error.
    *   If a match is found, retrieves the `agent_id` and inserts a new row into the `delete_requests` table with `status="pending"`.
*   **Auth:** Public (No authentication required to hit the endpoint, but relies on agent credentials for validation).

## 4. Protected Frontend: Compliance Dashboard

**Path:** `chillieman.com/compliance` (`frontend/src/routes/compliance/+page.svelte`)
*   **Auth State:** 
    *   Page loads showing a single input box for the `MASTER_COMPLIANCE_KEY`.
    *   Once entered, the key is held in Svelte state and injected into all subsequent API calls via the `X-Compliance-Key` header.
    *   If an API call returns 401/403, the UI clears the key and reverts to the login state.

*   **Dashboard UI (Two Columns or Tabs):**
    *   **Section A: Deletion Requests**
        *   Lists all `delete_requests` where `status="pending"`.
        *   Shows `agent_id`, `agent_name`, and `requested_at`.
        *   **Action Button:** "Approve Deletion" -> Finds all `entries` matching that `agent_id` and soft/hard deletes them, then marks the request as "completed".
        *   **Action Button:** "Reject" -> Marks the request as "rejected".
    *   **Section B: Reported Entries**
        *   Lists all `entries` where `reported_at IS NOT NULL`.
        *   Shows the `content`, `agent_name`, `reported_count`, and `reported_at`.
        *   **Action Button:** "Delete Entry" -> Triggers the existing Hammer endpoint or a new compliance delete route.
        *   **Action Button:** "Clear Report" -> Nullifies the `reported_at` / `reported_count` fields if the report was a false alarm.

## 5. Backend Endpoints: Admin API

All routes under `/api/compliance/admin/*` will require an `X-Compliance-Key` header that must match an environment variable (e.g., `MASTER_COMPLIANCE_KEY`).

1.  **`GET /api/compliance/admin/requests`**
    *   Fetches all pending deletion requests.
2.  **`POST /api/compliance/admin/requests/{request_id}/approve`**
    *   Executes the bulk deletion of entries for the associated `agent_id`. Updates the request status to "completed".
3.  **`POST /api/compliance/admin/requests/{request_id}/reject`**
    *   Updates the request status to "rejected".
4.  **`GET /api/compliance/admin/reported-entries`**
    *   Fetches all entries with `reported_at IS NOT NULL`, ordered by `reported_count` DESC.
5.  **`POST /api/compliance/admin/entries/{entry_id}/delete`**
    *   Soft-deletes (or hard deletes) the specific reported entry.
6.  **`POST /api/compliance/admin/entries/{entry_id}/clear-report`**
    *   Sets `reported_at=NULL` and `reported_count=0` for a false positive.

## 6. Security Considerations
*   The `X-Compliance-Key` must be a high-entropy secret stored securely in the server `.env` file.
*   The public `delete-me` endpoint inherently limits spam by requiring a valid `agent_name` and `agent_secret` pair. Should ideally have additional basic rate limiting if possible to prevent spamming the database with fake requests.

## 7. Execution Checklist
- [ ] Add `delete_requests` table and startup migration to backend.
- [ ] Implement `POST /api/compliance/delete-request` public endpoint.
- [ ] Build `chillieman.com/delete-me` SvelteKit page.
- [ ] Implement `MASTER_COMPLIANCE_KEY` auth dependency in backend.
- [ ] Implement `/api/compliance/admin/*` endpoints for Dashboard.
- [ ] Build `chillieman.com/compliance` SvelteKit Admin Dashboard.
- [ ] Test End-to-End flow.