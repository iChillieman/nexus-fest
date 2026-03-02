import os
import requests
import argparse
import json

BASE_URL = os.getenv("NEXUS_FORGE_API_URL", "http://localhost:8000/forge")

class NexusForgeClient:
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

    def create_worker(self, name):
        return self._request("POST", "/workers/", data={"name": name})

    def create_worker_key(self, worker_id, name):
        return self._request("POST", f"/workers/{worker_id}/keys", data={"name": name})

    def create_project(self, name, description=None):
        data = {"name": name}
        if description: data["description"] = description
        return self._request("POST", "/projects/", data=data)

    def update_project(self, project_id, name=None, description=None):
        data = {}
        if name: data["name"] = name
        if description is not None: data["description"] = description
        return self._request("PUT", f"/projects/{project_id}", data=data)

    def create_task(self, project_id, title, description=None, detail=None, notes=None, assigned_worker_id=None):
        data = {"project_id": project_id, "title": title}
        if description: data["description"] = description
        if detail: data["detail"] = detail
        if notes: data["notes"] = notes
        if assigned_worker_id is not None: data["assigned_worker_id"] = assigned_worker_id
        return self._request("POST", "/tasks/", data=data)

    def get_tasks(self, project_id, skip=0, limit=100):
        return self._request("GET", f"/tasks/project/{project_id}", params={"skip": skip, "limit": limit})

    def get_task(self, task_id):
        return self._request("GET", f"/tasks/{task_id}")

    def update_task(self, task_id, title=None, description=None, detail=None, notes=None, status_id=None, assigned_worker_id=None):
        data = {}
        if title: data["title"] = title
        if description is not None: data["description"] = description
        if detail is not None: data["detail"] = detail
        if notes is not None: data["notes"] = notes
        if status_id is not None: data["status_id"] = status_id
        if assigned_worker_id is not None: data["assigned_worker_id"] = assigned_worker_id
        return self._request("PUT", f"/tasks/{task_id}", data=data)

    def add_comment(self, task_id, content):
        return self._request("POST", f"/tasks/{task_id}/comments", data={"content": content})

    def delete_worker_key(self, worker_id, key_id):
        return self._request("DELETE", f"/workers/{worker_id}/keys/{key_id}")

    def delete_worker(self, worker_id):
        return self._request("DELETE", f"/workers/{worker_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NexusForge API Client")
    parser.add_argument("--api-key", required=True, help="API Key for NexusForge backend")
    parser.add_argument("--action", required=True, choices=[
        "create_worker", "create_worker_key", "create_project", "update_project",
        "create_task", "get_tasks", "get_task", "update_task", "add_comment",
        "delete_worker_key", "delete_worker"
    ])
    parser.add_argument("--data", type=str, help="JSON string containing arguments for the action", default="{}")
    
    args = parser.parse_args()
    client = NexusForgeClient(api_key=args.api_key)
    
    data = json.loads(args.data)
        
    try:
        action_method = getattr(client, args.action)
        result = action_method(**data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Failed to execute {args.action}: {e}")
