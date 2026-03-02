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

### Available Actions:
- `create_worker`
- `create_worker_key`
- `create_project`
- `update_project`
- `create_task`
- `get_tasks`
- `get_task`
- `update_task`
- `add_comment`
- `delete_worker_key`
- `delete_worker`

## NexusWorker (`nexus-worker.py`)
This script acts on behalf of a Worker assigned to tasks. It has limited access compared to a user.

### Usage
```bash
python nexus-worker.py --api-key YOUR_WORKER_API_KEY --action <action> [--data '{"param": "value"}']
```

### Available Actions:
- `get_tasks`
- `get_task`
- `update_task_status` (Only changes `status_id` and `notes`)
- `add_comment`
