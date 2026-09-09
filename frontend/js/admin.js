import {
    deleteAdminDocument,
    getAdminDocuments,
    getAdminQuiz,
    getAdminQuizzes,
    updateAdminQuestion,
    updateAdminQuiz,
} from "./api.js";

import { escapeHtml, setButtonLoading } from "./ui.js";

const loginPanel = document.querySelector("#login-panel");
const dashboard = document.querySelector("#dashboard");
const loginForm = document.querySelector("#login-form");
const adminKeyInput = document.querySelector("#admin-key");
const loginError = document.querySelector("#login-error");
const documentList = document.querySelector("#document-list");
const quizList = document.querySelector("#quiz-list");
const editor = document.querySelector("#editor");
const editorTitle = document.querySelector("#editor-title");
const quizForm = document.querySelector("#quiz-form");
const quizTitle = document.querySelector("#quiz-title");
const quizDescription = document.querySelector("#quiz-description");
const quizPublished = document.querySelector("#quiz-published");
const questionEditor = document.querySelector("#question-editor");
const dashboardMessage = document.querySelector("#dashboard-message");

let adminKey = sessionStorage.getItem("marist_pedia_admin_key") || "";
let currentQuiz = null;

function setMessage(message, isError = false) {
    dashboardMessage.textContent = message;
    dashboardMessage.style.color = isError ? "var(--color-error)" : "";
}

function showDashboard() {
    loginPanel.classList.add("hidden");
    dashboard.classList.remove("hidden");
    loadDashboard();
}

async function verifyKey(key) {
    // A harmless protected request verifies that the supplied key is valid.
    await getAdminQuizzes(key);
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginError.classList.add("hidden");

    const key = adminKeyInput.value.trim();
    if (!key) return;

    const button = loginForm.querySelector("button");
    setButtonLoading(button, true, "Checking...");

    try {
        await verifyKey(key);
        adminKey = key;
        sessionStorage.setItem("marist_pedia_admin_key", key);
        showDashboard();
    } catch (error) {
        loginError.textContent = error.message;
        loginError.classList.remove("hidden");
    } finally {
        setButtonLoading(button, false);
    }
});

async function loadDashboard() {
    await Promise.all([loadDocuments(), loadQuizzes()]);
}

async function loadDocuments() {
    documentList.textContent = "Loading documents...";
    try {
        const documents = await getAdminDocuments(adminKey);
        documentList.innerHTML = "";

        if (!documents.length) {
            documentList.innerHTML = '<p class="admin-muted">No documents have been uploaded.</p>';
            return;
        }

        documents.forEach((document) => {
            const row = document.createElement("article");
            row.className = "admin-row";
            row.innerHTML = `
                <div class="admin-row-main">
                    <p class="admin-row-title">${escapeHtml(document.original_filename)}</p>
                    <p class="admin-row-meta">${escapeHtml(document.extension)} · ${formatBytes(document.size)} · ${formatDate(document.uploaded_at)}</p>
                </div>
                <div class="admin-actions">
                    <button class="button button-secondary delete-document" type="button" data-id="${escapeHtml(document.id)}">Delete</button>
                </div>
            `;
            documentList.appendChild(row);
        });
    } catch (error) {
        documentList.innerHTML = `<p class="admin-error">${escapeHtml(error.message)}</p>`;
    }
}

async function loadQuizzes() {
    quizList.textContent = "Loading quizzes...";
    try {
        const quizzes = await getAdminQuizzes(adminKey);
        quizList.innerHTML = "";

        if (!quizzes.length) {
            quizList.innerHTML = '<p class="admin-muted">No quizzes have been generated.</p>';
            return;
        }

        quizzes.forEach((quiz) => {
            const row = document.createElement("article");
            row.className = "admin-row";
            row.innerHTML = `
                <div class="admin-row-main">
                    <p class="admin-row-title">
                        <span class="status-badge ${quiz.is_published ? "status-published" : "status-draft"}">${quiz.is_published ? "Published" : "Draft"}</span>
                        ${escapeHtml(quiz.title)}
                    </p>
                    <p class="admin-row-meta">${quiz.question_count} question${quiz.question_count === 1 ? "" : "s"} · Updated ${formatDate(quiz.updated_at)}</p>
                </div>
                <div class="admin-actions">
                    <button class="button button-primary edit-quiz" type="button" data-id="${escapeHtml(quiz.id)}">Review / edit</button>
                </div>
            `;
            quizList.appendChild(row);
        });
    } catch (error) {
        quizList.innerHTML = `<p class="admin-error">${escapeHtml(error.message)}</p>`;
    }
}

async function openQuizEditor(quizId) {
    setMessage("Loading quiz...");
    try {
        currentQuiz = await getAdminQuiz(adminKey, quizId);
        editorTitle.textContent = `Review: ${currentQuiz.title}`;
        quizTitle.value = currentQuiz.title;
        quizDescription.value = currentQuiz.description || "";
        quizPublished.checked = currentQuiz.is_published;
        renderQuestions();
        editor.classList.remove("hidden");
        editor.scrollIntoView({ behavior: "smooth", block: "start" });
        setMessage("");
    } catch (error) {
        setMessage(error.message, true);
    }
}

