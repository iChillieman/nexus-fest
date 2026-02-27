import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/forge"
RESULTS_FILE = "results.txt"

def log(message, level="INFO"):
    formatted_msg = f"[{level}] {message}"
    print(formatted_msg)
    with open(RESULTS_FILE, "a") as f:
        f.write(formatted_msg + "\n")

def clear_log():
    open(RESULTS_FILE, "w").close()

def assert_status(response, expected_status, name):
    if response.status_code == expected_status:
        log(f"✅ {name} passed (Status: {response.status_code})")
        return True
    else:
        log(f"❌ {name} failed! Expected {expected_status}, got {response.status_code}", "ERROR")
        try:
            log(f"   Response Body: {response.json()}", "ERROR")
        except:
            log(f"   Response Body: {response.text}", "ERROR")
        return False

# Helper function to catch connection errors easily
def make_request(method, url, **kwargs):
    try:
        return requests.request(method, url, **kwargs)
    except requests.exceptions.ConnectionError:
        log(f"❌ Connection refused to {url}. Is the backend running?", "ERROR")
        sys.exit(1)

def run_tests():
    clear_log()
    log("=====================================")
    log("  🚀 STARTING FORGE API TESTS 🚀")
    log("=====================================")

    log("Note: This script assumes a clean or test DB environment.")
    
    log("\n--- STEP 0: Authentication ---")
    
    # Generate unique user details to ensure a clean registration every time
    timestamp = str(int(time.time()))
    test_username = f"test_user_{timestamp}"
    test_email = f"test_{timestamp}@example.com"
    test_password = "TestPassword123!"

    log(f"Registering new test user: {test_username}")
    res = make_request("POST", f"{BASE_URL}/auth/register", json={
        "username": test_username,
        "email": test_email,
        "password": test_password
    })
    
    if not assert_status(res, 200, "User Registration"):
        log("❌ Failed to register user. Tests aborted.", "ERROR")
        sys.exit(1)
        
    API_KEY = res.json().get("api_key")
    user_id = res.json().get("id")
    log(f"   Successfully registered User ID: {user_id}")
    log(f"   Using newly minted API Key: {API_KEY[:5]}...{API_KEY[-5:]}")

    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    bad_headers = {
        "accept": "application/json",
        "X-API-Key": "wrong_key_123",
        "Content-Type": "application/json"
    }

    # ==========================
    # VALID TESTS
    # ==========================
    log("\n--- PART 1: VALID API KEY TESTS ---")

    # 1. Create Project
    res = make_request("POST", f"{BASE_URL}/projects/", headers=headers, json={
        "name": "Automated Test Project",
        "description": "Created by automated test script"
    })
    if not assert_status(res, 200, "Create Project"): return
    project_id = res.json().get("id")
    log(f"   Created Project ID: {project_id}")

    # 2. Edit Project
    res = make_request("PUT", f"{BASE_URL}/projects/{project_id}", headers=headers, json={
        "name": "Automated Test Project (Updated)",
        "description": "Updated by automated test script"
    })
    assert_status(res, 200, "Edit Project")

    # 3. List All Projects
    res = make_request("GET", f"{BASE_URL}/projects/?skip=0&limit=10", headers=headers)
    assert_status(res, 200, "List All Projects")

    # 4. List Single Project
    res = make_request("GET", f"{BASE_URL}/projects/{project_id}", headers=headers)
    assert_status(res, 200, "List Single Project")

    # 5. Delete Single Project
    res = make_request("DELETE", f"{BASE_URL}/projects/{project_id}", headers=headers)
    assert_status(res, 200, "Delete Single Project")
    if res.status_code == 200:
        deleted_at = res.json().get("deleted_at")
        if deleted_at:
            log(f"   ✅ Project properly soft-deleted (deleted_at: {deleted_at})")
        else:
            log("   ❌ Project soft-delete failed (deleted_at is null)", "ERROR")

    # ==========================
    # TASKS TESTS
    # ==========================
    log("\n--- PART 2: TASKS ---")
    
    # Create a fresh project for tasks
    res = make_request("POST", f"{BASE_URL}/projects/", headers=headers, json={
        "name": "Task Holder Project",
        "description": "Holds tests tasks"
    })
    if not assert_status(res, 200, "Create Setup Project for Tasks"): return
    task_project_id = res.json().get("id")

    # 1. Create Task
    res = make_request("POST", f"{BASE_URL}/tasks/", headers=headers, json={
        "title": "Automated Test Task",
        "description": "Task created via API",
        "project_id": task_project_id
    })
    if not assert_status(res, 200, "Create Task"): return
    task_id = res.json().get("id")
    log(f"   Created Task ID: {task_id}")

    # 2. Fetch Tasks for Project
    res = make_request("GET", f"{BASE_URL}/tasks/project/{task_project_id}?skip=0&limit=10", headers=headers)
    assert_status(res, 200, "Fetch Tasks for Project")

    # 2.5 Fetch Single Task (New Endpoint)
    res = make_request("GET", f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert_status(res, 200, "Fetch Specific Task")

    # 3. Update Task (All fields)
    res = make_request("PUT", f"{BASE_URL}/tasks/{task_id}", headers=headers, json={
        "title": "Updated Test Task",
        "description": "Updated description",
        "status_id": 2
    })
    assert_status(res, 200, "Update Task (All fields)")

    # 4. Update Task (Partial - Status only)
    res = make_request("PUT", f"{BASE_URL}/tasks/{task_id}", headers=headers, json={
        "status_id": 3
    })
    assert_status(res, 200, "Update Task (Status only)")

    # 5. Delete Task
    res = make_request("DELETE", f"{BASE_URL}/tasks/{task_id}", headers=headers)
    assert_status(res, 200, "Delete Task")

    # 6. Restore Task
    res = make_request("POST", f"{BASE_URL}/tasks/{task_id}/restore", headers=headers)
    assert_status(res, 200, "Restore Task")

    # ==========================
    # INVALID TESTS
    # ==========================
    log("\n--- PART 3: INVALID API KEY TESTS ---")

    res = make_request("POST", f"{BASE_URL}/projects/", headers=bad_headers, json={"name": "Bad Project"})
    assert_status(res, 403, "Invalid Create Project")

    res = make_request("PUT", f"{BASE_URL}/projects/{task_project_id}", headers=bad_headers, json={"name": "Bad Update"})
    assert_status(res, 403, "Invalid Edit Project")

    res = make_request("GET", f"{BASE_URL}/projects/", headers=bad_headers)
    assert_status(res, 403, "Invalid List All Projects")

    res = make_request("GET", f"{BASE_URL}/projects/{task_project_id}", headers=bad_headers)
    assert_status(res, 403, "Invalid List Single Project")

    res = make_request("DELETE", f"{BASE_URL}/projects/{task_project_id}", headers=bad_headers)
    assert_status(res, 403, "Invalid Delete Single Project")

    # ==========================
    # WORKER TESTS
    # ==========================
    log("\n--- PART 4: WORKER TESTS ---")

    # 1. Create Worker
    res = make_request("POST", f"{BASE_URL}/workers/", headers=headers, json={
        "name": "Automated Test Worker"
    })
    if not assert_status(res, 200, "Create Worker"): return
    worker_id = res.json().get("id")
    log(f"   Created Worker ID: {worker_id}")

    # 2. Create API Key for that Worker
    res = make_request("POST", f"{BASE_URL}/workers/{worker_id}/keys", headers=headers, json={
        "name": "Automated Worker Key"
    })
    if not assert_status(res, 200, "Create Worker API Key"): return
    worker_api_key = res.json().get("api_key")
    worker_key_id = res.json().get("id")
    log(f"   Created Worker Key ID: {worker_key_id}")

    worker_headers = {
        "accept": "application/json",
        "X-API-Key": worker_api_key,
        "Content-Type": "application/json"
    }

    # Setup a new task specifically assigned to this worker so they have permission
    res = make_request("POST", f"{BASE_URL}/tasks/", headers=headers, json={
        "title": "Worker Test Task",
        "description": "Task for worker to interact with",
        "project_id": task_project_id,
        "assigned_worker_id": worker_id
    })
    if not assert_status(res, 200, "Create Task Assigned to Worker"): return
    worker_task_id = res.json().get("id")

    # 3. Ensure the Worker API Key CAN fetch Task Details
    res = make_request("GET", f"{BASE_URL}/tasks/{worker_task_id}", headers=worker_headers)
    assert_status(res, 200, "Worker Fetch Task Details")

    # 4. Ensure the Worker API Key CAN update the Task status flag
    res = make_request("PUT", f"{BASE_URL}/tasks/{worker_task_id}", headers=worker_headers, json={
        "status_id": 4
    })
    assert_status(res, 200, "Worker Update Task Status")

    # 5. Ensure the Worker API Key CANNOT update a Task Title
    res = make_request("PUT", f"{BASE_URL}/tasks/{worker_task_id}", headers=worker_headers, json={
        "title": "Worker Malicious Update"
    })
    assert_status(res, 403, "Worker Prevented from Updating Title")

    # 6. Ensure the Worker API Key CANNOT update a Project Title
    res = make_request("PUT", f"{BASE_URL}/projects/{task_project_id}", headers=worker_headers, json={
        "name": "Worker Malicious Project Name"
    })
    assert_status(res, 403, "Worker Prevented from Updating Project")

    # 7. Ensure the Worker API Key CANNOT create Projects / Tasks
    res = make_request("POST", f"{BASE_URL}/projects/", headers=worker_headers, json={
        "name": "Worker Created Project"
    })
    assert_status(res, 403, "Worker Prevented from Creating Project")

    res = make_request("POST", f"{BASE_URL}/tasks/", headers=worker_headers, json={
        "title": "Worker Created Task",
        "project_id": task_project_id
    })
    assert_status(res, 403, "Worker Prevented from Creating Task")

    # 8. Revoke the Workers API key
    res = make_request("DELETE", f"{BASE_URL}/workers/{worker_id}/keys/{worker_key_id}", headers=headers)
    assert_status(res, 200, "Revoke Worker API Key")

    # Ensure key revocation works immediately
    res = make_request("GET", f"{BASE_URL}/tasks/{worker_task_id}", headers=worker_headers)
    assert_status(res, 403, "Ensure Worker Fails after Key Revoked")

    # Mint a new key to test Worker Deletion
    res = make_request("POST", f"{BASE_URL}/workers/{worker_id}/keys", headers=headers, json={
        "name": "Automated Worker Key 2"
    })
    worker_api_key_2 = res.json().get("api_key")
    worker_headers_2 = {
        "accept": "application/json",
        "X-API-Key": worker_api_key_2,
        "Content-Type": "application/json"
    }

    # 9. Delete the Worker
    res = make_request("DELETE", f"{BASE_URL}/workers/{worker_id}", headers=headers)
    assert_status(res, 200, "Delete Worker")

    # 10. Ensure endpoints FAIL using that old API key (since the worker is deleted)
    res = make_request("GET", f"{BASE_URL}/tasks/{worker_task_id}", headers=worker_headers_2)
    assert_status(res, 403, "Ensure Worker Key Fails after Worker Deleted")

    log("\n=====================================")
    log("  ✅ TESTS COMPLETE ✅")
    log(f"  Results saved to {RESULTS_FILE}")
    log("=====================================")

if __name__ == "__main__":
    run_tests()
