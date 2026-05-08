# 1. Install Everything Globally

Run once:

```powershell
pip install fastapi uvicorn pytest httpx python-multipart
```

Why these?

* `fastapi` → framework
* `uvicorn` → ASGI server
* `pytest` → test runner
* `httpx` → required by FastAPI TestClient
* `python-multipart` → commonly needed by FastAPI forms/uploads

---

# 2. Verify Global Packages

```powershell
pip list
```

You should see:

```txt
fastapi
pytest
httpx
uvicorn
```

---

# 3. Create FastAPI App

## main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/greet")
def greet(name: str = "Guest"):
    return {"message": f"Welcome, {name}!"}
```

---

# 4. Create Tests

## test_main.py

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_greet_with_name():
    response = client.get("/greet?name=Alice")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome, Alice!"
    }

def test_greet_default():
    response = client.get("/greet")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome, Guest!"
    }
```

---

# 5. Run Tests

```powershell
pytest
```

or:

```powershell
python -m pytest
```

---

# Final Successful Output

```txt
=========================================================== test session starts ===========================================================
platform win32 -- Python 3.14.2, pytest-9.0.3, pluggy-1.6.0
rootdir: scripts\test\fastapi
plugins: anyio-4.12.1
collected 2 items                                                                                                                          

test_main.py ..                                                                                                                      [100%]

============================================================ 2 passed in 0.85s ============================================================
```

---

# Minimal Judge0 `run` Script

## run

```bash
#!/usr/bin/env bash
set -e

python3 -m pytest
```

---