# Command Line Cheat Sheet

This document contains all the essential PowerShell / Command Prompt commands to run, test, and interact with every part of the AI Task Assistant system on Windows.

---

## 1. Environment & Setup

**Activate Virtual Environment:**
```powershell
.\.venv\Scripts\activate
```

**Install Dependencies:**
```powershell
pip install -r requirements.txt
```

---

## 2. Running the Application

**Start the FastAPI Server (Development Mode with Auto-Reload):**
```powershell
uvicorn app.main:app --reload --port 8000
```
*Once running, view the interactive Swagger UI at: [http://localhost:8000/docs](http://localhost:8000/docs)*

---

## 3. Running Tests

**Run All Tests:**
```powershell
pytest -v tests/
```

**Run Only Integration Tests (FastAPI Routes / Database):**
```powershell
pytest -v tests/test_tasks.py
```

**Run Only Unit Tests (LLM Parsing Logic):**
```powershell
pytest -v tests/test_llm.py
```

**Run the Interactive LLM CLI Script:**
```powershell
python test_llm_interactive.py
```

---

## 4. Interacting with the API via Command Line (PowerShell)

You can test the running server directly from a PowerShell terminal using `Invoke-RestMethod`.

**Create a Task (POST):**
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/tasks' -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"input": "Buy groceries tomorrow high priority"}'
```

**Get All Tasks (GET):**
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/tasks' -Method Get
```

**Get a Single Task by ID (GET):**
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/tasks/1' -Method Get
```

**Update a Task (PUT):**
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/tasks/1' -Method Put -Headers @{"Content-Type"="application/json"} -Body '{"title": "Updated Groceries", "description": "Milk and Eggs", "priority": "medium", "due_date": null}'
```

**Delete a Task (DELETE):**
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/tasks/1' -Method Delete
```

---

## 5. Git & Version Control

**View Git Status:**
```powershell
git status
```

**Stage All Files & Commit:**
```powershell
git add .
git commit -m "Your commit message here"
```

**Push to GitHub:**
```powershell
git push origin master
```
