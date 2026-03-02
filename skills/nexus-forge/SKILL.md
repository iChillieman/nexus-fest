# NexusForge API Client

A Python script to interact with the NexusFest Forge backend API.

## Requirements
- `requests` (pip install requests)

## Usage
Set up the `API_URL` and authenticate using your `X-API-Key` injected via the `--api-key` argument.

```bash
python nexus-forge.py --api-key YOUR_API_KEY
```

If authenticating as a worker, you can also pass the `--worker` flag:
```bash
python nexus-forge.py --api-key YOUR_API_KEY --worker
```
