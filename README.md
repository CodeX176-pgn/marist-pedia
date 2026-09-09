# Marist Pedia

Marist Pedia is a FastAPI + Vanilla JavaScript quiz application that turns study material into interactive quizzes.

## Current roadmap status

- **A — Foundation:** complete
- **B — Document Pipeline:** complete
- **C — Quiz Engine:** complete
- **D — Quiz Backend:** complete
- **E — Quiz Frontend:** complete
- **F — LAN + Security:** complete
- **G — Quality:** complete
- **H — Database:** complete
- **I — Teacher/Admin:** complete

## Phase I — Teacher/Admin features

The teacher dashboard is available at `frontend/admin.html`.

It provides:

- Uploaded-document management and deletion.
- A complete list of generated quizzes, including drafts.
- Quiz review with the correct answers visible to teachers.
- Quiz title and description editing.
- Question text, choices, correct answer, explanation, and difficulty editing.
- Publish/unpublish controls.
- A protected admin API using the `X-Admin-Key` header.

Generated quizzes start as **drafts**. The student quiz library only lists published quizzes. Existing databases are upgraded automatically when the application starts; older quizzes are kept published during the upgrade so the change does not unexpectedly hide existing content.

## Setup

### 1. Install dependencies

```powershell
uv sync
```

### 2. Configure the teacher key

Copy `.env.example` to `.env` and choose a private admin key.

```powershell
Copy-Item .env.example .env
```

Set:

```text
MARIST_ADMIN_KEY=your-private-teacher-key
```

Do not commit `.env`.

### 3. Start the backend

```powershell
uv run uvicorn app.main:app --reload --app-dir backend
```

### 4. Serve the frontend

From the project root, for example:

```powershell
py -m http.server 5500 --directory frontend
```

Open:

- Student app: `http://localhost:5500`
- Teacher dashboard: `http://localhost:5500/admin.html`
- API docs: `http://localhost:8000/docs`

## Teacher workflow

1. Generate a quiz from study material.
2. Open `admin.html`.
3. Enter the configured teacher key.
4. Open **Review / edit** for a generated quiz.
5. Check every question and correct answer.
6. Edit anything that needs correction.
7. Tick **Published** when the quiz is ready.
8. Students will then see it in the normal quiz library.

## Testing

Run the complete automated test suite:

```powershell
uv run pytest
```

## Git checkpoint — Phase I

```powershell
git add .
git commit -m "feat(admin): add teacher quiz and document management"
git push
```
