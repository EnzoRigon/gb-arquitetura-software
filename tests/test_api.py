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


def test_export_csv_empty(client, user_factory, token_factory, auth_header):
    user_factory("Export User", "export@example.com")
    token = token_factory("export@example.com")
    headers = auth_header(token)

    response = client.get("/tasks/export/csv", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Nenhuma tarefa encontrada." in response.text


def test_export_csv_with_tasks(client, user_factory, token_factory, auth_header):
    user_factory("CSV Owner", "csvowner@example.com")
    token = token_factory("csvowner@example.com")
    headers = auth_header(token)

    client.post(
        "/tasks",
        json={"title": "CSV Task", "description": "desc", "status": "pending", "priority": "high"},
        headers=headers,
    )

    response = client.get("/tasks/export/csv", headers=headers)
    assert response.status_code == 200
    assert "CSV Task" in response.text
    assert "high" in response.text
    assert "pending" in response.text


def test_export_csv_filters_by_status(client, user_factory, token_factory, auth_header):
    user_factory("Filter User", "filter@example.com")
    token = token_factory("filter@example.com")
    headers = auth_header(token)

    client.post("/tasks", json={"title": "Pending Task", "status": "pending", "priority": "low"}, headers=headers)
    client.post("/tasks", json={"title": "Done Task", "status": "done", "priority": "low"}, headers=headers)

    response = client.get("/tasks/export/csv", params={"status": "done"}, headers=headers)
    assert response.status_code == 200
    assert "Done Task" in response.text
    assert "Pending Task" not in response.text


def test_export_csv_include_assigned(client, user_factory, token_factory, auth_header):
    owner = user_factory("Owner Csv", "ownercv@example.com")
    assignee = user_factory("Assignee Csv", "assigneecv@example.com")

    owner_token = token_factory("ownercv@example.com")
    owner_headers = auth_header(owner_token)
    assignee_token = token_factory("assigneecv@example.com")
    assignee_headers = auth_header(assignee_token)

    client.post(
        "/tasks",
        json={"title": "Assigned To Me", "status": "pending", "priority": "medium", "assigned_to_id": assignee["id"]},
        headers=owner_headers,
    )

    # sem includeAssigned, assignee não vê a tarefa
    response_no_flag = client.get("/tasks/export/csv", headers=assignee_headers)
    assert "Assigned To Me" not in response_no_flag.text

    # com includeAssigned, assignee vê
    response_with_flag = client.get("/tasks/export/csv", params={"includeAssigned": True}, headers=assignee_headers)
    assert "Assigned To Me" in response_with_flag.text


def test_export_csv_does_not_include_deleted(client, user_factory, token_factory, auth_header):
    user_factory("Del User", "deluser@example.com")
    token = token_factory("deluser@example.com")
    headers = auth_header(token)

    create = client.post(
        "/tasks",
        json={"title": "To Be Deleted", "status": "pending", "priority": "low"},
        headers=headers,
    )
    task_id = create.json()["id"]
    client.delete(f"/tasks/{task_id}", headers=headers)

    response = client.get("/tasks/export/csv", headers=headers)
    assert "To Be Deleted" not in response.text


def test_export_pdf_returns_pdf(client, user_factory, token_factory, auth_header):
    user_factory("PDF User", "pdfuser@example.com")
    token = token_factory("pdfuser@example.com")
    headers = auth_header(token)

    client.post(
        "/tasks",
        json={"title": "PDF Task", "status": "in_progress", "priority": "medium"},
        headers=headers,
    )

    response = client.get("/tasks/export/pdf", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_export_pdf_empty(client, user_factory, token_factory, auth_header):
    user_factory("PDF Empty", "pdfempty@example.com")
    token = token_factory("pdfempty@example.com")
    headers = auth_header(token)

    response = client.get("/tasks/export/pdf", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_export_requires_auth(client):
    assert client.get("/tasks/export/csv").status_code == 401
    assert client.get("/tasks/export/pdf").status_code == 401