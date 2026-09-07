export function setLoading(element, message = "Loading...") {
    element.innerHTML = `
        <div class="empty-state">
            <p>${message}</p>
        </div>
    `;
}

export function showError(element, message) {
    element.innerHTML = `
        <div class="empty-state">
            <h3>Something went wrong</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

export function renderQuizCard(quiz) {
    const card = document.createElement("article");

    card.className = "quiz-card";

    card.innerHTML = `
        <h3>${escapeHtml(quiz.title)}</h3>
        <p>
            ${escapeHtml(
                quiz.description || "No description available."
            )}
        </p>
    `;

    return card;
}

export function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
