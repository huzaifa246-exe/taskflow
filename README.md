# TaskFlow

A task management REST API built with Python Flask, containerised with Docker, and deployed on AWS EC2.

**SE202L DevOps Lab Project**

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/taskflow.git
cd taskflow
docker build -t taskflow:v1 .
docker run -d -p 5000:5000 taskflow:v1
```

Open `http://localhost:5000` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/<id>` | Get one task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| POST | `/api/tasks/search` | Search tasks |

## Run Tests

```bash
pip install -r requirements.txt
python -m pytest test_app.py -v
```

## Tech Stack

- Python 3.11, Flask, flask-cors
- Docker
- GitHub Actions (CI/CD)
- AWS EC2 t2.micro (Ubuntu 22.04)
