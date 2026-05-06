import pytest
import json
from app import app, tasks


@pytest.fixture(autouse=True)
def clear_tasks():
    """Clear the in-memory task store before every test."""
    tasks.clear()
    yield
    tasks.clear()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ── Test 1: Health check ──────────────────────────────────
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data


# ── Test 2: Get empty task list ───────────────────────────
def test_get_tasks_empty(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['tasks'] == []
    assert data['count'] == 0


# ── Test 3: Create a task (POST) ──────────────────────────
def test_create_task(client):
    payload = {"title": "Buy groceries", "priority": "high"}
    response = client.post(
        '/api/tasks',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Buy groceries'
    assert data['priority'] == 'high'
    assert data['done'] is False
    assert 'id' in data


# ── Test 4: Create task without title returns 400 ─────────
def test_create_task_missing_title(client):
    response = client.post(
        '/api/tasks',
        data=json.dumps({"description": "no title here"}),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


# ── Test 5: Get single task and 404 for missing ───────────
def test_get_single_task(client):
    create_resp = client.post(
        '/api/tasks',
        data=json.dumps({"title": "Read book"}),
        content_type='application/json'
    )
    task_id = json.loads(create_resp.data)['id']

    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert json.loads(response.data)['title'] == 'Read book'

    response = client.get('/api/tasks/nonexistent')
    assert response.status_code == 404


# ── Test 6: Search tasks (POST) ───────────────────────────
def test_search_tasks(client):
    client.post('/api/tasks', data=json.dumps({"title": "Walk the dog"}), content_type='application/json')
    client.post('/api/tasks', data=json.dumps({"title": "Buy milk"}), content_type='application/json')

    response = client.post(
        '/api/tasks/search',
        data=json.dumps({"query": "dog"}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1
    assert data['results'][0]['title'] == 'Walk the dog'


# ── Test 7: Update a task (PUT) ───────────────────────────
def test_update_task(client):
    create_resp = client.post(
        '/api/tasks',
        data=json.dumps({"title": "Old title"}),
        content_type='application/json'
    )
    task_id = json.loads(create_resp.data)['id']

    update_resp = client.put(
        f'/api/tasks/{task_id}',
        data=json.dumps({"title": "New title", "done": True}),
        content_type='application/json'
    )
    assert update_resp.status_code == 200
    data = json.loads(update_resp.data)
    assert data['title'] == 'New title'
    assert data['done'] is True


# ── Test 8: Delete a task ─────────────────────────────────
def test_delete_task(client):
    create_resp = client.post(
        '/api/tasks',
        data=json.dumps({"title": "Task to delete"}),
        content_type='application/json'
    )
    task_id = json.loads(create_resp.data)['id']

    del_resp = client.delete(f'/api/tasks/{task_id}')
    assert del_resp.status_code == 200

    get_resp = client.get(f'/api/tasks/{task_id}')
    assert get_resp.status_code == 404
