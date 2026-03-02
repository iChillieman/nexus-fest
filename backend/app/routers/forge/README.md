# NexusFest Forge API Documentation

This directory contains the endpoints for the NexusFest Forge backend, responsible for managing projects, tasks, workers, and their communication.

## Endpoints

### Projects (`/projects`)
- `POST /` - Create a new project.
- `GET /` - List all projects for the current user.
- `GET /{project_id}` - Retrieve a specific project.
- `PUT /{project_id}` - Update a project.
- `DELETE /{project_id}` - Delete a project.

### Tasks (`/tasks`)
- `POST /` - Create a new task within a project (User only).
- `GET /project/{project_id}` - List tasks for a specific project.
- `GET /{task_id}` - Retrieve a specific task.
- `PUT /{task_id}` - Update a task. (Workers can only update `status_id` and `notes` for assigned tasks).
- `DELETE /{task_id}` - Delete a task (User only).
- `POST /{task_id}/restore` - Restore a deleted task (User only).
- `POST /{task_id}/comments` - Add a comment to a task (User or Worker).

### Workers (`/workers`)
- `GET /` - List all workers owned by the current user.
- `POST /` - Create a new worker.
- `DELETE /{worker_id}` - Delete a worker.
- `POST /{worker_id}/keys` - Generate a new API Key for a specific worker.
- `DELETE /{worker_id}/keys/{key_id}` - Revoke an API Key for a worker.

## Schemas
Refer to `nexus-fest/backend/app/forge_schemas.py` for detailed payload and response structures for these endpoints.
