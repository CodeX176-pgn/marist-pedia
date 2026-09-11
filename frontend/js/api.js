const DEFAULT_API_PORT = 8000;

function getDefaultApiUrl() {
    const protocol = window.location.protocol;

    // When the HTML file is opened directly from disk,
    // use localhost for local development.
    if (protocol === "file:") {
        return `http://localhost:${DEFAULT_API_PORT}`;
    }

    // During development the frontend normally runs on port 5500,
    // while FastAPI runs on port 8000.
    if (window.location.port === "5500") {
        return `${protocol}//${window.location.hostname}:${DEFAULT_API_PORT}`;
    }

    // Production uses a reverse proxy, so the frontend and API
    // share the same origin.
    return window.location.origin;
}

const API_BASE_URL = (
    window.MARIST_PEDIA_API_URL || getDefaultApiUrl()
).replace(/\/$/, "");

async function request(endpoint, options = {}) {
    const config = {
        ...options,
        headers: {
            Accept: "application/json",
            ...(options.headers || {}),
        },
    };

    if (config.body && !(config.body instanceof FormData)) {
        config.headers["Content-Type"] = "application/json";
    }

    let response;

    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    } catch (error) {
        throw new Error(
            "Unable to connect to the Marist Pedia server. Make sure FastAPI is running."
        );
    }

    let data = null;
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        const detail = data?.detail;

        const message = Array.isArray(detail)
            ? detail
                .map((item) => item.msg || "Invalid request")
                .join("; ")
            : detail || `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    return data;
}

export function getHealth() {
    return request("/health");
}

export function getQuizzes() {
    return request("/api/quizzes");
}

export function getQuiz(quizId) {
    return request(`/api/quizzes/${encodeURIComponent(quizId)}`);
}

export function createQuizSession(quizId) {
    return request(`/api/quizzes/${encodeURIComponent(quizId)}/sessions`, {
        method: "POST",
        body: JSON.stringify({ quiz_id: quizId }),
    });
}

export function getQuizSession(sessionId) {
    return request(
        `/api/quizzes/sessions/${encodeURIComponent(sessionId)}`,
    );
}

export function submitAnswer(sessionId, questionId, selectedAnswer) {
    return request(
        `/api/quizzes/sessions/${encodeURIComponent(sessionId)}/answers`,
        {
            method: "POST",
            body: JSON.stringify({
                question_id: questionId,
                selected_answer: selectedAnswer,
            }),
        },
    );
}

export function submitQuizSession(sessionId) {
    return request(
        `/api/quizzes/sessions/${encodeURIComponent(sessionId)}/submit`,
        { method: "POST" },
    );
}

export function adminRequest(endpoint, adminKey, options = {}) {
    return request(endpoint, {
        ...options,
        headers: {
            ...(options.headers || {}),
            "X-Admin-Key": adminKey,
        },
    });
}

export function getAdminDocuments(adminKey) {
    return adminRequest("/api/admin/documents", adminKey);
}

export function deleteAdminDocument(adminKey, documentId) {
    return adminRequest(`/api/admin/documents/${encodeURIComponent(documentId)}`, adminKey, {
        method: "DELETE",
    });
}

export function getAdminQuizzes(adminKey) {
    return adminRequest("/api/admin/quizzes", adminKey);
}

export function getAdminQuiz(adminKey, quizId) {
    return adminRequest(`/api/admin/quizzes/${encodeURIComponent(quizId)}`, adminKey);
}

export function updateAdminQuiz(adminKey, quizId, payload) {
    return adminRequest(`/api/admin/quizzes/${encodeURIComponent(quizId)}`, adminKey, {
        method: "PUT",
        body: JSON.stringify(payload),
    });
}

export function updateAdminQuestion(adminKey, quizId, questionId, payload) {
    return adminRequest(
        `/api/admin/quizzes/${encodeURIComponent(quizId)}/questions/${encodeURIComponent(questionId)}`,
        adminKey,
        {
            method: "PUT",
            body: JSON.stringify(payload),
        },
    );
}
