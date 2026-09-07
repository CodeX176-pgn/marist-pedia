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
│       │   ├── document_extraction_service.py
│       │   ├── document_service.py
│       │   ├── quiz_service.py
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
│   ├── test_document_extraction.py
│   └── test_text_processsing.py
├── pyproject.toml
├── README.md
└── uv.lock
```
