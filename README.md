# Project Structure

```
MaristPedia
├── backend
│   └── app
│       ├── config
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── core
│       │   ├── __init__.py
│       │   └── errors.py
│       ├── models
│       │   ├── __init__.py
│       │   └── quiz.py
│       ├── routers
│       │   ├── __init__.py
│       │   ├── documents.py
│       │   ├── health.py
│       │   └── quizzes.py
│       ├── schemas
│       │   ├── __init__.py
│       │   ├── document.py
│       │   └── quiz.py
│       ├── services
│       │   ├── __init__.py
│       │   ├── ai_question_generator.py
│       │   ├── document_extraction_service.py
│       │   ├── document_service.py
│       │   ├── local_question_generator.py
│       │   ├── question_generator_factory.py
│       │   ├── quiz_generator.py
│       │   ├── quiz_service.py
│       │   ├── quiz_session_service.py
│       │   └── text_processing_service.py
│       ├── __init__.py
│       └── main.py
├── frontend
│   ├── css
│   │   ├── components.css
│   │   ├── global.css
│   │   ├── reset.css
│   │   ├── style.css
│   │   └── variables.css
│   ├── js
│   │   ├── api.js
│   │   ├── app.js
│   │   └── ui.js
│   └── index.html
├── src
│   └── marist_pedia
│       └── __init__.py
├── storage
│   └── uploads
│       └── .gitkeep
├── tests
│   ├── test_document_api_security.py
│   ├── test_document_extraction.py
│   ├── conftest.py
│   ├── test_document_api_integration.py
│   ├── test_document_security.py
│   ├── test_question_generator_architecture.py
│   ├── test_error_handling.py
│   ├── test_quiz_api.py
│   ├── test_quiz_api_integration.py
│   ├── test_quiz_service.py
│   ├── test_quiz_session.py
│   └── test_text_processsing.py
├── pyproject.toml
├── README.md
└── uv.lock
```


## Quality

Phase G adds automated integration coverage and centralized API error handling.
The API also assigns an `X-Request-ID` to each request and writes structured JSON logs to the server console.

Run the test suite with:

```powershell
uv run pytest
```

The tests isolate in-memory quiz/session state and remove only upload files created by each test.
