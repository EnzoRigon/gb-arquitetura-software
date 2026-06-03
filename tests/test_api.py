from datetime import UTC, datetime, timedelta


def test_user_crud_flow(client, user_factory, token_factory, auth_header):
    created = user_factory("Alice", "alice@example.com")
    token = token_factory("alice@example.com")
    headers = auth_header(token)

    get_response = client.get(f"/users/{created['id']}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["email"] == "alice@example.com"

    update_response = client.put(
        f"/users/{created['id']}",
        json={"full_name": "Alice Updated"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Alice Updated"


def test_tasks_advanced_filters_and_notifications(client, user_factory, token_factory, auth_header):
    user_factory("Owner", "owner@example.com")
    assignee = user_factory("Bob", "bob@example.com")

    owner_token = token_factory("owner@example.com")
    owner_headers = auth_header(owner_token)

    due_date = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    create_task_response = client.post(
        "/tasks",
        json={
            "title": "Implement API",
            "description": "Build endpoints",
            "status": "pending",
            "priority": "high",
            "due_date": due_date,
            "assigned_to_id": assignee["id"],
        },
        headers=owner_headers,
    )
    assert create_task_response.status_code == 201
    task = create_task_response.json()

    update_task_response = client.put(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"},
        headers=owner_headers,
    )
    assert update_task_response.status_code == 200

    filtered = client.get(
        "/tasks",
        params={
            "assignedTo": assignee["id"],
            "status": "in_progress",
            "priority": "high",
        },
        headers=owner_headers,
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1

    due_before = (datetime.now(UTC) + timedelta(days=5)).isoformat()
    filtered_due = client.get(
        "/tasks",
        params={"dueBefore": due_before},
        headers=owner_headers,
    )
    assert filtered_due.status_code == 200
    assert len(filtered_due.json()) == 1

    assignee_token = token_factory("bob@example.com")
    assignee_headers = auth_header(assignee_token)
    notifications = client.get("/notifications", headers=assignee_headers)
    assert notifications.status_code == 200
    assert len(notifications.json()) >= 1


def test_logout_invalidates_token(client, user_factory, token_factory, auth_header):
    user_factory("Carol", "carol@example.com")
    token = token_factory("carol@example.com")
    headers = auth_header(token)

    logout_response = client.post("/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    forbidden_response = client.get("/tasks", headers=headers)
    assert forbidden_response.status_code == 401
