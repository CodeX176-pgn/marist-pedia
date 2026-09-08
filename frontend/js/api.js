const API_BASE_URL = (
    window.MARIST_PEDIA_API_URL || "http://localhost:8000"
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
            ? detail.map((item) => item.msg || "Invalid request").join("; ")
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
