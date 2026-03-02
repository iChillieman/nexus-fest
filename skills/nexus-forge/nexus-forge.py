import os
import requests
import json
import argparse

BASE_URL = os.getenv("NEXUS_FORGE_API_URL", "http://localhost:8000/forge")

class NexusForgeClient:
    def __init__(self, api_key: str, is_worker: bool = False):
        self.api_key = api_key
        self.is_worker = is_worker
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, json=data, params=params)
        response.raise_for_status()
        return response.json()

    # --- Projects ---
    def get_projects(self, skip=0, limit=100):
        return self._request("GET", "/projects/", params={"skip": skip, "limit": limit})
        
    def get_project(self, project_id):
        return self._request("GET", f"/projects/{project_id}")

    # --- Tasks ---
    def get_tasks_for_project(self, project_id, skip=0, limit=100):
        return self._request("GET", f"/tasks/project/{project_id}", params={"skip": skip, "limit": limit})
        
    def get_task(self, task_id):
        return self._request("GET", f"/tasks/{task_id}")

    def update_task(self, task_id, update_data):
        return self._request("PUT", f"/tasks/{task_id}", data=update_data)

    def add_task_comment(self, task_id, content):
        return self._request("POST", f"/tasks/{task_id}/comments", data={"content": content})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NexusForge API Client")
    parser.add_argument("--api-key", required=True, help="API Key for NexusForge backend")
    parser.add_argument("--worker", action="store_true", help="Flag if this is a worker API key")
    args = parser.parse_args()
    
    client = NexusForgeClient(api_key=args.api_key, is_worker=args.worker)
    print("NexusForgeClient initialized successfully with API key.")
