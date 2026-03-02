import os
import requests
import argparse
import json

BASE_URL = os.getenv("NEXUS_FORGE_API_URL", "http://localhost:8000/forge")

class NexusWorkerClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data, params=params)
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error: {e.response.text}")
            raise

    def get_tasks(self, project_id, skip=0, limit=100, status_ids=None):
        params = {"skip": skip, "limit": limit}
        if status_ids:
            params["status_ids"] = status_ids
        return self._request("GET", f"/tasks/project/{project_id}", params=params)

    def get_task(self, task_id):
        return self._request("GET", f"/tasks/{task_id}")

    def update_task_status(self, task_id, status_id=None, notes=None):
        data = {}
        if status_id is not None: data["status_id"] = status_id
        if notes is not None: data["notes"] = notes
        return self._request("PUT", f"/tasks/{task_id}", data=data)

    def add_comment(self, task_id, content):
        return self._request("POST", f"/tasks/{task_id}/comments", data={"content": content})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NexusWorker API Client")
    parser.add_argument("--api-key", required=True, help="Worker API Key for NexusForge backend")
    parser.add_argument("--action", required=True, choices=[
        "get_tasks", "get_task", "update_task_status", "add_comment"
    ])
    parser.add_argument("--data", type=str, help="JSON string containing arguments for the action", default="{}")
    
    args = parser.parse_args()
    client = NexusWorkerClient(api_key=args.api_key)
    
    data = json.loads(args.data)
        
    try:
        action_method = getattr(client, args.action)
        result = action_method(**data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Failed to execute {args.action}: {e}")
