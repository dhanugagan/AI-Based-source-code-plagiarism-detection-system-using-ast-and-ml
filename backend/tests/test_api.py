"""Integration tests for the core API flows using an isolated SQLite DB."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mktemp(suffix='.db')}"
os.environ["MODEL_PATH"] = tempfile.mktemp(suffix=".joblib")
os.environ["UPLOAD_DIRECTORY"] = tempfile.mkdtemp()
os.environ["REPORT_DIRECTORY"] = tempfile.mkdtemp()

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

CODE_A = b"a = 10\nb = 20\nc = a + b\nprint(c)\n"
CODE_B = b"x = 10\ny = 20\ntotal = x + y\nprint(total)\n"


def _register_and_login(email="student@example.com"):
    client.post(
        "/api/auth/register",
        json={
            "name": "Test Student",
            "email": email,
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": email, "password": "password123"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200


def test_register_login_and_upload_and_compare():
    headers = _register_and_login()

    up_a = client.post(
        "/api/submissions/upload",
        files={"file": ("a.py", CODE_A, "text/x-python")},
        headers=headers,
    )
    up_b = client.post(
        "/api/submissions/upload",
        files={"file": ("b.py", CODE_B, "text/x-python")},
        headers=headers,
    )
    assert up_a.status_code == 201
    assert up_b.status_code == 201

    sub_a_id = up_a.json()["id"]
    sub_b_id = up_b.json()["id"]

    analyze = client.post(
        "/api/comparisons/analyze",
        json={"submission1_id": sub_a_id, "submission2_id": sub_b_id},
        headers=headers,
    )
    assert analyze.status_code == 201
    body = analyze.json()
    assert body["final_score"] > 50  # renamed-variable pair should score highly
    assert body["risk_level"] in ("Low", "Medium", "High", "Very High")


def test_upload_rejects_bad_extension():
    headers = _register_and_login(email="student2@example.com")
    resp = client.post(
        "/api/submissions/upload",
        files={"file": ("a.exe", b"binary", "application/octet-stream")},
        headers=headers,
    )
    assert resp.status_code == 400


def test_batch_comparison_matrix():
    headers = _register_and_login(email="student3@example.com")

    files = {
        "s1.py": b"a = 10\nb = 20\nc = a + b\nprint(c)\n",
        "s2.py": b"x = 10\ny = 20\ntotal = x + y\nprint(total)\n",  # renamed variant of s1
        "s3.py": b"def greet(name):\n    print('Hello ' + name)\n\ngreet('World')\n",
    }
    ids = []
    for name, content in files.items():
        res = client.post(
            "/api/submissions/upload",
            files={"file": (name, content, "text/x-python")},
            headers=headers,
        )
        assert res.status_code == 201
        ids.append(res.json()["id"])

    batch_resp = client.post(
        "/api/comparisons/batch",
        json={"submission_ids": ids},
        headers=headers,
    )
    assert batch_resp.status_code == 200
    body = batch_resp.json()
    assert len(body["matrix"]) == 3
    assert len(body["pairs"]) == 3  # 3 choose 2
    # s1 vs s2 (renamed variant) should score very high
    s1_s2 = body["matrix"][0][1]
    assert s1_s2 > 80