function renderQuestions() {
    questionEditor.innerHTML = "";

    currentQuiz.questions.forEach((question, index) => {
        const card = document.createElement("article");
        card.className = "question-card";
        card.dataset.questionId = question.id;
        card.innerHTML = `
            <h3>Question ${index + 1}</h3>
            <label>Question text<textarea class="question-text" rows="4" maxlength="5000">${escapeHtml(question.text)}</textarea></label>
            <div class="choices"></div>
            <label>Correct answer ID<input class="correct-answer" value="${escapeHtml(question.correct_answer)}" maxlength="20"></label>
            <label>Explanation<textarea class="explanation" rows="3" maxlength="5000">${escapeHtml(question.explanation || "")}</textarea></label>
            <label>Difficulty<select class="difficulty"><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select></label>
            <button class="button button-primary question-save" type="button">Save question</button>
        `;

        const choices = card.querySelector(".choices");
        question.choices.forEach((choice) => {
            const row = document.createElement("div");
            row.className = "choice-row";
            row.innerHTML = `
                <strong>${escapeHtml(choice.id)}</strong>
                <input class="choice-text" data-choice-id="${escapeHtml(choice.id)}" value="${escapeHtml(choice.text)}" maxlength="2000">
            `;
            choices.appendChild(row);
        });

        card.querySelector(".difficulty").value = question.difficulty;
        questionEditor.appendChild(card);
    });
}

quizForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!currentQuiz) return;

    const button = quizForm.querySelector("button");
    setButtonLoading(button, true, "Saving...");
    try {
        currentQuiz = await updateAdminQuiz(adminKey, currentQuiz.id, {
            title: quizTitle.value.trim(),
            description: quizDescription.value.trim() || null,
            is_published: quizPublished.checked,
        });
        editorTitle.textContent = `Review: ${currentQuiz.title}`;
        setMessage("Quiz settings saved.");
        await loadQuizzes();
    } catch (error) {
        setMessage(error.message, true);
    } finally {
        setButtonLoading(button, false);
    }
});

document.addEventListener("click", async (event) => {
    const editButton = event.target.closest(".edit-quiz");
    if (editButton) {
        await openQuizEditor(editButton.dataset.id);
        return;
    }

    const deleteButton = event.target.closest(".delete-document");
    if (deleteButton) {
        const shouldDelete = window.confirm("Delete this uploaded document? This cannot be undone.");
        if (!shouldDelete) return;

        setButtonLoading(deleteButton, true, "Deleting...");
        try {
            await deleteAdminDocument(adminKey, deleteButton.dataset.id);
            await loadDocuments();
            setMessage("Document deleted.");
        } catch (error) {
            setMessage(error.message, true);
            setButtonLoading(deleteButton, false);
        }
        return;
    }

    const saveButton = event.target.closest(".question-save");
    if (saveButton) {
        const card = saveButton.closest(".question-card");
        const choices = [...card.querySelectorAll(".choice-text")].map((input) => ({
            id: input.dataset.choiceId,
            text: input.value.trim(),
        }));

        setButtonLoading(saveButton, true, "Saving...");
        try {
            const updatedQuiz = await updateAdminQuestion(
                adminKey,
                currentQuiz.id,
                card.dataset.questionId,
                {
                    text: card.querySelector(".question-text").value.trim(),
                    choices,
                    correct_answer: card.querySelector(".correct-answer").value.trim(),
                    explanation: card.querySelector(".explanation").value.trim() || null,
                    difficulty: card.querySelector(".difficulty").value,
                },
            );
            currentQuiz = await getAdminQuiz(adminKey, updatedQuiz.id);
            renderQuestions();
            setMessage("Question saved.");
        } catch (error) {
            setMessage(error.message, true);
        } finally {
            setButtonLoading(saveButton, false);
        }
    }
});

document.querySelector("#refresh-documents").addEventListener("click", loadDocuments);
document.querySelector("#refresh-quizzes").addEventListener("click", loadQuizzes);
document.querySelector("#close-editor").addEventListener("click", () => editor.classList.add("hidden"));
document.querySelector("#logout-button").addEventListener("click", () => {
    sessionStorage.removeItem("marist_pedia_admin_key");
    adminKey = "";
    currentQuiz = null;
    dashboard.classList.add("hidden");
    loginPanel.classList.remove("hidden");
    adminKeyInput.value = "";
    editor.classList.add("hidden");
});

function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}

function formatDate(value) {
    return new Date(value).toLocaleString();
}

if (adminKey) {
    verifyKey(adminKey).then(showDashboard).catch(() => {
        sessionStorage.removeItem("marist_pedia_admin_key");
        adminKey = "";
    });
}
