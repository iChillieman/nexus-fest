# NexusForge & NexusWorker API Clients

Two Python scripts to interact with the NexusFest Forge backend API from different perspectives.

## Requirements
- `requests` (pip install requests)

## NexusForge (`nexus-forge.py`)
This script acts on behalf of a regular User. It can manage projects, tasks, and workers.

### Usage
```bash
python nexus-forge.py --api-key YOUR_USER_API_KEY --action <action> [--data '{"param": "value"}']
```

### Available Actions & Expected Inputs (`--data` JSON):

**Task Status IDs:**
- `1` = To Do
- `2` = In Progress
- `3` = Ready for Review
- `4` = Done
- `5` = Blocked

*   **`create_worker`**
    *   Input: `{"name": "string"}`
    *   Example: `--data '{"name": "CoderBot 9000"}'`
*   **`create_worker_key`**
    *   Input: `{"worker_id": int, "name": "string"}`
    *   Example: `--data '{"worker_id": 1, "name": "Prod Key"}'`
*   **`create_project`**
    *   Input: `{"name": "string", "description": "string (optional)"}`
    *   Example: `--data '{"name": "New App", "description": "SaaS Platform"}'`
*   **`update_project`**
    *   Input: `{"project_id": int, "name": "string (optional)", "description": "string (optional)"}`
    *   Example: `--data '{"project_id": 5, "name": "Updated App"}'`
*   **`create_task`**
    *   Input: `{"project_id": int, "title": "string", "description": "string (optional)", "detail": "string (optional)", "notes": "string (optional)", "assigned_worker_id": int (optional)}`
    *   Example: `--data '{"project_id": 5, "title": "Build UI", "assigned_worker_id": 1}'`
*   **`get_tasks`**
    *   Input: `{"project_id": int, "skip": int (optional, default 0), "limit": int (optional, default 100), "status_ids": list[int] (optional)}`
    *   Example: `--data '{"project_id": 5, "status_ids": [1, 2]}'`
*   **`get_task`**
    *   Input: `{"task_id": int}`
    *   Example: `--data '{"task_id": 12}'`
*   **`update_task`**
    *   Input: `{"task_id": int, "title": "string (optional)", "description": "string (optional)", "detail": "string (optional)", "notes": "string (optional)", "status_id": int (optional), "assigned_worker_id": int (optional)}`
    *   Example: `--data '{"task_id": 12, "status_id": 2, "assigned_worker_id": 2}'`
*   **`add_comment`**
    *   Input: `{"task_id": int, "content": "string"}`
    *   Example: `--data '{"task_id": 12, "content": "Looking into this now."}'`
*   **`delete_worker_key`**
    *   Input: `{"worker_id": int, "key_id": int}`
    *   Example: `--data '{"worker_id": 1, "key_id": 3}'`
*   **`delete_worker`**
    *   Input: `{"worker_id": int}`
    *   Example: `--data '{"worker_id": 1}'`


## NexusWorker (`nexus-worker.py`)
This script acts on behalf of a Worker assigned to tasks. It has limited access compared to a user.

### Usage
```bash
python nexus-worker.py --api-key YOUR_WORKER_API_KEY --action <action> [--data '{"param": "value"}']
```

### Available Actions & Expected Inputs (`--data` JSON):

**Task Status IDs:**
- `1` = To Do
- `2` = In Progress
- `3` = Ready for Review
- `4` = Done
- `5` = Blocked

*   **`get_tasks`**
    *   Input: `{"project_id": int, "skip": int (optional, default 0), "limit": int (optional, default 100), "status_ids": list[int] (optional)}`
    *   Example: `--data '{"project_id": 5, "status_ids": [1, 2]}'`
*   **`get_task`**
    *   Input: `{"task_id": int}`
    *   Example: `--data '{"task_id": 12}'`
*   **`update_task_status`**
    *   Input: `{"task_id": int, "status_id": int (optional), "notes": "string (optional)"}`
    *   *(Note: Workers cannot change the title, description, detail, or assignment.)*
    *   Example: `--data '{"task_id": 12, "status_id": 3, "notes": "PR submitted"}'`
*   **`add_comment`**
    *   Input: `{"task_id": int, "content": "string"}`
    *   Example: `--data '{"task_id": 12, "content": "Encountered an issue with the API."}'`
