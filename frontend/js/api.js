const API_BASE_URL = "http://localhost:8000";

async function request(endpoint, options = {}) {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json",
                ...options.headers,
            },
            ...options,
        }
    );

    let data = null;

    const contentType = response.headers.get("content-type");

    if (contentType?.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    return data;
}

export async function getHealth() {
    return request("/health");
}

export async function getQuizzes() {
    return request("/quizzes");
}
