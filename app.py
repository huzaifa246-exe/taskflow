from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

app = Flask(__name__, static_folder='frontend')
CORS(app)

# In-memory task store
tasks = {}

# ── Serve frontend ─────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/style.css')
def css():
    return send_from_directory('frontend', 'style.css')

# ── Health check ───────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": utcnow().isoformat()}), 200

# ── Endpoint 1: GET /api/tasks ─────────────────────────────
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({"tasks": list(tasks.values()), "count": len(tasks)}), 200

# ── Endpoint 2: POST /api/tasks ────────────────────────────
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "title is required"}), 400

    title = data['title'].strip()
    if not title:
        return jsonify({"error": "title cannot be empty"}), 400

    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "title": title,
        "description": data.get('description', ''),
        "priority": data.get('priority', 'medium'),
        "done": False,
        "created_at": utcnow().isoformat()
    }
    tasks[task_id] = task
    return jsonify(task), 201

# ── Endpoint 3: GET /api/tasks/<id> ───────────────────────
@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task), 200

# ── Endpoint 4: PUT /api/tasks/<id> ───────────────────────
@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "no data provided"}), 400

    if 'title' in data:
        task['title'] = data['title'].strip()
    if 'description' in data:
        task['description'] = data['description']
    if 'priority' in data:
        task['priority'] = data['priority']
    if 'done' in data:
        task['done'] = bool(data['done'])

    task['updated_at'] = utcnow().isoformat()
    tasks[task_id] = task
    return jsonify(task), 200

# ── Endpoint 5: DELETE /api/tasks/<id> ────────────────────
@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = tasks.pop(task_id, None)
    if not task:
        return jsonify({"error": "task not found"}), 404
    return jsonify({"message": "task deleted", "id": task_id}), 200

# ── Endpoint 6: POST /api/tasks/search ────────────────────
@app.route('/api/tasks/search', methods=['POST'])
def search_tasks():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "query is required"}), 400

    query = data['query'].lower()
    results = [
        t for t in tasks.values()
        if query in t['title'].lower() or query in t.get('description', '').lower()
    ]
    return jsonify({"results": results, "count": len(results)}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
